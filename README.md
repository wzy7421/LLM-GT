# LLM-GT

![Manuscript alignment](https://github.com/wzy7421/LLM-GT/actions/workflows/manuscript-alignment.yml/badge.svg)

Reproducibility companion for the manuscript **“Human-in-the-Loop Knowledge Organization for Interdisciplinary Synthesis: Semantic Mapping, LLM-Assisted Interpretation, and Grounded Theory.”**

## Purpose

This repository provides a **schema-compatible, executable, reviewer-facing companion** for the computational and audit components described in the manuscript. It is designed to make the semantic-mapping pipeline, fixed LLM prompt structure, role-aligned evaluation logic, repeated-run stability diagnostics, divergence/adjudication logic, scaffold-to-claim gate, acquisition specifications, and manuscript-reported aggregate audit tables inspectable without redistributing licensed academic metadata or restricted user-generated records.

The repository is **not** a replacement for the manuscript and does not contain the empirical 412-publication scholarly corpus or the 34,500-text external issue-public corpus. Files in `data/demo/` are synthetic examples created only to demonstrate schemas and execution paths. Files in `data/derived/` mirror aggregate or audit-level values already reported in the manuscript.

## Core methodological boundary

The repository mirrors the paper’s asymmetric human–AI knowledge-organization protocol:

1. **Embedding-based semantic mapping**  
   Sentence-transformer embeddings → UMAP → HDBSCAN → c-TF-IDF. This stage contains no generative LLM and produces a provisional semantic scaffold rather than a finding.

2. **Post-cluster LLM-assisted provisional interpretation**  
   The LLM receives only pre-computed cluster evidence and produces bounded labels and summaries. It does **not** create embeddings, determine cluster membership, alter the map, or establish research gaps.

3. **Anchoring-controlled grounded-theory-informed reconstruction**  
   GT reconstruction remains a human interpretive branch. In the reported study, all 412 scholarly publications were coded before the semantic scaffold or provisional LLM interpretations were revealed; a 103-publication subset was additionally double-coded for reliability.

4. **GT–computational alignment and divergence-triggered adjudication**  
   Convergence, complementarity, and divergence are inspected against supporting documents. Divergence triggers document-level reinspection, memoing, and an explicit human decision rather than automatic averaging.

5. **Scaffold-to-claim gate and independent expert audit**  
   A proposition becomes eligible for the audited synthesis only when document-level trace evidence, recorded human adjudication, and independent expert confirmation are present. For research-gap eligibility, the manuscript additionally applies prespecified expert-rating thresholds.

6. **Optional case-bounded transferability probe**  
   The external issue-public module is applied only after the scholarly synthesis has been frozen. It is contingent rather than constitutive and is not used to establish core protocol efficacy, research-gap eligibility, population opinion, or cross-domain transfer. In other domains, a defensible external information environment may instead consist of standards, patents, policy documents, practitioner records, or expert interviews; the protocol may also end after the scholarly gate.

## Manuscript-aligned configuration

The repository intentionally contains **one manuscript configuration file**, `config/paper_config.yaml`, matching the configuration-file scope described in the response letter. It records the principal settings reported in the manuscript:

- primary embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- sensitivity embedding model: `sentence-transformers/all-mpnet-base-v2`
- normalized primary embedding dimension: `384`
- UMAP: `n_neighbors=15`, `min_dist=0.0`, `n_components=5`, `metric=cosine`, `random_state=42`
- HDBSCAN academic corpus: `min_cluster_size=5`, `min_samples=5`, `metric=euclidean`, `cluster_selection_method=eom`
- HDBSCAN external corpus: `min_cluster_size=30`, `min_samples=10`, `metric=euclidean`, `cluster_selection_method=eom`
- c-TF-IDF: top 10 representative terms per pre-computed cluster
- LLM snapshot: `gpt-4o-2024-11-20`
- endpoint / primary run date: `v1/chat/completions` / `2026-06-18`
- temperature / top-p: `0.2 / 0.9`
- primary decoding seed: `42`
- maximum output: `600` tokens
- maximum invalid-JSON retries: `2`
- repeated-run seeds: `11, 23, 42, 67, 89, 101, 131, 167, 191, 223`

The reported stochastic-sensitivity analysis used **20 fixed evidence units × 10 decoding seeds = 200 outputs**, with model snapshot, prompt text, input evidence, temperature, top-p, and maximum-output settings held fixed while only the decoding seed varied.

The measured environment reported in the manuscript used Ubuntu 22.04 LTS, Python 3.11.9, CUDA 12.1, an AMD Ryzen 9 7950X with 64 GB RAM, and an NVIDIA GeForce RTX 4090 with 24 GB VRAM. The public companion records the principal software versions in `config/paper_config.yaml` and `requirements.txt`; exact wall times remain hardware- and access-dependent.

## External acquisition audit artifact

`data/derived/external_acquisition_reported.yaml` mirrors the manuscript’s source-specific acquisition documentation for the optional external probe. It is an **audit artifact**, not a second runtime configuration file. It records:

- observation window: 1 January 2020–31 December 2025;
- fixed Chinese query C1 and English query E1;
- separate acquisition routes for Weibo, Reddit, archived X/Twitter datasets, and public news comments;
- source-level raw, exclusion, and retained counts;
- access dates and versioned acquisition-log identifiers;
- retained-field schema and release exclusions;
- explicit boundary between protocol-level reproducibility and exact-corpus reconstruction.

The source routes are **not probability samples**, and the external corpus is interpreted only as selected-platform issue-public evidence.

## Repository structure

```text
LLM-GT/
├─ .github/workflows/
│  └─ manuscript-alignment.yml
├─ config/
│  └─ paper_config.yaml
├─ data/
│  ├─ README.md
│  ├─ demo/
│  │  ├─ academic_demo.csv
│  │  ├─ public_demo.csv
│  │  ├─ gt_audit_demo.csv
│  │  ├─ gate_demo.csv
│  │  └─ llm_runs_demo.jsonl
│  └─ derived/
│     ├─ workflow_metrics.csv
│     ├─ reference_theme_crosswalk_reported.csv
│     ├─ interpretive_depth.csv
│     ├─ coding_reliability_reported.csv
│     ├─ coder_2x2_reported.csv
│     ├─ llm_stability_reported.csv
│     ├─ runtime_audit_reported.csv
│     ├─ external_acquisition_reported.yaml
│     ├─ public_noise_audit_reported.csv
│     ├─ platform_sensitivity_reported.csv
│     ├─ mechanism_subset_reported.csv
│     ├─ gap_decisions_reported.csv
│     └─ adjudication_outcomes_reported.csv
├─ prompts/
│  ├─ system_prompt.txt
│  └─ user_template.txt
├─ src/
│  ├─ semantic_mapping.py
│  ├─ llm_interpretation.py
│  ├─ stability.py
│  ├─ scaffold_to_claim_gate.py
│  ├─ plot_figure4.py
│  └─ validate_manuscript_alignment.py
├─ requirements.txt
├─ LICENSE
└─ README.md
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 0. Check repository–manuscript alignment

Before using the companion, run:

```bash
python src/validate_manuscript_alignment.py
```

The validator checks the public constants and claim boundaries mirrored from the final manuscript, including:

- the frozen 32-theme denominator and T01–T32 hit/miss crosswalk;
- workflow coverage/precision/F1 values;
- non-equivalent person-time endpoints and the absence of a percentage labor-reduction claim;
- category-level reliability, 2 × 2 coder cells, and interpretive-depth values;
- the 20-unit × 10-seed LLM stability summary;
- three-run runtime aggregates;
- external acquisition totals, public-noise review counts, and platform-sensitivity values;
- the 103-record mechanism analysis;
- the `12 screened → 4 rejected → 8 eligible` gap audit;
- the 20-unit human adjudication totals;
- model, UMAP, HDBSCAN, LLM, and measured-environment constants;
- the repository-shape requirement that `config/paper_config.yaml` is the single configuration file;
- removal of legacy terms that would contradict the revised manuscript.

The GitHub Actions workflow runs this validator automatically on pushes and pull requests. The check deliberately does **not** validate restricted raw corpora, expert judgments, or empirical provenance.

### 1. Semantic mapping demo

```bash
python src/semantic_mapping.py \
  --input data/demo/academic_demo.csv \
  --corpus academic \
  --output outputs/academic_demo_clusters.csv
```

The demo corpus is intentionally small, so its clusters are illustrative rather than manuscript-reproducing. The script does not call a generative LLM and does not convert clusters into final themes or claims.

For a sensitivity run, the embedding model may be overridden explicitly:

```bash
python src/semantic_mapping.py \
  --input data/demo/academic_demo.csv \
  --corpus academic \
  --embedding-model sentence-transformers/all-mpnet-base-v2 \
  --output outputs/academic_demo_clusters_mpnet.csv
```

### 2. Inspect the exact LLM prompt payload without making an API call

The script performs a dry run unless `--execute` is supplied:

```bash
python src/llm_interpretation.py \
  --cluster-id demo_C01 \
  --corpus academic \
  --terms trust shared-control handover recoverability \
  --records "record A" "record B" "record C"
```

The short term list above is intentionally a schema demonstration. The reported study supplied **10 c-TF-IDF terms and three representative de-identified records per unit**. When the supplied term count differs from the paper configuration, the script emits a warning.

To execute an API request, set `OPENAI_API_KEY` and add `--execute`. Generated JSONL records include `unit_id`, `run_id`, seed, model settings, and prompt hashes so that repeated generations can be passed directly into the stability workflow. A later blinded human-review step may append `human_decision` values before decision-invariance analysis.

### 3. Repeated-output stability diagnostics

A synthetic JSONL example is included for code inspection:

```bash
python src/stability.py \
  --input data/demo/llm_runs_demo.jsonl \
  --output outputs/llm_stability_by_unit.csv \
  --summary-output outputs/llm_stability_summary.csv
```

The manuscript-facing primary diagnostics are pairwise provisional-label similarity, unit-level modal agreement, and downstream human-decision invariance when blinded human decisions are available. The script also reports a pooled exact-string Fleiss’ kappa for traceability; because semantic units may have unit-specific label vocabularies, that pooled coefficient is treated as **descriptive** rather than as a conventional cross-unit agreement statistic. Stability does not establish semantic correctness or construct validity.

The manuscript-reported aggregate values are mirrored in `data/derived/llm_stability_reported.csv`:

- academic clusters: 120 outputs, cosine similarity `0.90 ± 0.04`, modal agreement `0.92`, Fleiss’ κ `0.85`, decision invariance `12/12`;
- public-topic families: 80 outputs, cosine similarity `0.86 ± 0.06`, modal agreement `0.87`, Fleiss’ κ `0.78`, decision invariance `7/8`;
- overall: 200 outputs, cosine similarity `0.88 ± 0.05`, modal agreement `0.90`, Fleiss’ κ `0.82`, decision invariance `19/20`.

### 4. Scaffold-to-claim and gap-eligibility gate demo

```bash
python src/scaffold_to_claim_gate.py \
  --input data/demo/gate_demo.csv \
  --output outputs/gate_decisions.csv
```

The checker implements two recorded layers:

1. **Scaffold-to-claim gate:** document trace evidence + recorded human adjudication + independent expert confirmation.
2. **Optional research-gap screen:** when expert-rating columns are supplied, novelty, importance, feasibility, and traceability panel means must each be at least `3.5/5`, and no individual traceability rating may be below `3`.

The checker does not create propositions, judge novelty, or replace expert assessment.

### 5. Regenerate the role-aligned Fig. 4 from reported aggregate values

```bash
python src/plot_figure4.py --output outputs/figure4_role_aligned.png
```

The script mirrors the final manuscript’s comparison logic:

- **Panel A:** coverage, precision, and F1 against the same frozen 32-theme reference inventory;
- **Panel B:** stage-specific recorded person-time with explicitly non-equivalent endpoints;
- **Panel C:** interpretive depth only for GT-containing workflows.

The repository does **not** estimate a percentage labor reduction. In the manuscript, `85.0 h` is the complete GT-only workflow, `2.6 h` is the semantic-mapping stage, `3.5 h` is the mapping-plus-provisional-interpretation stage, and `22.0 h` is additional post-GT integration and adjudication after the corpus-level GT reconstruction was frozen. A standalone total for the full-hybrid workflow is **not reported**.

## Reviewer-facing audit map

| Manuscript issue | Public companion artifact |
|---|---|
| Distinguish clustering from LLM interpretation | `src/semantic_mapping.py`, `src/llm_interpretation.py`, literal prompts |
| BERTopic-family computational scaffold; no algorithmic novelty claim | `src/semantic_mapping.py`, `config/paper_config.yaml` |
| Frozen 32-theme coverage denominator | `data/derived/reference_theme_crosswalk_reported.csv` |
| Role-aligned workflow evaluation | `data/derived/workflow_metrics.csv`, `src/plot_figure4.py` |
| Category-level reliability and depth | `coding_reliability_reported.csv`, `coder_2x2_reported.csv`, `interpretive_depth.csv` |
| LLM stochastic sensitivity | `llm_stability_reported.csv`, `src/stability.py` |
| Computational environment and runtime | `config/paper_config.yaml`, `runtime_audit_reported.csv` |
| Public-corpus acquisition transparency | `data/derived/external_acquisition_reported.yaml` |
| Public HDBSCAN noise review | `data/derived/public_noise_audit_reported.csv` |
| Weibo/platform sensitivity | `platform_sensitivity_reported.csv` |
| Divergence/gate mechanism analysis | `mechanism_subset_reported.csv` |
| Gap qualification | `gap_decisions_reported.csv`, `src/scaffold_to_claim_gate.py` |
| Human adjudication outcomes | `adjudication_outcomes_reported.csv` |

## Data and claim boundaries

- `data/demo/*` contains **synthetic schema examples only**.
- `data/derived/*` contains aggregate or audit-level values already reported in the manuscript.
- No licensed bibliographic record, username, profile information, direct identifier, or verbatim public post is included.
- The repository does not reproduce the empirical corpora from public data alone and does not claim exact-corpus reproducibility where source archives or licensed manifests are inaccessible.
- Computational clusters and provisional LLM labels are not findings.
- The repository does not convert sparse topics into research-gap claims automatically.
- External issue-public results are case-bounded and are not representative estimates of population opinion.
- Repeated-output similarity measures local stability under the fixed reported configuration; it does not establish truth, construct validity, or cross-model stability.
- Recorded person-time values have non-equivalent activity endpoints and are not evidence of a percentage labor reduction.
- The 103-record mechanism comparison uses frozen artifacts and a subset-specific 24-theme denominator; it is reported as mechanism-consistent evidence, not as a new randomized experiment.

## Reproducibility scope

The companion supports **protocol-level and code-path reproducibility** while respecting database licensing, platform terms, privacy constraints, and data minimization. Researchers with access to their own lawful source corpus can replace the synthetic demo files using the documented schemas and rerun the computational and audit logic. Empirical claims in the manuscript remain tied to the reported 412-publication scholarly corpus, the documented expert/coder procedures, and the case-bounded external corpus used in the study.

## License

Code in this repository is released under the MIT License. Synthetic demo data are provided for method illustration only.
