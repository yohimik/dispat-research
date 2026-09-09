# Released implementation evidence: Dispat 1.9.0

Recorded 9 September 2026. This release record is separate from scientific experiment outcomes.

- Feature: validated source commit authoring through natural message options; existing release-step commit behavior retained.
- Implementation: `4c22611dc02c6a88e39fae48f9b3184cdb3ae2fe`.
- Independently discovered routing correction: `8402051e3842fec1ab3604d31d396c051778da1b`. CV-10 was found after the first push but before release; its pending CI run was cancelled, new regressions preserved HEAD and staged contents, and a focused correction passed fresh gates.
- [CI](https://github.com/yohimik/dispat/actions/runs/34300485697): all four jobs passed.
- [Release](https://github.com/yohimik/dispat/actions/runs/34302770429): all seven jobs passed, including macOS/Linux/Windows installation checks. Installation checks alone do not establish native Windows authoring-hook or process-tree parity.
- Final release commit: `37610088e00c2075a2fd621e61431f7b6e45105a`.
- Published: Dispat, models, agent guide, docs and four Docker images at 1.9.0; CCME specification at 3.0.2. Parser remains 2.0.0, unchanged.
- Released docs report: `packages/docs/static/test-reports/1.9.json`, source stamp `8402051e3842fec1ab3604d31d396c051778da1b`.
- Combined statement coverage: 19,305 / 20,317 (95.01895%). Unit and integration profiles are combined; integration-only CLI coverage is 10,062 / 11,720 (85.9%).
- Suite: 2,996 named tests and 37 fuzz targets. All 641 integration cases passed ordinary and separately instrumented subprocess race runs. Tests, subtests, fuzz seeds, and oracle assertions are different units.
- Fresh local TinyGo 0.43.0-net.2: both Linux architectures compiled; native ARM64 integration 823 tests/subtests passed, zero failures or skips. The Go suite and TinyGo suite are separate runs.
- Independent macOS authoring probes: 18/18 passed, comprising exact native-Git message-byte comparisons across cleanup/editor combinations, bypass rejection, and routing/index preservation.

## Immutable Linux ARM64 research input

- Image index: `yohimik/dispat-alpine@sha256:68b86c1a2508771420d6ac63503b71967228227efe3303f6f9a3f8aa90ea1520`.
- Platform manifest: `yohimik/dispat-alpine@sha256:bf89800987e88a14683fb86b7dede7e9de1fedef82a454b8669655db98096d35`.
- `/usr/local/bin/dispat` SHA-256: `be3370c472cdbfe66fe4256d3fc1ff78ff19bdd5f041ef222187a52767fa4f35`.
- Version line: `dispat 1.9.0 (linux_arm64)`; uname: `aarch64`. Checked with network disabled.
- Campaign lock and runner provenance are under `experiments/saner-2027/campaign-next-release-prepared/`. Outcome status is determined from the run's provenance and COMPLETE marker, not this release record.

## Follow-ups outside this feature

Windows descendant-process cancellation requires a native runtime/job-object review. The release runner emitted deprecation notices for actions authored for Node 20 and forced to Node 24; gates passed, but action upgrades deserve a separate compatibility change. Neither limitation is scientific evidence against the modeled release protocol.
