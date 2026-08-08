# LLM-GT

Reproducibility companion for the manuscript **“Human-in-the-Loop Knowledge Organization for Interdisciplinary Synthesis: Integrating Embedding-Based Semantic Mapping, LLM-Assisted Interpretation, and Grounded Theory.”**

## Purpose

This repository provides a **schema-compatible, executable demonstration** of the computational parts of the manuscript. It is intended to make the workflow, configuration, prompt structure, evaluation logic, and figure generation inspectable without redistributing licensed academic metadata or user-generated public-discourse data.

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
   Machine-assisted outputs remain provisional unless trace evidence, recorded adjudication, and expert confirmation are present.
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

The repository also includes an **optional varying-seed stochastic-sensitivity mode**. This is provided as an extension for reviewer-facing robustness analysis and should not be described as a manuscript result unless it is actually run and the manuscript values are updated.

## Repository structure

```text
LLM-GT/
├─ config/
│  └─ paper_config.yaml
├─ data/
│  ├─ demo/
│  │  ├─ academic_demo.csv
│  │  ├─ public_demo.csv
│  │  └─ gt_audit_demo.csv
│  └─ derived/
│     ├─ workflow_metrics.csv
│     └─ interpretive_depth.csv
├─ prompts/
│  ├─ system_prompt.txt
│  └─ user_template.txt
├─ src/
│  ├─ semantic_mapping.py
│  ├─ llm_interpretation.py
│  ├─ stability.py
│  └─ plot_figure4.py
├─ requirements.txt
└─ README.md
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the semantic-mapping demonstration:

```bash
python src/semantic_mapping.py --input data/demo/academic_demo.csv --corpus academic --output outputs/academic_demo_clusters.csv
```

Inspect the exact LLM prompt payload without making an API call:

```bash
python src/llm_interpretation.py --cluster-id demo_C01 --terms "trust, shared control, handover, recoverability" --records "record A" "record B" "record C" --dry-run
```

If an API key is available, remove `--dry-run`. The script uses the model/configuration declared in `config/paper_config.yaml` unless overridden.

Run repeated-output stability analysis on saved JSONL outputs:

```bash
python src/stability.py --input outputs/llm_runs.jsonl
```

Regenerate the revised Fig. 4 from manuscript-level aggregate results:

```bash
python src/plot_figure4.py --output outputs/figure4_role_aligned.png
```

## Data and claim boundaries

- `data/demo/*` = synthetic schema examples only.
- `data/derived/*` = aggregate values already reported in the manuscript.
- No licensed bibliographic record, user identifier, profile text, or verbatim public post is included.
- The repository does not convert computational topics into research-gap claims automatically.
- Repeated LLM output similarity indicates repeatability/stability, not truth or construct validity.

## Reproducibility note

The code is intended to make the **pipeline and audit logic** reproducible while respecting database licensing, platform terms, and re-identification constraints. Researchers with access to their own lawful source corpus can replace the synthetic demo CSVs using the documented schemas.

## License

Code in this repository is released under the MIT License. Synthetic demo data are provided for method illustration only.
