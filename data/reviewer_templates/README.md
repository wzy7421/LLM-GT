# IPM-D-26-05980 | Reviewer evidence demonstration and blank CSV schemas

**DEMONSTRATION ONLY — NOT EMPIRICAL EVIDENCE — NOT FOR SUBMISSION.**

This public GitHub branch provides blank CSV shells sized to the manuscript-reported quantities and one fictional example row for each schema. Every fake reference is explicitly prefixed DEMO_ or TMP_. No new independent assessment, adjudication, LLM call or operator reconstruction was performed here.

## Independent evaluation (Group 1)
- independent_inventory_34.csv: 34 blank theme IDs and their documentary boundaries.
- candidate_matching_197.csv: 197 blank candidates, allocated to the six conditions according to the manuscript (27, 32, 34, 37, 34, 33).
- dispute_adjudication_9.csv: nine blank third-party dispute records.
- inventory_external_30.csv: 30 blank unmatched candidates to classify through documentary support and conceptual distinctness.
- reference_crosswalk.csv: 412 blank document-level links.

## Pure LLM comparator (Group 2)
- pure_llm_17_batch_manifest.csv: manuscript-reported input allocation of 16 batches of 25 and one batch of 12, **not proof that these calls were made**.
- pure_llm_execution_log.csv: 18 blank starter rows; add one per actual request/retry, possibly many more.
- pure_llm_37_frozen_candidates.csv: 37 blank automated candidates and consolidation lineage.

## Four-condition mechanism comparison (Group 3)
- reconstruction_operator_log.csv: four blank starter condition records; extend to all operators and actual runs.
- subset_24_theme_recovery.csv: 4 × 24 blank paired theme judgments, with actual output-lock evidence required.

## How to use
1. Inspect `demo/` to understand field meanings; **never publish these fictional examples as real experiment results**.
2. Replace `TMP_` placeholders in `templates/` using original dated records (initial ratings, third-party adjudication, documentary provenance, frozen inputs/outputs and model request logs).
3. Do **not** fill names, labels, dates, ratings, source links, request IDs or hashes by reverse-engineering the paper's aggregate statistics.
4. In published replacement files, use independent stable anonymized identifiers and assess privacy, literature full-text redistribution rights, API secrets and archival source conditions.
5. The manuscript's reported 167/15/15 split, κ=0.82, 17 input batches and 21/24 versus 23/24 are **targets for verification, not evidence validated by these files**.

This branch adds demonstration files only and does not modify the existing README, runtime code or manuscript-derived reported data on `main`.
