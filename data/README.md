# Data folders

## `demo/`

All files in `data/demo/` are **synthetic, schema-compatible examples** created for code demonstration. They do not contain records from the empirical 412-publication scholarly corpus or the 34,500-text external issue-public corpus.

- `academic_demo.csv` illustrates the scholarly-record schema used by `src/semantic_mapping.py`.
- `public_demo.csv` illustrates a de-identified short-text schema for the optional case-bounded transferability probe.
- `gt_audit_demo.csv` illustrates how human GT coding and memo identifiers can be represented in an audit ledger.
- `gate_demo.csv` illustrates the three recorded scaffold-to-claim gate requirements.
- `llm_runs_demo.jsonl` illustrates the repeated-run stability ledger schema.

These demo files are intentionally small. Consequently, they are not expected to reproduce the 12-cluster academic solution, the eight public-topic families, the 200-output empirical stability summary, or any manuscript metric.

## `derived/`

Files in `data/derived/` contain **aggregate values already reported in the manuscript**, not raw source data.

- `workflow_metrics.csv` reproduces the role-aligned workflow summary. The full-hybrid row contains no standalone person-time total; the separate post-GT integration/adjudication row records the additional 22.0 h stage after the corpus-level GT reconstruction was frozen.
- `interpretive_depth.csv` reproduces the category-level GT-only versus full-hybrid depth values.
- `llm_stability_reported.csv` reproduces the manuscript-reported 20-unit × 10-seed repeated-run summary: 120 academic-cluster outputs, 80 public-topic-family outputs, and 200 outputs overall.

The person-time quantities in `workflow_metrics.csv` have **non-equivalent endpoints**. They must not be used to calculate a percentage labor reduction.

## Restricted data

Raw academic metadata and raw user-generated issue-public records are not redistributed because the manuscript describes database licensing, platform terms, privacy constraints, and data-minimization requirements. The public repository therefore focuses on computational configuration, literal prompt structure, audit schemas, aggregate outputs, and executable demonstration code.

The repository supports protocol-level and code-path reproducibility; it does not claim exact reconstruction of restricted corpora when the underlying licensed archives or source manifests are not independently accessible.
