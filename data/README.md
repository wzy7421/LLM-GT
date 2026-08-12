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

- `workflow_metrics.csv` — role-aligned workflow results against the frozen 32-theme reference inventory. The full-hybrid row contains no standalone person-time total; the separate post-GT integration/adjudication row records the additional 22.0 h stage after corpus-level GT reconstruction was frozen.
- `reference_theme_crosswalk_reported.csv` — the complete T01–T32 frozen reference-theme hit/miss crosswalk used to make the 30/32 full-hybrid coverage denominator auditable.
- `interpretive_depth.csv` — seven-category GT-only versus full-hybrid depth profile.
- `coding_reliability_reported.csv` — category-level raw agreement, one-vs-rest Cohen's kappa, 95% CI, and depth results.
- `coder_2x2_reported.csv` — the reported 2 × 2 coder-decision cells for the 103-publication multi-label reliability subset.
- `llm_stability_reported.csv` — the manuscript-reported 20-unit × 10-seed repeated-run summary: 120 academic-cluster outputs, 80 public-topic-family outputs, and 200 outputs overall.
- `runtime_audit_reported.csv` — the three-run machine wall-time means and SDs reported in Appendix B.
- `platform_sensitivity_reported.csv` — observed, equal-platform, and leave-Weibo-out issue-public topic percentages.
- `mechanism_subset_reported.csv` — the 103-publication blinded-subset mechanism comparison using the frozen 24-theme subset denominator.
- `gap_decisions_reported.csv` — the 12 screened scholarly-workflow propositions and their final 8 eligible / 4 rejected decisions.
- `adjudication_outcomes_reported.csv` — the 20-unit human adjudication outcome counts.

The person-time quantities in `workflow_metrics.csv` have **non-equivalent endpoints** and must not be used to calculate a percentage labor reduction.

## Acquisition specifications

`config/external_acquisition.yaml` mirrors the source-specific acquisition routes, fixed C1/E1 retrieval expressions, observation window, source-level raw/exclusion/retained counts, access dates, retained-field schema, and the exact-reconstruction boundary reported in Appendix B.

This documentation supports **protocol-level acquisition reproducibility**, not unrestricted reconstruction of licensed or platform-restricted source records.

## Restricted data

Raw academic metadata and raw user-generated issue-public records are not redistributed because the manuscript describes database licensing, platform terms, privacy constraints, and data-minimization requirements. The public repository therefore focuses on computational configuration, literal prompt structure, audit schemas, aggregate outputs, and executable demonstration code.

The repository supports protocol-level and code-path reproducibility. It does **not** claim exact reconstruction of restricted corpora where the underlying licensed archives or source manifests are not independently accessible.
