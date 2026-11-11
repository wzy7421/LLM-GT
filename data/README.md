# Data folders

## `demo/`

All files in `data/demo/` are **synthetic, schema-compatible examples** created for code demonstration. They do not contain records from the empirical 412-publication scholarly corpus or the 34,500-text external issue-public corpus.

- `academic_demo.csv` illustrates the scholarly-record schema used by `src/semantic_mapping.py`.
- `public_demo.csv` illustrates a de-identified short-text schema for the optional case-bounded transferability probe.
- `gt_audit_demo.csv` illustrates how human GT coding and memo identifiers can be represented in an audit ledger.
- `gate_demo.csv` illustrates the scaffold-to-claim gate and the optional expert-rating threshold screen using generic synthetic propositions.
- `llm_runs_demo.jsonl` illustrates a repeated-run label ledger. It is intentionally small and is not the empirical 20-unit × 10-seed ledger.

These demo files are intentionally small and synthetic. They are **not expected to reproduce** the 12-cluster academic solution, the eight public-topic families, the 200-output empirical stability summary, or any manuscript metric.

## `derived/`

Files in `data/derived/` contain **aggregate or audit-level values already reported in the manuscript**, not restricted raw source data.

- `workflow_metrics.csv` — original within-study 32-theme results (Table 9) including the manuscript-reported **110.5 person-hour complete hybrid workflow** (85.0 GT + 3.5 mapping/LLM + 22.0 integration); the 2.6 h mapping-only stage is nested in the 3.5 h stage and must not be added again.
- `independent_34_theme_metrics_reported.csv` — **Table 6 aggregate values only** for six conditions against the separately constructed 34-theme reference; this is not a release of the 34 reference definitions or 197 candidate-level records.
- `independent_matching_agreement_reported.csv` — the **Table C14a 2×2 aggregate binary agreement counts** (164/4/5/24). These can reproduce κ≈0.82 but do not validate exact theme-ID agreement or independent blindness.
- `reference_theme_crosswalk_reported.csv` — complete T01–T32 frozen reference-theme hit/miss crosswalk used to make the 30/32 full-hybrid coverage denominator auditable.
- `interpretive_depth.csv` — seven-category GT-only versus full-hybrid depth profile.
- `coding_reliability_reported.csv` — category-level raw agreement, one-vs-rest Cohen's kappa, 95% CI, and depth results.
- `coder_2x2_reported.csv` — reported 2 × 2 coder-decision cells for the 103-publication multi-label reliability subset.
- `llm_stability_reported.csv` — manuscript-reported 20-unit × 10-seed repeated-run summary: 120 academic-cluster outputs, 80 public-topic-family outputs, and 200 outputs overall.
- `runtime_audit_reported.csv` — three-run machine wall-time means and SDs reported in Appendix B.
- `external_acquisition_reported.yaml` — audit-level mirror of the source-specific acquisition routes, fixed C1/E1 retrieval expressions, observation window, source-level counts, access dates, retained-field schema, and exact-reconstruction boundary reported in Appendix B. It is **not** a runtime configuration file.
- `public_noise_audit_reported.csv` — reported review of the 1,987 initial external HDBSCAN noise labels, including initial agreement, kappa, disagreement count, and final documented dispositions.
- `platform_sensitivity_reported.csv` — observed, equal-platform, and leave-Weibo-out issue-public topic percentages.
- `mechanism_subset_reported.csv` — 103-publication blinded-subset mechanism comparison using the frozen 24-theme subset denominator.
- `gap_decisions_reported.csv` — 12 screened scholarly-workflow propositions and their final 8 eligible / 4 rejected decisions.
- `adjudication_outcomes_reported.csv` — 20-unit human adjudication outcome counts.

The complete hybrid (110.5 h) and GT-only (85.0 h) have comparable full-workflow endpoints; the manuscript reports **+25.5 h (+30.0%)** additional analyst effort, not a labor reduction. Mapping-only (2.6 h), combined mapping/LLM (3.5 h), and post-GT integration (22.0 h) are **stage-level** quantities; 2.6 h is included within 3.5 h, and stage endpoints must not be confused with complete workflows.

## Configuration versus audit artifacts

The repository intentionally contains **one runtime/manuscript configuration file**, `config/paper_config.yaml`. This matches the response letter's bounded repository inventory. The YAML file under `data/derived/` is a reported acquisition audit artifact, not a second configuration file.

## Restricted data and verification boundary

Raw academic metadata and raw user-generated issue-public records are not redistributed because the manuscript describes database licensing, platform terms, privacy constraints, and data-minimization requirements. The public repository therefore focuses on computational configuration, literal prompt structure, audit schemas, manuscript-reported aggregate values, and executable demonstration code.

The repository supports protocol-level and code-path reproducibility. It does **not** claim exact reconstruction of restricted corpora where the underlying licensed archives or source manifests are not independently accessible. The aggregate files mirror values disclosed in the manuscript; they do not independently validate the underlying empirical source records, expert judgments, or provenance.

## Independent 34-theme evaluation: release status

The manuscript reports six-condition aggregate reference recovery against a separate 34-theme inventory and initial binary agreement for 197 candidate evaluations. The two new `*_reported.csv` files **mirror only published table aggregates** and allow arithmetic validation. They do **not** contain the 34 item definitions, the 197 first-pass candidate-level judgments, nine dispute-resolution cases, original LLM responses, or operator execution logs. These empirical materials must be located and reviewed before any claim of independently reproduced matching or model execution. Do not regenerate historical execution logs or assessor decisions from aggregate counts. Where materials are legitimately unavailable, state the limitation explicitly.

The academic metadata and full-text evidence used by the hybrid workflow are not identical inputs. The pure automated LLM comparator used titles, abstracts and keywords, whereas grounded-theory-informed coding also used full text. The aggregate comparison alone does not isolate a causal effect of human involvement.
