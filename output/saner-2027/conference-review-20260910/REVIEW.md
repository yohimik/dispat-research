# SANER paper and experiment review

The paper's strongest contribution is a precise recovery rule for evolving, heterogeneous releases: successful publication by a provider must not erase an unfinished consumer's versioned obligation. Stage ordering explains when work may execute; consumer-relative admission explains what remains owed. Keeping these two responsibilities distinct gives the paper a coherent software release engineering contribution.

The revision targets **Software Release Engineering, Continuous Integration and Delivery** in the SANER Research Track. The appropriate presentation is an accessible system explanation, followed by the mathematical model and guarantees, followed by experiments organized around questions that challenge those guarantees. Recent SANER work provides useful precedents for experimental design, but neither an award nor a particular section sequence establishes that another paper will be accepted.

## Conference requirements

The official 2027 call welcomes empirical, theoretical and tool-oriented work. It specifies IEEE conference format, a 24-point title and 10-point body, with at most ten content pages and two additional references-only pages. This revision uses exactly 10+2. Evaluation considers novelty, significance, soundness, verifiability and presentation. The call requires anonymous review, substantive AI-use compliance and a Data Availability statement after the conclusion. Artifact sharing is encouraged, not compulsory. Mandatory abstract and paper deadlines are 21 and 25 September 2026, AoE. The preprint anonymity period begins one month before the paper deadline. The call does not prescribe a universal section order. The linked standalone AI-guidance page returned 404 when checked; the Research Track policy remains the available authority. [^1]

## Recent technical neighbors

The selection emphasizes SANER 2026, the most recent completed edition, with 2025 examples where useful. This is a targeted review of primary publications and official conference records, not a systematic review or a claim that no equivalent protocol exists. A paper's track, accessible version and award status are recorded separately. The open author copies of the CI-context and failure-management papers were inspected; publisher-embargoed text was not treated as accessible.

| Paper | Year and track | Relevance to this paper | Access and award evidence |
|---|---|---|---|
| Huang, Zaidman and Proksch, *Does One CI-ze Fit All? How Continuous Integration Performs in Different Contexts* | 2026, Research | Dataset composition and explicit contextual limits | Full author PDF; no verified award [^2][^3] |
| Cardoen, Mens and Decan, *An Empirical Analysis of Code Clones in GitHub Actions Workflows* | 2026, Research | Shared configuration, duplication and existing reuse mechanisms | Institutional abstract and metadata; full publisher text embargoed; no verified award [^4] |
| Bui, Grintz, Berndt and Bach, *Using Large Language Models to Support Automation of Failure Management in CI/CD Pipelines: A Case Study in SAP HANA* | 2026, Industrial | Failure management, explicit outcome criteria and ablation | Full author preprint; no verified award [^5][^6] |
| Macho, Stengg and Pinzger, *Agent-based Dependency-related Build Repair* | 2026, Early Research Achievement | Dependency failures and distinction between repair and replay | Full author PDF; no verified award [^7][^8] |
| Khelifi and colleagues, *GHAminer: An Open Source Tool to Extract GitHub Actions Build Metrics* | 2025, Tool Demo | Traceable CI observation and build metrics | Official abstract and institutional metadata; no verified award [^9] |

Huang and colleagues make dataset composition an explicit experimental variable rather than treating CI adoption as one uniform intervention. Their article proceeds from background and related work to methodology, then separate research-question results, discussion and threats. The lesson for a release protocol is to specify which graph shapes, failure boundaries, version states and host environments are covered. A balanced fixture matrix improves coverage of chosen factors; it does not become a representative sample of software teams. [^2]

Cardoen and colleagues investigate duplication in GitHub Actions workflows and opportunities for existing reuse mechanisms. Their institutional abstract supports the importance of workflow maintenance, but does not show that this release protocol reduces maintenance cost. A claim of less configuration duplication should therefore be tied to actual unchanged workflow files and package additions, while human effort remains unmeasured. The published SANER study is distinct from an earlier BENEVOL version with different dataset counts. [^4]

Bui and colleagues evaluate failure diagnosis and proposed solutions in one industrial CI/CD setting, varying the supplied knowledge in an ablation study. Their outcomes concern error location and solution accuracy. Those denominators are not comparable to publication-recovery episodes. The transferable practice is isolating the contribution of a mechanism under specified inputs. Our source-window counterfactual asks whether provider completion can discard an outstanding obligation; it does not claim to outperform a failure-diagnosis system. [^5]

Macho and colleagues evaluate dependency-related build repair, including the effect of full versus summarized logs and repeated model runs. This addresses changing a broken build configuration. In contrast, retry stability assumes fixed reviewed release inputs: a repair that changes dependency policy requires a new plan. The two tasks can complement each other, but their success rates cannot be compared as if they implement the same contract. [^7]

GHAminer collects build status, duration, changes, tests and repository information. It motivates observable, inspectable experiment records. It is a tool-demo paper, so its length and evaluation depth are not templates for a full research submission. This revision retains command-level observations and stage events rather than replacing them with a single total of passing assertions. [^9]

## Award-winning presentation examples

The official 2026 awards page identifies STELLAR and the TEE study below as Research Track Distinguished Papers. The 2025 issue-tracker award is supported by the author's institutional thesis. These are verified examples, not a complete census of award recipients. Their topics differ from release recovery, so they are useful presentation references rather than competing release mechanisms. [^10][^14]

| Paper | Award year | Observed structure | Useful practice |
|---|---|---|---|
| Sorokin and colleagues, *STELLAR: A Search-Based Testing Framework for Large Language Model Applications* | 2026 | Motivation and definitions; approach; evaluation; threats; qualitative analysis; related work | State effectiveness and diversity questions, comparison budgets and interpretable outcomes [^11] |
| Niu and colleagues, *What You Trust Is Insecure: Demystifying How Developers (Mis)Use Trusted Execution Environments in Practice* | 2026 | Background; data collection and labeling; question-specific findings; discussion; threats | Expose filtering, population boundaries and the implications of each result [^12] |
| Das, Mondal and Roy, *Why Do Developers Engage with ChatGPT in Issue-Tracker? Investigating Usage and Reliance on ChatGPT-Generated Code* | 2025 | Motivating example; methodology; question-specific findings; discussion; threats; related work | Carry concrete examples into explicit questions and distinguish different outcome constructs [^13] |

STELLAR is a system-oriented example with a formal optimization formulation; the two empirical papers do not follow a system-to-theorem-to-experiment template. Thus the requested order is a good fit for this contribution, not a verified convention followed by every SANER paper. Adopting unfamiliar mathematical machinery or adding irrelevant award-winning citations would weaken the argument. The revision instead preserves the existing mathematical content and improves its connection to the practical release problem.

## Scientific content to preserve

The mathematical contribution is the discipline of admission and discharge. A release intent is checked against the consumer's fresh-work window; the origin's completed release does not by itself erase that contribution. A separate train window retains accumulated prerelease target information. A successful consumer record discharges fresh work, including channel contributions and exact pins when applicable.

The retry assumptions are substantive. The corrected intent stream, source membership, graph, scope and depth predicates, suppression, and relevant resolved channel inputs must remain fixed except for valid completion records. Several stability lemmas are direct consequences of that invariant. Their value is making operational obligations explicit; they do not show that every arbitrary repository mutation is safe.

The eight guarantees remain conditional model statements. The convergence bound counts runs that make progress. An unlimited series of unsuccessful attempts is not bounded by the number of packages. Recorded-state idempotence also differs from external exactly-once execution: a registry write can succeed while its response or Git record is lost. Such an integration needs safe repetition or artifact-identity reconciliation.

These findings should survive presentation edits unchanged. Build DAGs, Git persistence, sagas, reusable CI and cross-language hooks are established ideas. The release-specific combination and its admission discipline must carry the novelty argument. Existing deployment and reconciliation antecedents remain relevant even though they are older than the newest SANER papers.

## Experimental changes and interpretation

The original 1.10.0 campaign remains a frozen baseline. Its 300 accepted core histories, 20 recovery episodes, two separate 30-execution registry topologies and three CI repetitions are not replaced, pooled or relabeled. Earlier 1.8.2 evidence continues to expose restricted-oracle disagreements, reconstructed-policy replay mismatches and planning costs under its original environment. The failed 1.9.0 strict-overlap oracle attempt remains part of the evidence history.

The supplementary mechanism campaign has a prospective protocol and a pilot stage. Its designed factors are graph shape, stable/beta baseline, fault location and fault boundary. Each factor corresponds to a potential objection to the central recovery claim. Five four-package topologies exercise depth, fan-out, fan-in, redundant paths and disconnected components. Three failure boundaries distinguish an unfinished build, refused publication and an artifact written before a publisher reports failure. Repeated failure probes safety without progress; repair probes discharge and the final no-op state.

The source-window alternative is evaluated against the same observed completion states. It is an analysis-model ablation, not a different compiled product or a generalization about a competing tool. The direct comparison is the set of obligations lost by discarding the originating unit after its source completes. The observed counterexamples demonstrate the necessity of that distinction in the designed cases, not population-wide superiority.

The local immutable publisher makes the uncertain-outcome assumption executable. It verifies version/content identity before adopting a preexisting artifact. Separate foreign-content controls test rejection of a conflicting identity. Passing these controls supports that adapter contract; it cannot validate every npm, OCI or arbitrary shell publisher. The prior real-registry campaign supplies complementary ecosystem observations.

Finite model exploration covers a deliberately small stable-channel projection. Enumerating the failure subsets and reachable completion states of ordered four-node DAGs strengthens checking of the transition model. It does not mechanize the full mathematical proof, explore every concurrent external interleaving, or cover the complete parser and channel language. Model states, transitions, episodes and repeated verifier predicates are separate units.

All new experimental execution uses Docker, with the measured binary hash, image identity, platform, resource limits, code hashes and raw outputs recorded. A Docker image digest constrains the userspace; it does not make scheduling, host kernels or wall-clock performance identical on all machines. Consequently the new campaign emphasizes observable safety and recovery states rather than a speedup claim. The exact runner is available locally, but no Docker/OCI image export is retained in the repository. The retained Dockerfile uses digest-pinned parents and an APK package lock; rebuilding also depends on package-mirror availability and may yield a different image identity. A fresh-machine rebuild must be recorded as a separate provenance run unless the exact measured image is available.

## Completed mechanism results

The separately frozen `full-01` run completed all 140 designed episodes. Its independently implemented offline consistency checker reconstructed plans, completion records and model records from retained observations and reported no discrepancies. This is a second implementation of the checks, not an independent scientific replication. The pilot is retained separately and is not included in the 140.

| Designed stratum | Episodes | Episodes meeting their specified outcome | Cases losing obligations under the source-window counterfactual | Lost obligations |
|---|---:|---:|---:|---:|
| Failure before build completion | 40 | 40 | 28 | 41 |
| Failure before publication | 40 | 40 | 28 | 35 |
| Failure after local write, before successful response | 40 | 40 | 28 | 35 |
| No-fault controls | 10 | 10 | 0 | 0 |
| Foreign-content controls | 10 | 10 | 10 | 10 |

Across the 120 fault episodes, the released binary retained the residual obligation set at the original versions. Repeating the same fault did not change the pending plan or completion tags. Repair completed the remaining work; the final invocation performed no additional build or publication stages. The source-window counterfactual lost work in 84 of these episodes, totaling 111 obligations. The ten foreign-content controls are separate: each rejected the conflict without a new completion record and recovered after the valid content was restored. Counting them together with fault episodes would give 94 cases and 121 obligations, but that combined number is not the primary comparison.

Each completed case recorded four actual writes by the local publication adapter, one per package; repeat invocations could verify and accept an existing identical artifact. Deliberate foreign-content substitution is a test intervention, not an adapter write. This distinction matters: the experiment supports the supplied reconciliation contract, not exactly-once arbitrary external effects.

The finite projection explored 64 ordered four-node DAGs and four single origins per graph: 772 reachable states, 2,270 failure-subset transitions and 1,054 progress transitions. It found no projection-invariant violation. The source-window mutant discarded pending work in 260 enumerated states. Those are exhaustive counts for the stated finite projection, not independent samples or a replacement for the full proofs.

The [campaign results](../../../experiments/saner-2027/campaign-mechanisms-20260910/RESULTS.md) provide the binary/image identities, finer strata, timestamps, archive hashes and reproduction instructions. The original 103-file baseline manifest remains unchanged. The full fixture archive was checked byte-for-byte before expanded copies were removed; an offline consistency replay from a fresh extraction passed all 140 cases. A deliberately corrupted disposable copy failed verification, and reusing the completed run name was refused. The final manuscript and source-preservation checks are recorded separately with the paper's PDF evidence.

## Gap assessment

| Reviewer concern | Resolution in the revision | Remaining boundary |
|---|---|---|
| Contribution sounds like another build DAG | Explain the orphan scenario before notation; contrast scheduling with obligation retention | Related systems may implement equivalent policies in some configurations |
| Experiments read as an internal test inventory | Organize around questions, specified factors, outcome units and explicit answers | Generated cases remain designed fixtures |
| Main recovery mechanism lacks isolation | Add source-window counterfactual on matched completion states | Not a modified-binary or competitor ablation |
| Failure schedules are narrow | Add fault locations, three boundaries, repeat-without-progress and finite-state exploration | Not exhaustive concurrency or distributed crash testing |
| Lost publication responses are only a disclaimer | Exercise a local identity-checking adapter and foreign-content refusal | Adapter-specific evidence, not external exactly-once publication |
| CI benefits imply reduced developer effort | Tie claims to unchanged workflow hashes and observed gates | No user study or quantified onboarding effort |
| Cross-platform support looks experimentally validated | Retain shared-configuration explanation and state the untested native Windows boundary | Native Windows/Linux equivalence is still unmeasured |
| Mathematical assurance appears to apply to the binary | Preserve proofs and distinguish them from selected implementation traces | Full refinement and mechanized proof remain open |
| Historical results appear current | Separate versions, protocols and failed attempts | Historical scale and competitor results are not latest-version benchmarks |
| Reproducibility depends on a developer machine | Pin Docker execution and provide append-only run records and archive checks | Exact runner export is absent; rebuild identity and external package availability are not guaranteed; anonymous distribution remains an author decision |
| An award-like presentation is confused with evidence | Use recent topical neighbors for technical positioning; award examples for method and exposition | No justified prediction of acceptance or an award |

“Closing gaps” should mean resolving unsupported claims or adding evidence appropriate to the stated claim. It cannot honestly mean declaring universal portability, industrial effectiveness, or a refinement proof after a finite local campaign. Those remain explicit limits. The main contribution is defensible without claiming them.

## Review judgment

The strongest reading is a model-backed release protocol with controlled implementation evidence. Reviewers should be able to identify the practical failure, see which rule prevents it, inspect its assumptions, and follow an experiment designed to challenge that rule. The revised paper should avoid making the size of the codebase, the amount of AI assistance, or the number of assertions part of its scientific significance argument.

The strongest unresolved objection is external validity. A synthetic matrix can establish precise behavior and expose counterexamples, but it cannot establish how often the problem occurs or how much engineering effort the protocol saves in practice. The historical replay already demonstrates limits of transferring release policy. Preserve that negative evidence. A future field study should recruit independent teams or mine actual interrupted release histories with inclusion criteria and an explicit policy-mapping procedure.

A second objection is the model-to-implementation boundary. The finite checker and actual command traces improve assurance for a defined fragment, while hooks, recording failures, finalization and complex channel interactions still require deeper refinement. These should remain bounded claims rather than be hidden in footnotes. Author review of the full proofs is still necessary.

Before submission, resolve the history of public versions and promotion, verify exact AI model labels against the author's records, and decide how anonymous supporting materials will be supplied. No submission, public artifact upload, or repository-visibility change is part of this revision.

## Final manuscript verification

The delivered paper has exactly ten content pages followed by two references-only pages, with 43 cited entries in first-citation order. It uses IEEE conference format with a 10-point body and 24-point title. The narrative proceeds through the practical system, mathematical model and guarantees, then four research questions and experiments. The requested topic appears in the keywords. All twelve pages were visually inspected; the final reference-page columns are balanced. Structural checks found no unresolved citations, missing glyphs, font substitution or overfull boxes.

The model and guarantee source files are byte-identical to the pre-revision versions. All 103 baseline files and 4,896 supplementary-campaign files match their manifests. The final PDF SHA-256 is `2c3e8ecb868e785400a9c8f22972bc49e30b05e60238dde8ed511dd7f64dd978`. See the [build evidence](../../../paper/saner/evidence/BUILD-20260910.json), [visual review](../../../paper/saner/evidence/PDF-20260910.json), and [final integrity record](FINAL-VERIFICATION.json). These checks validate presentation and evidence integrity, not submission eligibility or the mathematical proofs.

## Sources

[^1]: SANER 2027. [Research Track call, evaluation criteria and submission policies](https://conf.researchr.org/track/saner-2027/saner-2027-papers). Checked 10 September 2026.
[^2]: S. Huang, A. Zaidman and S. Proksch. [Does One CI-ze Fit All? How Continuous Integration Performs in Different Contexts](https://azaidman.github.io/publications/huangSANER2026.pdf). SANER 2026, pp. 491-502. [DOI](https://doi.org/10.1109/SANER67736.2026.00060). Author PDF inspected.
[^3]: SANER 2026. [Official Research Track presentation record for Huang et al.](https://conf.researchr.org/details/saner-2026/saner-2026-papers/36/Does-one-CI-ze-fit-all-How-Continuous-Integration-Performs-in-Different-Contexts). Resolves a conflicting companion-track label in one repository metadata field.
[^4]: G. Cardoen, T. Mens and A. Decan. [An Empirical Analysis of Code Clones in GitHub Actions Workflows](https://orbi.umons.ac.be/handle/20.500.12907/54129). SANER 2026, pp. 170-180. [DOI](https://doi.org/10.1109/SANER67736.2026.00028). Institutional abstract and metadata inspected; full text embargoed.
[^5]: D. Bui, S. Grintz, A. Berndt and T. Bach. [Using Large Language Models to Support Automation of Failure Management in CI/CD Pipelines: A Case Study in SAP HANA](https://arxiv.org/abs/2602.06709). SANER 2026, pp. 524-535. [DOI](https://doi.org/10.1109/SANER67736.2026.00063). Author preprint inspected.
[^6]: SANER 2026. [Official Industrial Track record for Bui et al.](https://conf.researchr.org/details/saner-2026/saner-2026-industrial-track/4/Using-Large-Language-Models-to-Support-Automation-of-Failure-Management-in-CI-CD-Pipe).
[^7]: C. Macho, K. Stengg and M. Pinzger. [Agent-based Dependency-related Build Repair](https://pinzger.github.io/papers/Macho2026-repair.pdf). SANER 2026. Author PDF inspected.
[^8]: SANER 2026. [Official Early Research Achievement Track record for Macho et al.](https://conf.researchr.org/details/saner-2026/saner-2026-early-research-achievement-era--track/13/Agent-based-Dependency-related-Build-Repair).
[^9]: J. Khelifi, Y. Benzina, M. Chouchen, A. Ouni, M. Sayagh and S. Bouktif. [GHAminer: An Open Source Tool to Extract GitHub Actions Build Metrics](https://conf.researchr.org/details/saner-2025/saner-2025-tool-demo-track/6/GHAminer-An-Open-Source-Tool-to-Extract-GitHub-Actions-Build-Metrics). SANER 2025 Tool Demo, pp. 834-838. [DOI](https://doi.org/10.1109/SANER64311.2025.00087). Official abstract inspected.
[^10]: SANER 2026. [Official awards](https://conf.researchr.org/attending/saner-2026/awards).
[^11]: L. Sorokin, I. Vasilev, K. E. Friedl and A. Stocco. [STELLAR: A Search-Based Testing Framework for Large Language Model Applications](https://tsigalko18.github.io/assets/pdf/2026-Sorokin-SANER.pdf). SANER 2026. Full author PDF inspected.
[^12]: Y. Niu, J. Shi, R. Han, Y. Liu, C. Ma, Y. Lyu and D. Lo. [What You Trust Is Insecure: Demystifying How Developers (Mis)Use Trusted Execution Environments in Practice](https://arxiv.org/abs/2512.17363). SANER 2026; author preprint version 3 inspected.
[^13]: J. K. Das, S. Mondal and C. K. Roy. [Why Do Developers Engage with ChatGPT in Issue-Tracker? Investigating Usage and Reliance on ChatGPT-Generated Code](https://joykrishan.github.io/assets/pdf/Why_Do_Developers_Engage_with_ChatGPT_in_Issue-Tracker_Investigating_Usage_and_Reliance_on_ChatGPT-Generated_Code.pdf). SANER 2025. Full author PDF inspected.
[^14]: J. K. Das. [Studying Developers' Engagement with ChatGPT](https://harvest.usask.ca/server/api/core/bitstreams/d46eb8a8-a39d-44b9-ae47-a3678ce9788e/content). University of Saskatchewan thesis; co-authorship statement records the SANER 2025 distinguished-paper award.
