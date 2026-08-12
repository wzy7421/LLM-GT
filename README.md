# LLM-GT

Reproducibility companion for the manuscript **“Human-in-the-Loop Knowledge Organization for Interdisciplinary Synthesis: Semantic Mapping, LLM-Assisted Interpretation, and Grounded Theory.”**

## Purpose

This repository provides a **schema-compatible, executable companion** for the computational and audit components described in the manuscript. Its purpose is to make the workflow, configuration, prompt structure, role-aligned evaluation logic, repeated-run stability diagnostics, scaffold-to-claim gate, and aggregate figure generation inspectable without redistributing licensed academic metadata or restricted user-generated records.

The repository is **not** a replacement for the manuscript and does not contain the empirical 412-publication scholarly corpus or the 34,500-text external issue-public corpus. Files in `data/demo/` are synthetic examples created only to demonstrate schemas and execution paths. Files in `data/derived/` contain aggregate values already reported in the manuscript.

## Manuscript-aligned methodological structure

The repository mirrors the paper’s asymmetric human–AI knowledge-organization protocol:

1. **Embedding-based semantic mapping**  
   Sentence-transformer embeddings → UMAP → HDBSCAN → c-TF-IDF. This stage contains no generative LLM and produces a provisional semantic scaffold rather than a finding.

2. **Post-cluster LLM-assisted provisional interpretation**  
   The LLM receives only pre-computed cluster evidence and produces bounded labels and summaries. It does **not** create embeddings, determine cluster membership, alter the map, or establish research gaps.

3. **Anchoring-controlled grounded-theory-informed reconstruction**  
   GT reconstruction remains a human interpretive branch. In the reported study, all 412 scholarly publications were coded before the semantic scaffold or provisional LLM labels were revealed; a 103-publication subset was additionally double-coded for reliability.

4. **GT–computational alignment and divergence-triggered adjudication**  
   Convergence, complementarity, and divergence are inspected against supporting documents. Divergence triggers document-level reinspection, memoing, and an explicit human decision rather than automatic averaging.

5. **Scaffold-to-claim gate and independent expert audit**  
   A proposition is eligible for the audited synthesis only when document-level trace evidence, recorded human adjudication, and independent expert confirmation are all present.

6. **Optional case-bounded transferability probe**  
   The external issue-public module is applied only after the scholarly synthesis has been frozen. It is contingent rather than constitutive and is not used to establish core protocol efficacy, research-gap eligibility, population opinion, or cross-domain transfer. In other domains, a defensible external information environment may instead consist of standards, patents, policy documents, practitioner records, or expert interviews; the protocol may also end after the scholarly gate.

## Paper-aligned configuration

`config/paper_config.yaml` records the main settings reported in the manuscript:

- embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- normalized embedding dimension: 384
- UMAP: `n_neighbors=15`, `min_dist=0.0`, `n_components=5`, `metric=cosine`, `random_state=42`
- HDBSCAN academic corpus: `min_cluster_size=5`, `min_samples=5`, `metric=euclidean`, `cluster_selection_method=eom`
- HDBSCAN external corpus: `min_cluster_size=30`, `min_samples=10`, `metric=euclidean`, `cluster_selection_method=eom`
- c-TF-IDF: top 10 representative terms per pre-computed cluster
- LLM snapshot: `gpt-4o-2024-11-20`
- temperature: `0.2`
- top-p: `0.9`
- primary decoding seed: `42`
- maximum output: `600` tokens
- maximum invalid-JSON retries: `2`
- repeated-run decoding seeds: `11, 23, 42, 67, 89, 101, 131, 167, 191, 223`

The reported stochastic-sensitivity analysis used **20 fixed evidence units × 10 decoding seeds = 200 outputs**, with model snapshot, prompt text, input evidence, temperature, top-p, and maximum-output settings held fixed while only the decoding seed varied.

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

The demo corpus is intentionally small, so its clusters are illustrative rather than manuscript-reproducing. The semantic-mapping script does not call a generative LLM and does not convert clusters into final themes or claims.

### 2. Inspect the exact LLM prompt payload without making an API call

The script performs a dry run unless `--execute` is supplied:

```bash
python src/llm_interpretation.py \
  --cluster-id demo_C01 \
  --corpus academic \
  --terms trust shared-control handover recoverability \
  --records "record A" "record B" "record C"
```

To execute an API request, set `OPENAI_API_KEY` and add `--execute`. The script uses the model/configuration declared in `config/paper_config.yaml` unless a decoding seed is explicitly overridden.

### 3. Repeated-output stability diagnostics

A synthetic JSONL example is included for code inspection:

```bash
python src/stability.py \
  --input data/demo/llm_runs_demo.jsonl \
  --output outputs/llm_stability_by_unit.csv \
  --summary-output outputs/llm_stability_summary.csv
```

The manuscript-facing primary diagnostics are pairwise provisional-label similarity, unit-level modal agreement, and downstream human-decision invariance. The script also reports a pooled exact-string Fleiss’ kappa for traceability; because semantic units may have unit-specific label vocabularies, that pooled coefficient is treated as descriptive rather than as a conventional cross-unit agreement statistic. Stability does not establish semantic correctness or construct validity.

The aggregate values reported in the manuscript are stored in `data/derived/llm_stability_reported.csv`:

- academic clusters: 120 outputs, cosine similarity `0.90 ± 0.04`, modal agreement `0.92`, Fleiss’ κ `0.85`, decision invariance `12/12`;
- public-topic families: 80 outputs, cosine similarity `0.86 ± 0.06`, modal agreement `0.87`, Fleiss’ κ `0.78`, decision invariance `7/8`;
- overall: 200 outputs, cosine similarity `0.88 ± 0.05`, modal agreement `0.90`, Fleiss’ κ `0.82`, decision invariance `19/20`.

### 4. Scaffold-to-claim gate demo

```bash
python src/scaffold_to_claim_gate.py \
  --input data/demo/gate_demo.csv \
  --output outputs/gate_decisions.csv
```

This checker does not generate or judge research gaps. It only checks whether the three manuscript-defined audit requirements have been recorded. A plausible LLM label, semantic proximity, or cluster sparsity alone cannot satisfy the gate.

### 5. Regenerate the role-aligned Fig. 4 from reported aggregate values

```bash
python src/plot_figure4.py --output outputs/figure4_role_aligned.png
```

The script mirrors the final manuscript’s comparison logic:

- **Panel A:** coverage, precision, and F1 against the same frozen 32-theme reference inventory;
- **Panel B:** stage-specific recorded person-time with explicitly non-equivalent endpoints;
- **Panel C:** interpretive depth only for GT-containing workflows.

The repository does **not** estimate a percentage labor reduction. In the manuscript, `85.0 h` is the complete GT-only workflow, `2.6 h` is the semantic-mapping stage, `3.5 h` is the mapping-plus-provisional-interpretation stage, and `22.0 h` is additional post-GT integration and adjudication after the corpus-level GT reconstruction was frozen. A standalone total for the full-hybrid workflow is **not reported**.

## Aggregate manuscript values

`data/derived/workflow_metrics.csv` reproduces the role-aligned workflow results against the frozen 32-theme reference inventory:

- GT-only: `23/32` recovered (`71.9%`), precision `85.2%`, F1 `78.0%`;
- semantic map only: `26/32` (`81.3%`), precision/F1 `81.3%`;
- semantic map + LLM: `28/32` (`87.5%`), precision `82.4%`, F1 `84.8%`;
- full hybrid: `30/32` (`93.8%`), precision `90.9%`, F1 `92.3%`.

`data/derived/interpretive_depth.csv` reproduces the seven-category GT-only versus full-hybrid depth profile, including the reported decreases in cognitive collaboration (`4.8 → 3.9`) and 4E cognition/physical AI (`4.6 → 4.0`) and the pooled means (`4.51 → 4.30`).

## Data and claim boundaries

- `data/demo/*` contains synthetic schema examples only.
- `data/derived/*` contains aggregate values already reported in the manuscript.
- No licensed bibliographic record, username, profile information, direct identifier, or verbatim public post is included.
- The repository does not reproduce the empirical corpora from public data alone and does not claim exact-corpus reproducibility where source archives or licensed manifests are inaccessible.
- Computational clusters and provisional LLM labels are not findings.
- The repository does not convert sparse topics into research-gap claims automatically.
- External issue-public results are case-bounded and are not representative estimates of population opinion.
- Repeated-output similarity measures local stability under the fixed reported configuration; it does not establish truth, construct validity, or cross-model stability.
- Recorded person-time values have non-equivalent activity endpoints and are not evidence of a percentage labor reduction.

## Reproducibility scope

The companion supports **protocol-level and code-path reproducibility** while respecting database licensing, platform terms, privacy constraints, and data minimization. Researchers with access to their own lawful source corpus can replace the synthetic demo files using the documented schemas and rerun the computational and audit logic. Empirical claims in the manuscript remain tied to the reported 412-publication scholarly corpus, the documented expert/coder procedures, and the case-bounded external corpus used in the study.

## License

Code in this repository is released under the MIT License. Synthetic demo data are provided for method illustration only.
