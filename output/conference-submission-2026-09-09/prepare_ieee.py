from pathlib import Path
import re
out=Path('output/conference-submission-2026-09-09'); s=Path('paper/icse/main.tex').read_text()
s=s.replace('\\documentclass[sigconf,nonacm]{acmart}\n\\settopmatter{printfolios=true}', r'''\documentclass[10pt,conference]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsthm,graphicx,url}
\usepackage[hidelinks]{hyperref}
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{proposition}{Proposition}
\theoremstyle{definition}
\newtheorem{definition}{Definition}''')
a=s.index('\\author{'); b=s.index('\\begin{abstract}',a)
s=s[:a]+r'\maketitle'+'\n\n'+s[b:]
a=s.index('\\begin{CCSXML}'); b=s.index('\\section{Introduction}',a)
s=s[:a]+r'''\begin{IEEEkeywords}
release engineering, semantic versioning, sagas, partial failure,
idempotency, deterministic replay
\end{IEEEkeywords}

'''+s[b:]
s=s.replace('\\url{https://github.com/yohimik/dispat}. A local supplementary bundle retains\nthe proof details, vectors, fixtures, harnesses, checksums, and raw records;\nits archival deposit remains a publication-readiness requirement.', '''an author-identifying public repository, omitted for anonymous review.
A local supplementary bundle retains proof details, vectors, fixtures,
harnesses, checksums, and raw records. The accompanying anonymous artifact draft provides experiment scripts,
selected raw and summary records, and a manifest of source and review-copy
hashes. Author-identifying paths are redacted. Binaries, container images,
Git repositories and large compressed dossiers are omitted from this
non-executable review draft. The complete archival replication package
is planned for publication with the accepted paper.''')
s=re.sub(r'\\url\{https://github.com/yohimik/[^}]+\}', 'Public source URL omitted for anonymous review',s)
# The integration PR identifies the tool author; it is illustrative rather than experimental evidence.
a=s.index('HOL Guard PR~2813'); b=s.index('\\section{Evaluation}',a)
s=s[:a]+s[b:]
a=s.index('\\bibitem{guard}'); b=s.find('\\bibitem',a+8)
if b<0: b=s.index('\\end{thebibliography}',a)
s=s[:a]+s[b:]
(out/'icsa-draft.tex').write_text(s)
