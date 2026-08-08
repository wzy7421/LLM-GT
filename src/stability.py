#!/usr/bin/env python3
"""Repeated-output stability diagnostics for provisional LLM labels.

Expected JSONL fields per line:
  unit_id, run_id, provisional_label, human_decision
Optional fields:
  seed, corpus

This script reports wording-level label similarity, modal-label agreement,
Fleiss' kappa, and downstream decision invariance. These diagnostics measure
repeatability/stability, not truth or construct validity.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_label(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def mean_pairwise_similarity(labels: list[str]) -> float:
    if len(labels) < 2:
        return 1.0
    X = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(labels)
    sim = cosine_similarity(X)
    tri = sim[np.triu_indices_from(sim, k=1)]
    return float(tri.mean()) if len(tri) else 1.0


def modal_agreement(labels: list[str]) -> float:
    normalized = [normalize_label(x) for x in labels]
    return Counter(normalized).most_common(1)[0][1] / len(normalized)


def fleiss_kappa(count_matrix: np.ndarray) -> float:
    """Compute Fleiss' kappa from an N-items x K-categories count matrix."""
    n_items, _ = count_matrix.shape
    n_raters = count_matrix.sum(axis=1)
    if not np.all(n_raters == n_raters[0]):
        raise ValueError("Fleiss' kappa requires the same number of ratings per item")
    n = float(n_raters[0])
    if n <= 1:
        return float("nan")

    p_j = count_matrix.sum(axis=0) / (n_items * n)
    p_i = ((count_matrix ** 2).sum(axis=1) - n) / (n * (n - 1))
    p_bar = p_i.mean()
    p_e = (p_j ** 2).sum()
    if np.isclose(1 - p_e, 0):
        return 1.0
    return float((p_bar - p_e) / (1 - p_e))


def read_jsonl(path: str) -> pd.DataFrame:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    df = pd.DataFrame(rows)
    required = {"unit_id", "run_id", "provisional_label", "human_decision"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required JSONL fields: {sorted(missing)}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    df = read_jsonl(args.input)
    summaries = []

    all_normalized = sorted({normalize_label(x) for x in df["provisional_label"]})
    label_to_idx = {label: i for i, label in enumerate(all_normalized)}
    count_rows = []

    for unit_id, group in df.groupby("unit_id", sort=True):
        labels = group["provisional_label"].astype(str).tolist()
        decisions = group["human_decision"].astype(str).tolist()
        normalized = [normalize_label(x) for x in labels]

        counts = np.zeros(len(all_normalized), dtype=int)
        for label in normalized:
            counts[label_to_idx[label]] += 1
        count_rows.append(counts)

        summaries.append(
            {
                "unit_id": unit_id,
                "n_runs": len(group),
                "mean_pairwise_label_similarity": mean_pairwise_similarity(labels),
                "modal_label_agreement": modal_agreement(labels),
                "decision_invariant": len(set(decisions)) == 1,
                "unique_labels": len(set(normalized)),
                "unique_decisions": len(set(decisions)),
            }
        )

    summary_df = pd.DataFrame(summaries)
    kappa = fleiss_kappa(np.vstack(count_rows)) if count_rows else float("nan")

    overall = {
        "units": int(summary_df.shape[0]),
        "outputs": int(df.shape[0]),
        "mean_unit_pairwise_similarity": float(summary_df["mean_pairwise_label_similarity"].mean()),
        "sd_unit_pairwise_similarity": float(summary_df["mean_pairwise_label_similarity"].std(ddof=1)),
        "mean_modal_agreement": float(summary_df["modal_label_agreement"].mean()),
        "fleiss_kappa_exact_normalized_labels": kappa,
        "decision_invariance_n": int(summary_df["decision_invariant"].sum()),
        "decision_invariance_total": int(summary_df.shape[0]),
    }

    print(json.dumps(overall, indent=2))

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(path, index=False)
        print(f"Per-unit diagnostics saved to {path}")


if __name__ == "__main__":
    main()
