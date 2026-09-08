from pathlib import Path
p=Path('output/conference-submission-2026-09-09/icsa-draft.tex');s=p.read_text()
s=s.replace('Propagate: minor          Channel: beta\nPropagate-Depth: all      Propagate-Channel-Depth: all','Propagate: minor\nChannel: beta\nPropagate-Depth: all\nPropagate-Channel-Depth: all')
for label in ['tab:headers','tab:runs']:
 at=s.index('\\label{'+label+'}'); a=s.rfind('\\begin{table}',0,at); b=s.index('\\end{table}',at)+len('\\end{table}')
 block=s[a:b].replace('\\begin{table}', '\\begin{table*}').replace('\\end{table}','\\end{table*}'); s=s[:a]+block+s[b:]
s=s.replace(r'''  \mathit{src}_\sigma(u) = \{ p \in \mathit{scope}(u) :
    \mathit{disch}_\sigma(p,c_u) \lor
    \lnot(\mathit{canc}(c_u,p) \lor \mathit{held}(p)) \}.''', r'''\begin{aligned}
  \mathit{src}_\sigma(u) = \{ p \in \mathit{scope}(u) : {}&
    \mathit{disch}_\sigma(p,c_u) \\
    &\lor\lnot(\mathit{canc}(c_u,p) \lor \mathit{held}(p)) \}.
\end{aligned}''')
s=s.replace(r'\text{(\textbf{consumer\'s} window)}', r'\text{(fresh window)}') if False else s.replace("\\text{(\\textbf{consumer's} window)}",r'\text{(fresh window)}')
s=s.replace(r'''  \mathit{adm}_\sigma(u,D) \;\equiv\;\;
     & D''',r'''  \mathit{adm}_\sigma(u,D) \;\equiv\; & \\[-0pt]
     & D''')
s=s.replace(r'\\[-1mm]',r'\\')
s=s.replace(r'''     \ \lor\ \mathit{pin}_\sigma(P)\downarrow) \,\},''',r'''     \\
    &\ \lor\ \mathit{pin}_\sigma(P)\downarrow) \,\},''')
s=s.replace(r'''      & \text{if } \mathit{core}(B) = t \wedge \mathit{ch}(B) =
        \mathit{ch},\\''',r'''      & \begin{array}{l}\text{if } \mathit{core}(B) = t\text{ and}\\
        \mathit{ch}(B) = \mathit{ch},\end{array}\\''')
p.write_text(s)
