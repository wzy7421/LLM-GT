#!/usr/bin/env python3
"""Repeated-output diagnostics for provisional post-cluster LLM labels.

Required JSONL fields per line:
  unit_id, run_id, provisional_label
Optional fields:
  seed, corpus, human_decision

Primary manuscript-facing diagnostics are:
  - mean pairwise label similarity within each fixed evidence unit,
  - unit-level modal-label agreement,
  - downstream human-decision invariance when blinded human decisions are present.

A pooled exact-string Fleiss' kappa is also calculated for traceability when a
count matrix can be formed. Because different semantic units may have
unit-specific label vocabularies, that pooled coefficient should be treated as
descriptive rather than as a conventional cross-unit agreement statistic.
None of these diagnostics establishes semantic correctness or construct
validity.
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
    normalized = [normalize_label(x) for x in labels]
    if len(set(normalized)) == 1:
        return 1.0
    X = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(normalized)
    sim = cosine_similarity(X)
    tri = sim[np.triu_indices_from(sim, k=1)]
    return float(tri.mean()) if len(tri) else 1.0


def modal_agreement(labels: list[str]) -> float:
    normalized = [normalize_label(x) for x in labels]
    return Counter(normalized).most_common(1)[0][1] / len(normalized)


def fleiss_kappa(count_matrix: np.ndarray) -> float:
    """Compute Fleiss' kappa from an N-items x K-categories count matrix."""
    if count_matrix.size == 0:
        return float("nan")
    n_items, _ = count_matrix.shape
    n_raters = count_matrix.sum(axis=1)
    if not np.all(n_raters == n_raters[0]):
        raise ValueError("Fleiss' kappa requires the same number of ratings per item")
    n = float(n_raters[0])
    if n <= 1:
        return float("nan")

    p_j = count_matrix.sum(axis=0) / (n_items * n)
    p_i = ((count_matrix**2).sum(axis=1) - n) / (n * (n - 1))
    p_bar = p_i.mean()
    p_e = (p_j**2).sum()
    if np.isclose(1 - p_e, 0):
        return 1.0
    return float((p_bar - p_e) / (1 - p_e))


def read_jsonl(path: str) -> pd.DataFrame:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    df = pd.DataFrame(rows)
    required = {"unit_id", "run_id", "provisional_label"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required JSONL fields: {sorted(missing)}")
    if df.empty:
        raise ValueError("Input JSONL contains no records")
    return df


def per_unit_summary(df: pd.DataFrame) -> pd.DataFrame:
    summaries = []
    decision_available = "human_decision" in df.columns

    for unit_id, group in df.groupby("unit_id", sort=True):
        labels = group["provisional_label"].astype(str).tolist()
        normalized = [normalize_label(x) for x in labels]
        corpus = group["corpus"].iloc[0] if "corpus" in group.columns else "unspecified"

        decision_invariant: bool | None = None
        unique_decisions: int | None = None
        if decision_available:
            decision_series = group["human_decision"].dropna().astype(str)
            if len(decision_series) == len(group):
                decision_invariant = len(set(decision_series.tolist())) == 1
                unique_decisions = len(set(decision_series.tolist()))

        summaries.append(
            {
                "unit_id": unit_id,
                "corpus": corpus,
                "n_runs": len(group),
                "mean_pairwise_label_similarity": mean_pairwise_similarity(labels),
                "modal_label_agreement": modal_agreement(labels),
                "decision_invariant": decision_invariant,
                "unique_labels": len(set(normalized)),
                "unique_decisions": unique_decisions,
            }
        )
    return pd.DataFrame(summaries)


def descriptive_exact_string_kappa(df: pd.DataFrame) -> float:
    all_normalized = sorted({normalize_label(x) for x in df["provisional_label"]})
    if not all_normalized:
        return float("nan")
    label_to_idx = {label: i for i, label in enumerate(all_normalized)}
    count_rows = []
    for _, group in df.groupby("unit_id", sort=True):
        counts = np.zeros(len(all_normalized), dtype=int)
        for value in group["provisional_label"].astype(str):
            counts[label_to_idx[normalize_label(value)]] += 1
        count_rows.append(counts)
    return fleiss_kappa(np.vstack(count_rows)) if count_rows else float("nan")


def aggregate_block(df: pd.DataFrame, summary_df: pd.DataFrame, label: str) -> dict:
    kappa = descriptive_exact_string_kappa(df)

    decision_values = summary_df["decision_invariant"].dropna()
    decision_n = int(decision_values.astype(bool).sum()) if len(decision_values) else pd.NA
    decision_total = int(len(decision_values)) if len(decision_values) else pd.NA

    return {
        "units": label,
        "outputs": int(df.shape[0]),
        "cosine_mean": float(summary_df["mean_pairwise_label_similarity"].mean()),
        "cosine_sd": float(summary_df["mean_pairwise_label_similarity"].std(ddof=1))
        if len(summary_df) > 1
        else 0.0,
        "modal_agreement": float(summary_df["modal_label_agreement"].mean()),
        "fleiss_kappa": kappa,
        "decision_invariance_n": decision_n,
        "decision_invariance_total": decision_total,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default=None, help="Optional per-unit CSV output")
    parser.add_argument("--summary-output", default=None, help="Optional aggregate manuscript-style CSV output")
    args = parser.parse_args()

    df = read_jsonl(args.input)
    summary_df = per_unit_summary(df)

    blocks: list[dict] = []
    if "corpus" in df.columns:
        corpus_values = set(df["corpus"].astype(str))
        corpus_order = [x for x in ["academic", "public"] if x in corpus_values]
        corpus_order += [x for x in sorted(corpus_values) if x not in corpus_order]
        display = {"academic": "Academic clusters", "public": "Public topic families"}
        for corpus in corpus_order:
            raw_subset = df[df["corpus"].astype(str) == corpus]
            unit_subset = summary_df[summary_df["corpus"].astype(str) == corpus]
            blocks.append(aggregate_block(raw_subset, unit_subset, display.get(corpus, corpus)))

    blocks.append(aggregate_block(df, summary_df, "Overall"))
    aggregate_df = pd.DataFrame(blocks)

    print(aggregate_df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(
        "\nInterpretation boundary: pairwise similarity and modal agreement measure local wording repeatability. "
        "Decision invariance is calculated only when every run for a unit has a blinded human_decision value. "
        "The pooled exact-string Fleiss' kappa is descriptive because semantic units may not share a prespecified nominal label set."
    )

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(path, index=False)
        print(f"Per-unit diagnostics saved to {path}")

    if args.summary_output:
        path = Path(args.summary_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        aggregate_df.to_csv(path, index=False)
        print(f"Aggregate diagnostics saved to {path}")


if __name__ == "__main__":
    main()
