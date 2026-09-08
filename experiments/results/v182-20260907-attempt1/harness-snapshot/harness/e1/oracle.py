"""E1 oracle: the release computation of the paper, Section 4, and nothing
else. Every function cites the Definition/Eq it transcribes (numbering of
ccme-conference-paper-v8). Deliberately reproduces the paper's model
verbatim, including its known incompletenesses relative to the
implementation; the comparator classifies those (PG1..PG3 in run.py).

Instance JSON schema (consumed here and realized by shared/realize.py):
  packages: [name]
  edges:    [[dependent, dependency]]          # (a,b): a depends on b
  commits:  [{id, units: [unit]}]              # index order = history, 0 oldest
  tags:     [{pkg, version, commit}]
  unit: {type, scope: [pkg], breaking: bool,
         pb: "patch"|"minor"|"major"|null,     # null = not written (default)
         pd: 0|N|-1,                           # -1 = all
         channel: name|null,                   # direct % value
         pchannel: name|null,                  # %% value (explicit only, v1)
         pcd: 0|N|-1,
         releaseAs: "none"|null}
History is linear in v1: reach(commits[i]) = commits[0..i].
"""
import json
import sys

BUMPS = {"none": 0, "patch": 1, "minor": 2, "major": 3}
BUMPN = {v: k for k, v in BUMPS.items()}
TYPEMAP = {"feat": "minor", "fix": "patch", "perf": "patch",
           "docs": "none", "chore": "none", "release": "none",
           "cancel": "none"}
ALL = -1


# ---- versions (Def "bumps, versions, channels") -------------------------

def vparse(s):
    """SemVer subset used by the instances: X.Y.Z[-ch.N]."""
    core, _, pre = s.partition("-")
    x, y, z = (int(p) for p in core.split("."))
    if pre:
        ch, _, n = pre.partition(".")
        return (x, y, z, ch, int(n))
    return (x, y, z, None, None)

def vfmt(v):
    x, y, z, ch, n = v
    return f"{x}.{y}.{z}" + (f"-{ch}.{n}" if ch else "")

def vcmp(a, b):
    """SemVer precedence: core numerically; a prerelease sorts below its
    core; identifiers (channel asciibetical, counter numeric)."""
    if a[:3] != b[:3]:
        return -1 if a[:3] < b[:3] else 1
    apre, bpre = a[3] is not None, b[3] is not None
    if apre != bpre:
        return -1 if apre else 1          # prerelease < release
    if not apre:
        return 0
    if a[3] != b[3]:
        return -1 if a[3] < b[3] else 1
    return (a[4] > b[4]) - (a[4] < b[4])

def ch_of(v):
    """ch(v): stable for non-prerelease, else the first identifier."""
    return v[3] or "stable"

def core_of(v):
    return v[:3] + (None, None)

def cnt_of(v):
    return v[4]

def apply_bump(v, b):
    """apply(v,b) on a stable version."""
    x, y, z = v[:3]
    if b == "major":
        return (x + 1, 0, 0, None, None)
    if b == "minor":
        return (x, y + 1, 0, None, None)
    if b == "patch":
        return (x, y, z + 1, None, None)
    return v                               # none

def bjoin(a, b):
    """Bump join = max over none<patch<minor<major."""
    return BUMPN[max(BUMPS[a], BUMPS[b])]


class Oracle:
    def __init__(self, inst):
        self.P = list(inst["packages"])
        self.dep = {p: [] for p in self.P}          # dep(p): dependents of p
        for a, b in inst["edges"]:                  # a depends on b
            self.dep[b].append(a)
        self.commits = inst["commits"]
        self.idx = {c["id"]: i for i, c in enumerate(self.commits)}
        self.tags = inst["tags"]

    # ---- Def "state": base, sbase, scom ---------------------------------
    def base(self, p):
        """base_sigma(p): highest-precedence tag; None if untagged."""
        best = None
        for t in self.tags:
            if t["pkg"] != p:
                continue
            v = vparse(t["version"])
            if best is None or vcmp(v, best[0]) > 0:
                best = (v, t["commit"])
        return best                                  # (version, commit) | None

    def sbase(self, p):
        """sbase/scom: highest-precedence non-prerelease tag."""
        best = None
        for t in self.tags:
            if t["pkg"] != p:
                continue
            v = vparse(t["version"])
            if v[3] is not None:
                continue
            if best is None or vcmp(v, best[0]) > 0:
                best = (v, t["commit"])
        return best

    def base_channel(self, p):
        """ch(base_sigma(p)); stable by convention when untagged."""
        b = self.base(p)
        return ch_of(b[0]) if b else "stable"

    # ---- Def "pending window", Eq (1) -----------------------------------
    def window(self, p):
        """W(p) as a set of commit ids. Linear history: reach(c)=0..idx."""
        sb = self.sbase(p)
        if sb is None:
            return {c["id"] for c in self.commits}
        cut = self.idx[sb[1]]
        return {c["id"] for c in self.commits[cut + 1:]}

    # ---- units, iterated newest commit first, last unit first -----------
    def units(self):
        out = []
        for ci in range(len(self.commits) - 1, -1, -1):
            c = self.commits[ci]
            for ui in range(len(c["units"]) - 1, -1, -1):
                out.append((c["id"], c["units"][ui]))
        return out                                   # precedence order

    @staticmethod
    def bump_of(u):
        """bump(u): the type map and `!` alone."""
        return "major" if u.get("breaking") else TYPEMAP[u["type"]]

    @staticmethod
    def pb_of(u):
        """pb(u): the stated value, default patch once propagation asked."""
        return u.get("pb") or "patch"

    # ---- Def "suppression and sources", Eq (2) --------------------------
    def cancelled(self, cid, p):
        """canc(c,p): c ancestor-or-self of a cancel commit scoping p."""
        ci = self.idx[cid]
        for c in self.commits[ci:]:                  # ancestors-or-self of later cancels
            for u in c["units"]:
                if u["type"] == "cancel" and p in u["scope"]:
                    return True
        return False

    def held(self, p):
        """held(p): effective Release-As is none (newest wins; v1 has
        only the value none, so any applicable directive in W(p) holds)."""
        w = self.window(p)
        for cid, u in self.units():
            if u.get("releaseAs") == "none" and p in u["scope"] and cid in w:
                return True
        return False

    def src(self, u, cid):
        """src(u), Eq (2): scope minus suppressed, discharge first."""
        out = set()
        for p in u["scope"]:
            if p not in self.P:
                continue
            disch = cid not in self.window(p)
            if disch or not (self.cancelled(cid, p) or self.held(p)):
                out.add(p)
        return out

    # ---- Def "reach": R(S, l), shortest-path, S excluded ----------------
    def reach(self, S, depth):
        seen = set(S)
        frontier = set(S)
        out = {}
        level = 0
        while frontier and (depth == ALL or level < depth):
            level += 1
            nxt = set()
            for p in frontier:
                for d in self.dep[p]:
                    if d not in seen:
                        seen.add(d)
                        nxt.add(d)
                        out[d] = level
            frontier = nxt
        return out

    # ---- Def "channels": chan(P) for every package ----------------------
    def proposal(self, value, cur, transition=False, propagated=False):
        """A proposal against cur = ch(base); empty when it proposes cur;
        a propagated non-transition stable never graduates a prerelease."""
        if propagated and not transition and value == "stable" \
                and cur != "stable":
            return None
        if value == cur:
            return None
        return value

    def channels(self):
        chan = {}
        for p in self.P:
            cur = self.base_channel(p)
            w = self.window(p)
            got = None
            # clause 1: newest direct Channel directive naming P in W(P)
            for cid, u in self.units():
                if u.get("channel") and p in u["scope"] and cid in w \
                        and not self.cancelled(cid, p):
                    v = self.proposal(u["channel"], cur)
                    if v is not None:
                        got = v
                        break
            # clause 2: newest channel-axis unit reaching P
            if got is None:
                for cid, u in self.units():
                    if u.get("pcd", 0) == 0 or not u.get("pchannel"):
                        continue
                    s = self.src(u, cid)
                    if not s:
                        continue
                    if p not in self.reach(s, u["pcd"]):
                        continue
                    if cid not in w or self.cancelled(cid, p):
                        continue
                    v = self.proposal(u["pchannel"], cur, propagated=True)
                    if v is not None:
                        got = v
                        break
            chan[p] = got if got is not None else cur
        return chan

    # ---- Eq (3) resolvable, Eq (4) admission, Eq (5) effective ----------
    def plan(self):
        chan = self.channels()
        eff = {p: "none" for p in self.P}
        due = {p: set() for p in self.P}
        for cid, u in self.units():
            if u["type"] == "cancel":
                continue
            s = self.src(u, cid)
            # direct: join bump(u) over P in src ∩ scope with c in W(P)
            b = self.bump_of(u)
            if b != "none":
                for p in s & set(u["scope"]):
                    if cid in self.window(p):
                        eff[p] = bjoin(eff[p], b)
            # propagated: Eq (4) clauses; Eq (5) join of pb(u)
            if u.get("pd", 0) == 0 or not s:
                continue
            srcch = {chan[p] for p in s}
            for d in self.reach(s, u["pd"]):
                if cid not in self.window(d):          # consumer's window
                    continue
                if self.cancelled(cid, d):
                    continue
                if "stable" not in srcch and chan[d] not in srcch:
                    continue                            # Eq (3)
                eff[d] = bjoin(eff[d], self.pb_of(u))
                due[d].add(cid)

        out = {}
        for p in self.P:
            base = self.base(p)
            basech = ch_of(base[0]) if base else "stable"
            in_plan = (not self.held(p)) and \
                (eff[p] != "none" or chan[p] != basech)
            if not in_plan:
                out[p] = {"changed": False,
                          "next": vfmt(base[0]) if base else "",
                          "bump": "none", "channel": chan[p]}
                continue
            # ---- Def "plan and versions", Eq (6)/(7) --------------------
            sb = self.sbase(p)
            S = sb[0] if sb else (0, 0, 0, None, None)   # untagged: v1 avoids
            if chan[p] == "stable":
                nxt = apply_bump(S, eff[p])
            else:
                t = apply_bump(S, eff[p])
                B = base[0] if base else None
                if B is not None and core_of(B) == t and ch_of(B) == chan[p]:
                    nxt = t[:3] + (chan[p], cnt_of(B) + 1)
                else:
                    nxt = t[:3] + (chan[p], 0)
            guard = base is not None and vcmp(nxt, base[0]) <= 0
            out[p] = {"changed": not guard, "next": vfmt(nxt),
                      "bump": eff[p], "channel": chan[p],
                      "guard": guard}
        return out


if __name__ == "__main__":
    inst = json.load(open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin)
    print(json.dumps(Oracle(inst).plan(), indent=1, sort_keys=True))
