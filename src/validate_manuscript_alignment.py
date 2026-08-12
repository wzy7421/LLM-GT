#!/usr/bin/env python3
"""Validate aggregate repository values against the final manuscript.

This validator intentionally checks only values and boundaries that are already
reported in the manuscript and mirrored in the public companion. It does not
validate restricted raw corpora, expert judgments, or empirical provenance.

Run from the repository root:
    python src/validate_manuscript_alignment.py
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]


def close(actual: float, expected: float, tol: float = 1e-9) -> bool:
    return math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tol)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_workflow_metrics() -> None:
    path = ROOT / "data/derived/workflow_metrics.csv"
    df = pd.read_csv(path).set_index("workflow")

    expected = {
        "GT-only": (23, 32, 27, 71.9, 85.2, 78.0),
        "Semantic map only": (26, 32, 32, 81.3, 81.3, 81.3),
        "Semantic map + LLM": (28, 32, 34, 87.5, 82.4, 84.8),
        "Full hybrid": (30, 32, 33, 93.8, 90.9, 92.3),
    }

    for workflow, values in expected.items():
        require(workflow in df.index, f"Missing workflow row: {workflow}")
        recovered, reference_total, candidates, coverage, precision, f1 = values
        row = df.loc[workflow]
        require(int(row["recovered"]) == recovered, f"{workflow}: recovered mismatch")
        require(int(row["reference_total"]) == reference_total, f"{workflow}: reference_total mismatch")
        require(int(row["candidates"]) == candidates, f"{workflow}: candidates mismatch")
        require(close(row["coverage"], coverage), f"{workflow}: coverage mismatch")
        require(close(row["precision"], precision), f"{workflow}: precision mismatch")
        require(close(row["f1"], f1), f"{workflow}: F1 mismatch")

    require(pd.isna(df.loc["Full hybrid", "recorded_person_hours"]),
            "Full hybrid must not carry a standalone person-time total")
    require(close(df.loc["GT-only", "recorded_person_hours"], 85.0),
            "GT-only person-time must be 85.0 h")
    require(close(df.loc["Semantic map only", "recorded_person_hours"], 2.6),
            "Semantic-map stage must be 2.6 h")
    require(close(df.loc["Semantic map + LLM", "recorded_person_hours"], 3.5),
            "Map + LLM stage must be 3.5 h")

    post = "Post-GT hybrid integration and adjudication"
    require(post in df.index, "Missing post-GT integration/adjudication row")
    require(close(df.loc[post, "recorded_person_hours"], 22.0),
            "Post-GT integration/adjudication must be 22.0 h additional")


def validate_stability() -> None:
    path = ROOT / "data/derived/llm_stability_reported.csv"
    df = pd.read_csv(path).set_index("units")

    expected = {
        "Academic clusters": (120, 0.90, 0.04, 0.92, 0.85, 12, 12),
        "Public topic families": (80, 0.86, 0.06, 0.87, 0.78, 7, 8),
        "Overall": (200, 0.88, 0.05, 0.90, 0.82, 19, 20),
    }

    for label, values in expected.items():
        require(label in df.index, f"Missing stability row: {label}")
        outputs, cosine_mean, cosine_sd, modal, kappa, inv_n, inv_total = values
        row = df.loc[label]
        require(int(row["outputs"]) == outputs, f"{label}: output count mismatch")
        require(close(row["cosine_mean"], cosine_mean), f"{label}: cosine mean mismatch")
        require(close(row["cosine_sd"], cosine_sd), f"{label}: cosine SD mismatch")
        require(close(row["modal_agreement"], modal), f"{label}: modal agreement mismatch")
        require(close(row["fleiss_kappa"], kappa), f"{label}: reported kappa mismatch")
        require(int(row["decision_invariance_n"]) == inv_n, f"{label}: invariance numerator mismatch")
        require(int(row["decision_invariance_total"]) == inv_total, f"{label}: invariance denominator mismatch")


def validate_depth() -> None:
    path = ROOT / "data/derived/interpretive_depth.csv"
    df = pd.read_csv(path).set_index("category")

    require(close(df.loc["Mean", "gt_only"], 4.51), "GT-only mean depth must be 4.51")
    require(close(df.loc["Mean", "full_hybrid"], 4.30), "Full-hybrid mean depth must be 4.30")
    require(close(df.loc["Mean", "delta_hybrid_minus_gt"], -0.21), "Mean depth delta must be -0.21")
    require(close(df.loc["Cognitive collaboration", "delta_hybrid_minus_gt"], -0.9),
            "Cognitive collaboration delta must be -0.9")
    require(close(df.loc["4E cognition/physical AI", "delta_hybrid_minus_gt"], -0.6),
            "4E cognition/physical AI delta must be -0.6")


def validate_config() -> None:
    path = ROOT / "config/paper_config.yaml"
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))

    require(cfg["embedding"]["model"] == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "Embedding model mismatch")
    require(cfg["umap"] == {
        "n_neighbors": 15,
        "min_dist": 0.0,
        "n_components": 5,
        "metric": "cosine",
        "random_state": 42,
    }, "UMAP configuration mismatch")
    require(cfg["hdbscan"]["academic"]["min_cluster_size"] == 5, "Academic min_cluster_size mismatch")
    require(cfg["hdbscan"]["academic"]["min_samples"] == 5, "Academic min_samples mismatch")
    require(cfg["hdbscan"]["public"]["min_cluster_size"] == 30, "External min_cluster_size mismatch")
    require(cfg["hdbscan"]["public"]["min_samples"] == 10, "External min_samples mismatch")
    require(cfg["llm"]["model"] == "gpt-4o-2024-11-20", "LLM snapshot mismatch")
    require(close(cfg["llm"]["temperature"], 0.2), "Temperature mismatch")
    require(close(cfg["llm"]["top_p"], 0.9), "top_p mismatch")
    require(int(cfg["llm"]["seed"]) == 42, "Primary decoding seed mismatch")
    require(int(cfg["llm"]["max_tokens"]) == 600, "Maximum output mismatch")
    require(cfg["llm"]["stochastic_sensitivity_seeds"] == [11, 23, 42, 67, 89, 101, 131, 167, 191, 223],
            "Repeated-run seed list mismatch")
    require(int(cfg["evaluation"]["reference_theme_count"]) == 32, "Reference-theme denominator mismatch")
    require(int(cfg["evaluation"]["academic_record_count"]) == 412, "Academic record count mismatch")
    require(int(cfg["evaluation"]["external_record_count"]) == 34500, "External record count mismatch")


def main() -> None:
    validate_workflow_metrics()
    validate_stability()
    validate_depth()
    validate_config()
    print("PASS: public companion aggregate values and configuration match the final manuscript constants checked here.")
    print("Boundary: this check does not validate restricted raw data, expert judgments, or empirical provenance.")


if __name__ == "__main__":
    main()
