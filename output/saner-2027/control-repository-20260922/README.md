# Control-repository definition — September 22, 2026

The conference paper now defines a control repository as a repository holding deployment manifests, environment settings and artifact selections separately from application source. It distinguishes configuration intent from completed releases and retains source-owned completion records. This is described as established practice, not a newly invented repository pattern.

## Sources checked

- Puppet, *A Puppet Control Repository*: https://github.com/puppetlabs/control-repo — the template documents Puppetfile references, environment configuration and deployment structure.
- Florian Beetz, Anja Kammer and Simon Harrer, *GitOps*, section “Environment Configurations as Git repository”: https://www.gitops.tech/ — describes separate application and environment-configuration repositories and the latter’s desired deployment state.

Both sources were inspected on September 22, 2026 and cited directly in the paper. Bibliographic metadata also identified Florian Beetz and Simon Harrer, “GitOps: The Evolution of DevOps?”, IEEE Software 39(4), 70–75, 2022, DOI 10.1109/MS.2021.3119106. Its full text was unavailable for inspection, so it is not used as evidence for the exact definition. This search does not establish scholarly priority or absence of earlier descriptions.

## Scope and verification

Only system.tex, discussion.tex and references.tex changed. Nearby self-hosting and skill prose was condensed to preserve the page limit without changing the reported findings. The abstract, anomaly descriptions, mathematical model and experimental observations are unchanged. The separate technical report matches the protected hashes.

Tectonic compilation and paper/saner/check.py passed: ten content pages, two reference pages, 48 references. All twelve rendered pages were visually inspected; no clipping, overlapping text or illegible layout was found. verification.json records the source and PDF hashes. Before snapshots and changes.diff preserve the revision provenance.
