# LLM-GT

Reproducibility companion for the manuscript **“Human-in-the-Loop Knowledge Organization for Interdisciplinary Synthesis: Integrating Embedding-Based Semantic Mapping, LLM-Assisted Interpretation, and Grounded Theory.”**

## Purpose

This repository provides a **schema-compatible, executable demonstration** of the computational and audit components described in the manuscript. It is intended to make the workflow, configuration, prompt structure, evaluation logic, stability diagnostics, scaffold-to-claim gate, and figure generation inspectable without redistributing licensed academic metadata or user-generated public-discourse data.

**Important:** the files in `data/demo/` are synthetic examples created only to illustrate the data schema and execution path. They are **not** the 412-paper scholarly corpus or the 34,500-text external corpus used in the study, and they must not be used to reproduce the manuscript's empirical claims.

Derived aggregate values reported in the manuscript are provided separately in `data/derived/` so that figures and summary tables can be regenerated without exposing restricted source records.

## Methodological structure

The repository mirrors the manuscript's asymmetric human–AI design:

1. **Embedding-based semantic mapping**  
   Sentence-transformer embeddings → UMAP → HDBSCAN → c-TF-IDF.
2. **LLM-assisted provisional interpretation**  
   The LLM receives only pre-computed cluster evidence and produces bounded labels/summaries. It does **not** create clusters or final themes.
3. **Anchoring-controlled GT reconstruction**  
   GT coding remains a human interpretive branch. A small synthetic coding ledger is included only to demonstrate the expected audit schema.
4. **GT–computational alignment and divergence adjudication**  
   Convergence, complementarity, and divergence are recorded as explicit human decisions.
5. **Independent expert audit and scaffold-to-claim gate**  
   Machine-assisted outputs remain provisional unless document-level trace evidence, recorded human adjudication, and independent expert confirmation are all present.
6. **Optional external triangulation**  
   Public-discourse analysis is treated as a boundary-sensitivity extension, not as evidence of core workflow efficacy or population opinion.

## Paper-aligned configuration

The publication configuration in `config/paper_config.yaml` records the settings described in the manuscript:

- embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- UMAP: `n_neighbors=15`, `min_dist=0.0`, `n_components=5`, `metric=cosine`, `random_state=42`
- HDBSCAN academic corpus: `min_cluster_size=5`, `min_samples=5`, `metric=euclidean`, `cluster_selection_method=eom`
- HDBSCAN external corpus: `min_cluster_size=30`, `min_samples=10`
- c-TF-IDF: top 10 representative terms per cluster
- LLM snapshot recorded in the manuscript: `gpt-4o-2024-11-20`
- temperature: `0.2`; top_p: `0.9`; seed: `42`; max output: `600` tokens

The repository also records a set of **optional varying seeds** for a reviewer-facing stochastic-sensitivity extension. These seeds are not manuscript results by themselves. If this extension is run, the resulting metrics should be recomputed and the manuscript updated before they are reported.

## Repository structure

```text
LLM-GT/
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
│     ├─ interpretive_depth.csv
│     └─ llm_stability_reported.csv
├─ prompts/
│  ├─ system_prompt.txt
│  └─ user_template.txt
├─ src/
│  ├─ semantic_mapping.py
│  ├─ llm_interpretation.py
│  ├─ stability.py
│  ├─ scaffold_to_claim_gate.py
│  └─ plot_figure4.py
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

### 1. Semantic mapping demo

```bash
python src/semantic_mapping.py \
  --input data/demo/academic_demo.csv \
  --corpus academic \
  --output outputs/academic_demo_clusters.csv
```

The demo corpus is intentionally small, so its clusters are illustrative rather than manuscript-reproducing.

### 2. Inspect the exact LLM prompt payload without making an API call

The script is a dry run unless `--execute` is supplied:

```bash
python src/llm_interpretation.py \
  --cluster-id demo_C01 \
  --corpus academic \
  --terms trust shared-control handover recoverability \
  --records "record A" "record B" "record C"
```

To execute an API request, set `OPENAI_API_KEY` and add `--execute`. The script then uses the model/configuration declared in `config/paper_config.yaml` unless the seed is overridden.

A varying-seed robustness run can be produced by repeating the command with the seeds recorded under `llm.stochastic_sensitivity_seeds` in the configuration file and saving each output to a JSONL ledger.

### 3. Repeated-output stability analysis

A synthetic JSONL example is included:

```bash
python src/stability.py \
  --input data/demo/llm_runs_demo.jsonl \
  --output outputs/llm_stability_by_unit.csv
```

The script reports label-similarity, modal agreement, Fleiss' kappa, and downstream human-decision invariance. These are stability diagnostics, not evidence that a provisional label is true.

### 4. Scaffold-to-claim gate demo

```bash
python src/scaffold_to_claim_gate.py \
  --input data/demo/gate_demo.csv \
  --output outputs/gate_decisions.csv
```

This checker does not create or judge research gaps. It only tests whether the three manuscript-defined audit requirements have been recorded.

### 5. Regenerate revised Fig. 4

```bash
python src/plot_figure4.py --output outputs/figure4_role_aligned.png
```

This figure uses only manuscript-level aggregate values from `data/derived/`.

## Data and claim boundaries

- `data/demo/*` = synthetic schema examples only.
- `data/derived/*` = aggregate values already reported in the manuscript.
- No licensed bibliographic record, user identifier, profile text, or verbatim public post is included.
- The repository does not convert computational topics into research-gap claims automatically.
- LLM outputs remain provisional until human audit requirements are met.
- Repeated LLM output similarity indicates repeatability/stability, not truth or construct validity.

## Reproducibility note

The code is intended to make the **pipeline and audit logic** reproducible while respecting database licensing, platform terms, and re-identification constraints. Researchers with access to their own lawful source corpus can replace the synthetic demo CSVs using the documented schemas.

## License

Code in this repository is released under the MIT License. Synthetic demo data are provided for method illustration only.
