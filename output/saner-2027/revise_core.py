from pathlib import Path
p=Path('paper/saner/model.tex');s=p.read_text()
s=s.replace('\\section{The Model}','\\section{Formal Model}')
s=s.replace('Section~\\ref{sec:guarantees} proves the guarantees over these\ndefinitions and nothing else.','Section~\\ref{sec:guarantees} proves guarantees over these definitions.\nThe model separates stage availability from cross-run admission and discharge.')
stage=r'''
\subsection{Stage Availability}
For a selected package $p$, let $B_p$ and $P_p$ denote successful completion
of its build and publish stage, respectively. A version task, when present,
is a prefix of $B_p$. For a provider $q$ and consumer $p$, the normal
successful-stage dependencies include $B_q\to B_p$, $B_p\to P_p$, and
$P_q\to P_p$. If $q$ requires published-artifact availability, add
$P_q\to B_p$. Here stage arrows mean prerequisite-to-successor; the package
edge convention below is consumer-to-provider. The construction is over the
full package graph, with stages outside the selected work treated as already
satisfied only when their required artifacts are available.

\begin{proposition}[stage-order safety]
\label{prop:stages}
For a finite acyclic package graph, the constructed stage graph is acyclic.
Any schedule that starts a stage only after all its prerequisites succeed
respects both local-build and published-artifact availability.
\end{proposition}
\begin{proof}
Take a provider-first topological rank of packages. Every cross-package stage
edge increases that rank. Within a package, the only direction is build to
publish. A directed cycle would therefore require a rank decrease or a
publish-to-build edge within one package, neither of which exists. Each
availability requirement is an explicit prerequisite, so a legal schedule
cannot cross it early. The claim concerns ordering, not whether a command
actually produces the promised artifact; that is an integration contract.
\end{proof}

A global build phase followed by a global publish phase violates the
$P_{\mathrm{base}}\to B_{\mathrm{app}}$ edge in Fig.~\ref{fig:stages}.
Conversely, no edge requires $P_{\mathrm{assets}}$ to precede
$B_{\mathrm{base}}$, so those stages may overlap. This elementary construction
uses standard topological scheduling~\cite{kahn,mokhov}; the recovery results
below address the separate problem of retaining the correct selected work.
'''
s=s.replace('\\subsection{Workspace, State, Windows}',stage+'\n\\subsection{Workspace, State, Windows}')
s=s.replace('$h$ is fixed throughout. This reading of a',r'''$h$ is fixed throughout. Normalization supplies a deterministic total order
of the commits consistent with ancestry; ``newest'' refers to this order,
with unit position breaking ties within a commit. Ancestry alone is only a
partial order, so this ordering policy is a fixed planning input. This reading of a''')
s=s.replace('contents at all, only history, tags and messages, which is what\nmakes the plan a pure function of the repository.','contents, only history, tags and normalized intent. Manifests and path-derived\nscopes are supplied through the normalized instance rather than modeled as files.')
s=s.replace('The graph is acyclic (a cycle is a repository-scoped error: no\npublish order exists for it, so whichever member went first would\ndeclare a range on a version that does not exist).','The graph is acyclic; cyclic workspaces are outside this protocol\nand are rejected before scheduling.')
s=s.replace('Tags are never moved or deleted, so\nstates only grow: a tag is the record that a leg of the transaction\ncompleted, and a rewritten record is what makes a saga unrecoverable.','Equal-precedence tags with conflicting release identities are rejected.\nAn untagged package has a virtual stable baseline of 0.0.0 and a configured\ninitial version; applying its first nonzero bump returns that initial version.\nWithin a valid run sequence, tags are never moved or deleted, so states only\ngrow. Rewriting a completion record is outside the guarantees.')
s=s.replace("history, which is also why adoption on an existing repository needs no\nmigration step.","history. An existing project must therefore configure its initial baseline\nand scope mapping deliberately.")
s=s.replace('the honest signal for a dependent whose\nown API did not change','a dependency update need not\nchange the consumer\'s own API')
s=s.replace('(an installer selects a prerelease only on its own line, so a bump\nacross a channel boundary is not a real obligation),','(the modeled policy admits a prerelease source only on a matching\nconsumer channel; this is an explicit release policy, not a universal\nclaim about package installers),')
s=s.replace('propagation can\nonly raise a version','joining an admitted bump cannot lower the effective bump')
s=s.replace('CCME~2.0',r'\lang{}~2.0')
s=s.replace('dispat',r'\tool{}')
s=s.replace('The definitions above are parametric, and a theorem about the model\nis worth nothing to an operator unless it is a theorem about\n\\emph{their} repository. A concrete repository at a commit determines\none \\emph{instance}','A concrete repository at a commit determines a normalized \\emph{instance}')
s=s.replace('The latter is a property of the run sequence, checked again before\neach retry, rather than a static property of one instance.','The latter is a property of the run sequence, rather than a static property\nof one instance. Maintaining it is a premise of the claim; the implementation\nis not assumed to automatically check every semantic component of that premise.')
p.write_text(s)
p=Path('paper/saner/guarantees.tex');s=p.read_text().replace('\\section{Guarantees, with Proofs}','\\section{Guarantees and Proof Arguments}')
s=s.replace('A run that publishes nothing has not failed \\emph{partially}\nand is surfaced as a hard error, not retried.','The bound assumes progress on every counted nonempty run; it does not bound\nthe number of failed attempts that make no progress.')
a=s.index('Three corollaries carry the operational weight.');b=s.index('\\begin{table*}',a)
s=s[:a]+r'''Three consequences explain the operational behavior. \emph{Resumption}:
after a partial failure, $\Pi(\sigma_2)=F\cup B$ at the original versions
(\G{2}--\G{5}), provided the retry invariant holds. \emph{Idempotence}:
let $\mathit{release}(s)=\mathit{run}(s,\emptyset)$ denote a fully successful
transformation with fixed reviewed inputs and valid records. Then
\[
  \mathit{release}(s)=\mathit{release}(\mathit{release}(s)),
\]
because the first transformation discharges every admitted obligation and the
second has an empty plan (\G{4}). Determinism of an unchanged preview is a
separate property (Theorem~\ref{thm:det}). \emph{Scope preservation}: \G{5}
makes the original plan an upper bound on retry publication under the same
invariant. This is not an authorization guarantee against changed commands,
rewritten tags, or changed credentials.

The idempotence equation concerns recorded release state. If a publisher
succeeds but its completion record is lost, its outcome must be reconciled,
or the publisher must safely accept repetition. Arbitrary shell-side effects
are not made exactly-once by a tag ledger.

'''+s[b:]
a=s.index('\\begin{table*}');s=s[:a]+r'''
\begin{table}[t]
\centering
\caption{Running example after one downstream failure. Planned versions are
assets 1.5.0, base 0.8.3, and app 2.1.1. This is a model trace, not a timing
measurement. A no-progress attempt may be inserted without violating safety;
it is excluded from the progress premise of the convergence bound.}
\label{tab:runs}
\small
\begin{tabular}{@{}llll@{}}
\toprule
Run & Plan & Recorded success & Failure \\
\midrule
1 & assets, base, app & assets, base & app \\
2 & app 2.1.1 & app & none \\
3 & empty & none & none \\
\bottomrule
\end{tabular}
\end{table}
'''
p.write_text(s)
