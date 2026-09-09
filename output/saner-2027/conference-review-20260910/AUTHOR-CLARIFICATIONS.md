# Author clarifications: release communication and dependency availability

This 10 September addendum follows the author's clarification after the conference revision in commit `fa30c15`. It updates practical framing, not experimental outcomes or mathematical claims. The earlier review and its verification records describe that earlier PDF; the follow-up paper has separate `BUILD-20260910-NOTES.json` and `PDF-20260910-NOTES.json` evidence.

## Release notes as reusable communication material

A private project may place little value on maintaining a conventional public changelog. Its developers can still mark release-worthy changes in commit messages while the work is fresh. At release time, those descriptions can be collected into version-specific notes. A developer can adapt the summary into a social-media announcement, or pass it to a manager to prepare a stakeholder report. The practical benefit is reuse of development-time context during release communication.

For example, a scoped feature description recording new theme assets supplies both release intent and a starting point for a human-facing explanation of the delivered change. A human still selects and edits the material for its audience. The paper does not assert that the system publishes social posts, generates managerial reports automatically, or demonstrably saves staff time.

The versioned 1.10 documentation describes scoped/typed commit units, per-package changelog generation, configurable headings and sections, and reuse of changelog text as a GitHub release body. These support the underlying collection and rendering capability. The proposed downstream communication use is an author-identified application, not a new empirical result. Human-facing note entries are distinct from the completion tags used by the recovery model.

Read-only implementation-documentation evidence:

- [Commit units](/Users/yohimik/Projects/dispat/packages/docs/versioned_docs/version-1.10/reference/commits.md:14).
- [Record configuration](/Users/yohimik/Projects/dispat/packages/docs/versioned_docs/version-1.10/configuration/records.md:1).
- [Changelog step and release-body reuse](/Users/yohimik/Projects/dispat/packages/docs/versioned_docs/version-1.10/reference/releasing/steps.md:128).

## Dependency availability is the distinction

The npm example is a provider-consumer pair: the UI package depends on the assets library and can build using that provider's local workspace output before the provider is uploaded. Merely saying that two packages share output obscures this dependency.

The Docker example is also a provider-consumer pair: the application image has `FROM base:new-version`. Its isolated builder resolves the base through a registry and cannot use another builder's private local image store. The base must be made available through that configured registry first. This is a property of the illustrated setup, not a claim that Docker universally forbids local image reuse. Docker documents distinct builder drivers and image-loading behavior. [Docker container driver](https://docs.docker.com/build/builders/drivers/docker-container/).

For Go modules, a consumer resolving a new dependency version needs the corresponding tagged source to be available through its configured repository/proxy. A compiled provider binary is not a substitute for that module source. Local workspace or `replace` arrangements instead allow compilation against local source, so publication is not required in every Go setup. [Go module publication](https://go.dev/doc/modules/publishing), [Go module reference](https://go.dev/ref/mod), [Local replacements](https://go.dev/doc/modules/gomod-ref).

The product's [versioned Go example](/Users/yohimik/Projects/dispat/packages/docs/versioned_docs/version-1.10/examples/go.md:100) also describes local linking with `replace`. No new Go integration execution is claimed here. The retained npm/Docker experiments already test the two availability modes; these wording corrections do not change their protocol or results.

Source hashes and access scope are recorded in [the clarification provenance](AUTHOR-CLARIFICATIONS-PROVENANCE.json). The mathematical model and guarantees remain unchanged.

## Delivered follow-up verification

The follow-up PDF has exactly ten content pages and two references-only pages, with 44 references. Structural checks pass and all twelve pages were visually inspected. The model, guarantees, evaluation, mixed-results, and discussion sources are unchanged. Final PDF SHA-256: `e1101c91a00e732e982639e2f4834244c05c42c8c43188adb577fa6bc74349ff`. [Build record](../../../paper/saner/evidence/BUILD-20260910-NOTES.json); [visual review](../../../paper/saner/evidence/PDF-20260910-NOTES.json).
