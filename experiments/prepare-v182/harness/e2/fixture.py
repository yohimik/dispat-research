"""Build the six-package fixture in four flavours: lerna, nx, turbo
(turborepo orchestration + changesets version/publish, per Turborepo's
own docs) and dispat. All get the paper graph: cli,ui,api -> core;
theme,docs -> ui. Tool versions are baked into dispat-exp:node
(lerna 10.0.1, nx 23.1.2, turbo 2.10.12, @changesets/cli 3.0.1)."""
import json
import os
import subprocess
import sys

PKGS = ["core", "cli", "ui", "api", "theme", "docs"]
DEPS = {"cli": ["core"], "ui": ["core"], "api": ["core"],
        "theme": ["ui"], "docs": ["ui"]}
REG = "http://failproxy:4873"
TOK = os.environ.get("NPM_TOKEN", "anonymous")


def sh(args, cwd):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args}: {r.stdout[-300:]} {r.stderr[-300:]}")
    return r.stdout


def base(root, flavor):
    os.makedirs(root, exist_ok=True)
    sh(["git", "init", "-q", "."], root)
    open(os.path.join(root, ".gitignore"), "w").write("node_modules\n")
    for p in PKGS:
        d = os.path.join(root, "packages", p)
        os.makedirs(d, exist_ok=True)
        pj = {"name": p, "version": "1.0.0",
              "dependencies": {q: "^1.0.0" for q in DEPS.get(p, [])}}
        if flavor == "turbo":
            pj["scripts"] = {"build": "node -e 0"}
        json.dump(pj, open(os.path.join(d, "package.json"), "w"), indent=1)
        open(os.path.join(d, "index.js"), "w").write("// v1\n")
        if flavor in ("dispat", "nx", "turbo"):
            open(os.path.join(d, ".npmrc"), "w").write(
                f"registry={REG}\n//failproxy:4873/:_authToken={TOK}\n")
    with open(os.path.join(root, ".npmrc"), "w") as f:
        f.write(f"registry={REG}\n//failproxy:4873/:_authToken={TOK}\n")

    if flavor == "nx":
        json.dump({"name": "fixture", "private": True,
                   "workspaces": ["packages/*"]},
                  open(os.path.join(root, "package.json"), "w"), indent=1)
        json.dump({"release": {
                       "projects": ["*"],
                       "projectsRelationship": "independent",
                       "version": {"conventionalCommits": True},
                       "changelog": {"workspaceChangelog": False,
                                     "projectChangelogs": False}},
                   "defaultBase": "main"},
                  open(os.path.join(root, "nx.json"), "w"), indent=1)
    elif flavor == "turbo":
        json.dump({"name": "fixture", "private": True,
                   "workspaces": ["packages/*"],
                   "packageManager": "npm@10.9.2"},
                  open(os.path.join(root, "package.json"), "w"), indent=1)
        json.dump({"tasks": {"build": {"dependsOn": ["^build"]}}},
                  open(os.path.join(root, "turbo.json"), "w"), indent=1)
        # manypkg (changesets' discovery) only recognises an npm
        # workspace when a package-lock.json exists at the root.
        open(os.path.join(root, "package-lock.json"), "w").write("{}\n")
        cs = os.path.join(root, ".changeset")
        os.makedirs(cs, exist_ok=True)
        json.dump({"changelog": False, "commit": False,
                   "fixed": [], "linked": [], "ignore": [],
                   "access": "public", "baseBranch": "main",
                   "updateInternalDependencies": "patch"},
                  open(os.path.join(cs, "config.json"), "w"), indent=1)
    elif flavor == "lerna":
        json.dump({"name": "fixture", "private": True,
                   "workspaces": ["packages/*"]},
                  open(os.path.join(root, "package.json"), "w"), indent=1)
        json.dump({"version": "independent",
                   "command": {"version": {"conventionalCommits": True,
                                           "push": False},
                               "publish": {"registry": REG}}},
                  open(os.path.join(root, "lerna.json"), "w"), indent=1)
    else:
        open(os.path.join(root, "dispat.yaml"), "w").write(f"""\
spaces:
  packages:
    path: packages
    scripts:
      publish: npm publish --ignore-scripts --registry {REG} > /tmp/pub-$DISPAT_PACKAGE.log 2>&1
    flow:
      publish: publish
packages:
""" + "".join(f"  {p}:\n    dependencies: [{', '.join(d)}]\n"
              for p, d in DEPS.items()) + """\
autoVersion:
  enabled: true
changelog:
  enabled: false
github:
  enabled: false
""")
    sh(["git", "add", "-A"], root)
    sh(["git", "commit", "-qm", "chore: baseline"], root)
    for p in PKGS:
        sh(["git", "tag", f"{p}@1.0.0"], root)
    origin = root + "-origin.git"
    subprocess.run(["git", "init", "-q", "--bare", origin])
    sh(["git", "remote", "add", "origin", origin], root)
    sh(["git", "push", "-q", "origin", "main", "--tags"], root)


def feature(root, flavor):
    p = os.path.join(root, "packages", "core", "index.js")
    open(p, "a").write("// streaming\n")
    if flavor == "turbo":
        # changesets ignores commit messages; the bump intent is a
        # committed changeset file. major so the ^1.0.0 ranges fall out
        # of range and dependents get the default out-of-range patch.
        open(os.path.join(root, ".changeset", "streaming-reader.md"),
             "w").write('---\n"core": major\n---\n\nstreaming reader\n')
    sh(["git", "add", "-A"], root)
    msg = {"lerna": "feat(core): streaming reader",
           "nx": "feat(core): streaming reader",
           "turbo": "feat: streaming reader"}.get(
        flavor, "feat(core)^: streaming reader")
    sh(["git", "commit", "-qm", msg], root)


if __name__ == "__main__":
    root, flavor = sys.argv[1], sys.argv[2]
    base(root, flavor)
    feature(root, flavor)
    print("fixture ready:", root, flavor)
