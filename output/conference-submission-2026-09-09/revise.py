from pathlib import Path
p=Path('paper/icse/main.tex'); s=p.read_text()
s=s.replace('Releasing Polyglot Projects as Distributed Transactions:\\\\\n       The CCME Protocol and Its Implementation in dispat','Recoverable Releases Across Package Registries:\\\\\n       A Git-Backed Saga Protocol')
s=s.replace('CCME~2.0\nincorporates six repairs derived from counterexamples to the historical 1.0\nspecification, including separate train and fresh-work windows and\nchannel-aware admission.', 'Minimal counterexamples establish why delivery must be tracked per consumer,\nwhy prerelease aggregation needs a separate window, and why retry guarantees\nrequire stable channel and suppression predicates.')
s=s.replace('agrees with the historical 1.0 oracle on all 1{,}500 core\ninstances', 'agrees with a restricted reference oracle on all 1{,}500 core\ninstances')
a=s.index('\\noindent\\textbf{Specification snapshot.}'); b=s.index('\\section{Introduction}',a)
s=s[:a]+s[b:]
s=s.replace('the formalisation\n    records counterexamples to the historical 1.0 rules and proves the\n    repaired 2.0 guarantees under their explicit retry invariant', 'minimal counterexamples identify necessary design choices and\n    the explicit invariant under which retries preserve the guarantees')
a=s.index('\\emph{Diagnostics and parsing.}'); b=s.index('\\section{The Model}',a)
s=s[:a]+s[b:]
a=s.index('The explicit graduation rule in'); b=s.index('\\end{definition}',a)
s=s[:a]+s[b:]
a=s.index('CCME~3.0.1\nvectors'); b=s.index('\n\nOrder matters',a)
s=s[:a]+s[b:]
s=s.replace('(H1) is not decorative. In the historical 1.0 claim, ``all releases are\nstable\'\' was treated as sufficient, although', '(H1) cannot be replaced by requiring stable completed releases:')
s=s.replace('This historical counterexample is why CCME~2.0 states H1 as an\nexplicit component of the retry invariant rather than claiming unconditional\nversion stability.', 'Thus unchanged inherited-channel state must be an explicit component of the\nretry invariant; successful stable releases alone do not imply version stability.')
s=s.replace('\\section{The Competitors, Instantiated}', '\\section{Release-Tool Comparison}')
s=s.replace('under CCME~2.0 \\S19.4', 'under the publish-then-record protocol')
s=s.replace('We tested it differentially. An oracle\nimplementing Section~\\ref{sec:model} and nothing else, each function\ntracing to its Definition, was written in $\\sim$300 lines of Python;\na seeded generator produces random instances (5--20 packages, layered\nDAGs, 4--12 units over the directive grammar, mixed tag states); each\ninstance is realised as a real git repository and planned by both the\noracle and the released binary taken from the project\'s official\ncontainer image, so the subject is the shipped bytes (1.7.2 below; the\n1.4.0, 1.6.0 and 1.7.0 releases agree with it on every row of every seed). A\ngate of golden cases lifted from this paper\'s own tables and examples\nmust pass first.', 'We test it with selected specification vectors and a restricted reference\noracle in approximately 300 lines of Python. The oracle predates the complete\nmodel presented here: agreement within its core domain is evidence for that\nfragment, not a proof of refinement of the full model. A seeded generator\nproduces instances with 5--20 packages, layered DAGs, 4--12 units, and mixed\ntag states. Each instance becomes a real Git repository and is planned by\nthe oracle and the released binary. Golden cases gate the comparison.')
a=s.index('Unless explicitly marked as the fresh'); b=s.index('\\subsection{Differential',a)
s=s[:a]+'''The primary campaign uses the official dispat~1.8.2 image and implemented
CCME~2.0 semantics~\\cite{ccme2}. Release-tool comparisons retain their pinned
1.7.x measurements and are not represented as new 1.8.2 experiments. The
artifact records images, seeds, raw streams, checksums, and harness versions.

'''+s[b:]
a=s.index('The historical 1.0 oracle used two profiles.'); b=s.index('\\subsection{Fresh CCME',a)
s=s[:a]+'''The core profile isolates the oracle's shared semantic domain. The full
profile deliberately exercises prerelease baselines, channel-only entries,
and bump-less directive types outside that domain. Differences in the latter
are classified diagnostically; they are not counted as passing conformance
checks. The current campaign below reports both profiles, including rejected
plans and the limits of its heuristic classification.

'''+s[b:]
s=s.replace('\\subsection{Fresh CCME 2.0 / dispat 1.8.2 Campaign}', '\\subsection{Released-Binary Evaluation}')
s=s.replace('and distinguishes semantic refusals from execution failures. Preserved 1.8.1\nrecords use the earlier runner; no runtime improvement is inferred.', 'and distinguishes semantic refusals from execution failures. These timings\nare not compared with runs using an earlier harness.')
a=s.index('The strongest validation result concerns the formalisation itself.'); b=s.index('\\section{Threats to Validity}',a)
s=s[:a]+r'''Minimal counterexamples identify why several apparently simpler designs fail.
They serve as regression obligations and explain the model's assumptions.

\begin{enumerate}
  \item \emph{Aggregation is not discharge.} Reusing a stable-baseline
    train window for fresh admission can produce \code{beta.1},
    \code{beta.2}, $\ldots$ without new commits. Separate $W$ and
    $W^\circ$ retain train intent while discharging delivered work.
  \item \emph{Suppression must remain stable across retries.} If a
    cancelled or corrected source is later released, its discharged record
    can change the source set and reach new consumers. H2 excludes this
    widening within a reviewed retry sequence; changing it requires a new plan.
  \item \emph{Inherited channels are mutable inputs.} The graduation
    example in Remark~\ref{rem:drift} changes a failed consumer's next version
    unless H1 preserves its inherited-channel inputs.
  \item \emph{Reverse audits need the full admission predicate.} A
    consumer-side staleness audit that omits channel eligibility or target
    self-exclusion can disagree with forward propagation.
  \item \emph{Axis independence is one-way.} Resolving channels can make a
    dependency ineligible and suppress a bump; suppressing a bump does not
    suppress a channel change. Resolving channels first preserves this order.
  \item \emph{Shared graph traversal does not merge unit identity.}
    Subtracting a union of source sets excludes legitimate targets of other
    units; admitting every traversed node can include a unit's own source.
    Traversal may be shared, but admission and provenance remain per unit.
\end{enumerate}

These counterexamples motivated the released rules used in the model. Their
role here is to establish design necessities, not to claim defects in the
current specification. The selected released-binary vectors cover six cases;
they do not establish full implementation refinement.

'''+s[b:]
s=s.replace('Formalisation found six defects in the historical 1.0 prose; CCME~2.0\nincorporates the corresponding repairs.', 'Minimal counterexamples show why separate admission windows, stable retry\npredicates, and per-unit provenance are necessary.')
s=s.replace('The historical dispat~1.7.x executed\nfaults confirm', 'The pinned release-tool fault experiments support')
s=s.replace('\\bibitem{ccme301}\nCCME Specification 3.0.1, corrected algorithm guidance.\n\\url{https://github.com/yohimik/dispat/blob/8238e2465670b39609f8dcf5a8a5d34ea71d3db1/specs/ccme-spec/SPEC.md},\naccessed 2026.\n\n','')
s=s.replace('CCME Specification 2.0.0 and historical 1.0.0 snapshot.\n\\url{https://github.com/yohimik/dispat/blob/d3ce8ae637232908ced82efb5cda550f60ed2fdf/specs/ccme-spec/SPEC.md};\n\\url{https://github.com/yohimik/dispat/blob/713f1a0b/pkg/ccme/SPEC.md},', 'CCME Specification 2.0.0.\n\\url{https://github.com/yohimik/dispat/blob/d3ce8ae637232908ced82efb5cda550f60ed2fdf/specs/ccme-spec/SPEC.md},')
ai=r'''\section*{Acknowledgments: AI Assistance}
OpenAI Codex agents assisted with drafting and revising the exposition and
proof arguments throughout Sections~\ref{sec:intro}--\ref{sec:conclusion},
writing experiment harness code, running experiments, and summarising the
resulting records. This assistance extended beyond language editing.
Reported measurements were obtained from program executions rather than
language-model predictions. The human author remains accountable for the
claims, proofs, references, and experimental interpretation.

'''
s=s.replace('\\section*{Data Availability}',ai+'\\section*{Data Availability}')
p.write_text(s)
