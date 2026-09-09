# Four-node extension oracle review

This extension contains 30 executions: five fixed configurations repeated six times in a seeded shuffled order. Repetitions expose nondeterministic scheduling or cleanup defects; individual verifier predicates are not independent observations.

## Identity and completeness

- Exactly 30 distinct `(configuration, repetition)` pairs prevents omission, duplication, or favorable filtering.
- The schedule seed, exact seeded shuffle, and result order must match, so the complete declared order is auditable.
- Every event must carry the expected version for its package. Assets changes are minor (`1.4.2` → `1.5.0`); unchanged dependents receive patch releases: ui `3.2.1`, base `0.8.3`, and app `2.1.1`.
- Unique event keys and start-before-end timestamps establish that later ordering comparisons refer to one well-formed interval per stage.

## Real artifact chain

- `assets/dist/theme.txt == new theme` proves the assets build copied the changed source rather than producing an unrelated constant fixture.
- `ui/dist/ui.txt == ui(new theme)` proves the UI build read the assets package's local build output.
- Local and published UI manifests retain a compatible dependency on the run's unique assets npm package. The build performs no install; this isolates local-output scheduling from registry resolution.
- Reading `ui.txt` from the base OCI layer proves the base build consumed UI local output.
- Reading the inherited `ui.txt` from the app OCI layout proves the final image includes the base artifact. This is required only after configurations that eventually complete; the deliberately missing barrier never repairs its app.
- Independent private-registry queries check `assets@1.5.0`, `ui@3.2.1`, `base:0.8.3`, and, except for the missing-barrier control, `app:2.1.1`. These observations distinguish publication from local files and Git tags.

## Required ordering

- Assets build end precedes UI build start, and UI build end precedes base build start, because each consumer reads its predecessor's local output.
- Assets publish end precedes UI publish start, and UI publish end precedes base publish start, because dependent publications must follow predecessor publication.
- Base publish end precedes app build start in the mixed, serialized, and app-failure initial executions because the app `FROM` resolves through the registry. The base-failure initial execution has no app stage; successful retries are checked separately.
- In the mixed configuration, UI build overlaps delayed assets publication; this is a fixture-controlled observed condition, not a universal scheduler claim. For the next edge, base build must start before UI publication completes, proving that UI publication is not a prerequisite. Base build may overlap publication or may finish before publication starts; both schedules are valid. The verifier records their interval intersection and whether the build completed before publication began as descriptive observations. Artificial delays expose ordering and are not throughput measurements.
- The first retained run failed only because the prior oracle required strict base-build/UI-publication overlap. That requirement excluded the valid completed-before-publication-start schedule. This predeclared correction tests the dependency-relevant ordering above; it does not turn the retained failed run into a formal result. A synthetic tooling check accepts completed-before-start and rejects a base build that starts after UI publication ends.
- In the serialized control, each npm predecessor's publication ends before its consumer build starts. This checks the explicit wait setting.
- In the missing-barrier control, app build begins before base publication ends, the app stage fails, its completion tag and registry image are absent, and the log records the unavailable base. These are expected control outcomes.

## Failure, repair, and idempotence

- A refused base publication ends with injected code 37, prevents all app stages, and leaves the base completion tag absent.
- An injected app build failure ends with code 37 after the correctly published base and leaves the app tag absent on the first attempt.
- Removing either injected fault must produce one successful retry with unchanged computed versions. No failed execution is discarded.
- Every repaired or initially successful configuration gets a final successful invocation with all completion tags and no build or publish stage. This checks persistent completion and no-op behavior; the missing-barrier control is intentionally excluded because its fault is the configuration itself.
- Cleanup inspection requires all experiment-owned containers to be absent. It does not claim that unrelated daemon resources were inspected or removed.
