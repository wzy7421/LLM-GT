# Data folders

## `demo/`

All files in `data/demo/` are **synthetic, schema-compatible examples** created for code demonstration. They do not contain records from the empirical 412-publication scholarly corpus or the 34,500-text external issue-public corpus.

- `academic_demo.csv` illustrates the scholarly-record schema used by `src/semantic_mapping.py`.
- `public_demo.csv` illustrates a de-identified short-text schema for optional external triangulation.
- `gt_audit_demo.csv` illustrates how human GT coding and memo identifiers can be represented in an audit ledger.

These demo files are intentionally small. Consequently, they are not expected to reproduce the 12-cluster academic solution, the eight public-topic families, or any manuscript metric.

## `derived/`

Files in `data/derived/` contain **aggregate values already reported in the manuscript**, not raw source data.

- `workflow_metrics.csv` reproduces the role-aligned workflow summary used in Table 7 / revised Fig. 4.
- `interpretive_depth.csv` reproduces the category-level GT-only versus full-hybrid depth values.
- `llm_stability_reported.csv` reproduces the manuscript-reported fixed-configuration repeated-run summary.

## Restricted data

Raw academic metadata and raw user-generated public-discourse records are not redistributed because the manuscript describes database licensing, platform terms, and re-identification constraints. The public repository therefore focuses on computational configuration, prompt structure, audit schema, aggregate outputs, and executable demonstration code.
