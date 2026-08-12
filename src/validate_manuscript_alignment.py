#!/usr/bin/env python3
"""Validate public companion constants against the final manuscript.

This validator checks only values and boundaries explicitly mirrored from the
manuscript into this public companion. It does not validate restricted raw
corpora, expert judgments, or empirical provenance.

Run from the repository root:
    python src/validate_manuscript_alignment.py
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
FINAL_TITLE = (
    "Human-in-the-Loop Knowledge Organization for Interdisciplinary Synthesis: "
    "Semantic Mapping, LLM-Assisted Interpretation, and Grounded Theory"
)


def close(actual: float, expected: float, tol: float = 1e-9) -> bool:
    return math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tol)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_workflow_metrics() -> None:
    df = pd.read_csv(ROOT / "data/derived/workflow_metrics.csv").set_index("workflow")
    expected = {
        "GT-only": (23, 32, 27, 71.9, 85.2, 78.0),
        "Semantic map only": (26, 32, 32, 81.3, 81.3, 81.3),
        "Semantic map + LLM": (28, 32, 34, 87.5, 82.4, 84.8),
        "Full hybrid": (30, 32, 33, 93.8, 90.9, 92.3),
    }
    for workflow, values in expected.items():
        require(workflow in df.index, f"Missing workflow row: {workflow}")
        recovered, total, candidates, coverage, precision, f1 = values
        row = df.loc[workflow]
        require(int(row["recovered"]) == recovered, f"{workflow}: recovered mismatch")
        require(int(row["reference_total"]) == total, f"{workflow}: denominator mismatch")
        require(int(row["candidates"]) == candidates, f"{workflow}: candidate mismatch")
        require(close(row["coverage"], coverage), f"{workflow}: coverage mismatch")
        require(close(row["precision"], precision), f"{workflow}: precision mismatch")
        require(close(row["f1"], f1), f"{workflow}: F1 mismatch")

    require(pd.isna(df.loc["Full hybrid", "recorded_person_hours"]),
            "Full hybrid must not carry a standalone person-time total")
    require(str(df.loc["Full hybrid", "time_endpoint"]) == "Standalone total not reported",
            "Full hybrid time endpoint boundary mismatch")
    require(close(df.loc["GT-only", "recorded_person_hours"], 85.0), "GT-only time mismatch")
    require(close(df.loc["Semantic map only", "recorded_person_hours"], 2.6), "Mapping-stage time mismatch")
    require(close(df.loc["Semantic map + LLM", "recorded_person_hours"], 3.5), "Map+LLM time mismatch")

    post = "Post-GT hybrid integration and adjudication"
    require(post in df.index, "Missing post-GT integration/adjudication row")
    require(close(df.loc[post, "recorded_person_hours"], 22.0), "Post-GT additional time mismatch")
    require(str(df.loc[post, "time_endpoint"]) == "Additional after frozen corpus-level GT reconstruction",
            "Post-GT endpoint boundary mismatch")


def validate_reference_crosswalk() -> None:
    df = pd.read_csv(ROOT / "data/derived/reference_theme_crosswalk_reported.csv")
    require(len(df) == 32, "Reference-theme crosswalk must contain T01-T32")
    require(df["id"].tolist() == [f"T{i:02d}" for i in range(1, 33)], "Theme IDs must be T01-T32 in order")
    expected_hits = {
        "gt_only": 23,
        "semantic_map": 26,
        "map_plus_llm": 28,
        "full_hybrid": 30,
    }
    for col, expected in expected_hits.items():
        values = df[col].astype(str).str.strip().str.lower()
        require(set(values).issubset({"yes", "no"}), f"{col}: hit/miss values must be Yes/No")
        require(int((values == "yes").sum()) == expected, f"{col}: recovered-theme count mismatch")


def validate_stability() -> None:
    df = pd.read_csv(ROOT / "data/derived/llm_stability_reported.csv").set_index("units")
    expected = {
        "Academic clusters": (120, 0.90, 0.04, 0.92, 0.85, 12, 12),
        "Public topic families": (80, 0.86, 0.06, 0.87, 0.78, 7, 8),
        "Overall": (200, 0.88, 0.05, 0.90, 0.82, 19, 20),
    }
    for label, values in expected.items():
        outputs, cosine_mean, cosine_sd, modal, kappa, inv_n, inv_total = values
        row = df.loc[label]
        require(int(row["outputs"]) == outputs, f"{label}: output count mismatch")
        require(close(row["cosine_mean"], cosine_mean), f"{label}: cosine mean mismatch")
        require(close(row["cosine_sd"], cosine_sd), f"{label}: cosine SD mismatch")
        require(close(row["modal_agreement"], modal), f"{label}: modal agreement mismatch")
        require(close(row["fleiss_kappa"], kappa), f"{label}: reported descriptive kappa mismatch")
        require(int(row["decision_invariance_n"]) == inv_n, f"{label}: invariance numerator mismatch")
        require(int(row["decision_invariance_total"]) == inv_total, f"{label}: invariance denominator mismatch")


def validate_reliability_and_depth() -> None:
    rel = pd.read_csv(ROOT / "data/derived/coding_reliability_reported.csv").set_index("core_category")
    require(close(rel.loc["Cognitive collaboration", "cohen_kappa"], 0.68), "Cognitive collaboration kappa mismatch")
    require(close(rel.loc["4E cognition/physical AI", "cohen_kappa"], 0.71), "4E kappa mismatch")
    require(close(rel.loc["Safety/ethics/accessibility", "cohen_kappa"], 0.85), "Safety/access kappa mismatch")
    require(close(rel.loc["Pooled / mean", "cohen_kappa"], 0.78), "Pooled kappa mismatch")
    require(close(rel.loc["Pooled / mean", "gt_depth_mean"], 4.51), "GT mean depth mismatch")
    require(close(rel.loc["Pooled / mean", "hybrid_depth_mean"], 4.30), "Hybrid mean depth mismatch")
    require(close(rel.loc["Cognitive collaboration", "delta_hybrid_minus_gt"], -0.9), "Cognitive depth delta mismatch")
    require(close(rel.loc["4E cognition/physical AI", "delta_hybrid_minus_gt"], -0.6), "4E depth delta mismatch")

    depth = pd.read_csv(ROOT / "data/derived/interpretive_depth.csv").set_index("category")
    require(close(depth.loc["Mean", "gt_only"], 4.51), "Interpretive-depth GT mean mismatch")
    require(close(depth.loc["Mean", "full_hybrid"], 4.30), "Interpretive-depth hybrid mean mismatch")

    cells = pd.read_csv(ROOT / "data/derived/coder_2x2_reported.csv")
    category_rows = cells[cells["denominator"] == 103]
    require(len(category_rows) == 7, "Coder 2x2 table must contain seven 103-record category rows")
    for _, row in category_rows.iterrows():
        total = int(row["both_present"] + row["coder1_only"] + row["coder2_only"] + row["both_absent"])
        require(total == 103, f"Coder cells do not sum to 103 for {row['core_category']}")
    pooled = cells[cells["core_category"] == "Pooled across 721 decisions"].iloc[0]
    require(int(pooled["denominator"]) == 721, "Pooled coder denominator must be 721")


def validate_runtime() -> None:
    df = pd.read_csv(ROOT / "data/derived/runtime_audit_reported.csv").set_index("stage")
    expected = {
        "Preprocessing": (0.42, 0.03, 21.7, 0.8),
        "Embedding": (3.8, 0.2, 126.0, 4.0),
        "UMAP": (2.6, 0.1, 48.3, 1.9),
        "HDBSCAN": (0.19, 0.01, 4.9, 0.2),
        "c-TF-IDF": (0.12, 0.01, 1.3, 0.1),
        "LLM API": (64.0, 3.0, 43.6, 2.4),
        "Total wall time": (71.1, 3.0, 245.8, 5.8),
    }
    for stage, values in expected.items():
        row = df.loc[stage]
        for col, expected_value in zip(
            ["academic_mean_s", "academic_sd_s", "external_mean_s", "external_sd_s"], values
        ):
            require(close(row[col], expected_value), f"{stage}: {col} mismatch")


def validate_external_probe() -> None:
    cfg = yaml.safe_load((ROOT / "config/external_acquisition.yaml").read_text(encoding="utf-8"))
    require(str(cfg["observation_window"]["start"]) == "2020-01-01", "External observation start mismatch")
    require(str(cfg["observation_window"]["end"]) == "2025-12-31", "External observation end mismatch")
    require(cfg["scope"]["probability_sample"] is False, "External corpus must not be marked as a probability sample")
    require(cfg["scope"]["population_inference_permitted"] is False, "Population inference must remain prohibited")
    require(int(cfg["totals"]["raw_n"]) == 41230, "External raw total mismatch")
    require(int(cfg["totals"]["retained_n"]) == 34500, "External retained total mismatch")
    require(sum(int(v["retained_n"]) for v in cfg["sources"].values()) == 34500, "Source retained counts do not sum to 34,500")

    platform = pd.read_csv(ROOT / "data/derived/platform_sensitivity_reported.csv").set_index("topic")
    totals = platform.loc["Column total"]
    for col in ["weibo", "reddit", "x_twitter", "news", "observed", "equal_platform", "no_weibo"]:
        require(close(totals[col], 100.0), f"Platform-sensitivity column {col} does not sum to 100")
    require(close(platform.loc["Safety/accountability", "observed"], 26.8), "Observed safety prevalence mismatch")
    require(close(platform.loc["Safety/accountability", "no_weibo"], 28.1), "No-Weibo safety prevalence mismatch")


def validate_mechanism_and_gap_audit() -> None:
    mechanism = pd.read_csv(ROOT / "data/derived/mechanism_subset_reported.csv").set_index("condition")
    require(int(mechanism.loc["Divergence + scaffold-to-claim gate", "themes_recovered"]) == 23,
            "Mechanism-condition theme recovery mismatch")
    require(close(mechanism.loc["Divergence + scaffold-to-claim gate", "coverage_percent"], 95.8),
            "Mechanism-condition coverage mismatch")
    require(close(mechanism.loc["Divergence + scaffold-to-claim gate", "decision_trace_completeness_percent"], 100.0),
            "Mechanism-condition trace completeness mismatch")

    gaps = pd.read_csv(ROOT / "data/derived/gap_decisions_reported.csv")
    require(len(gaps) == 12, "Gap audit must contain 12 screened propositions")
    status = gaps["final_status"].astype(str).str.lower()
    require(int((status == "eligible").sum()) == 8, "Gap audit must contain eight eligible propositions")
    require(int((status == "rejected").sum()) == 4, "Gap audit must contain four rejected propositions")

    adjudication = pd.read_csv(ROOT / "data/derived/adjudication_outcomes_reported.csv").set_index("decision")
    require(int(adjudication.loc["Total", "n"]) == 20, "Adjudication total must be 20 interpreted units")
    require(int(adjudication.drop(index="Total")["n"].sum()) == 20, "Adjudication categories must sum to 20")


def validate_config() -> None:
    cfg = yaml.safe_load((ROOT / "config/paper_config.yaml").read_text(encoding="utf-8"))
    require(cfg["manuscript"]["title"] == FINAL_TITLE, "Manuscript title mismatch")
    require(cfg["manuscript"]["previous_reference"] == "IPM-D-26-03845", "Previous reference mismatch")
    require(cfg["manuscript"]["journal"] == "Information Processing & Management", "Journal metadata mismatch")

    embedding = cfg["embedding"]
    require(embedding["model"] == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "Primary embedding mismatch")
    require(embedding["sensitivity_model"] == "sentence-transformers/all-mpnet-base-v2", "Sensitivity embedding mismatch")
    require(int(embedding["output_dimension"]) == 384, "Embedding dimension mismatch")

    require(cfg["umap"] == {
        "n_neighbors": 15, "min_dist": 0.0, "n_components": 5,
        "metric": "cosine", "random_state": 42,
    }, "UMAP configuration mismatch")
    require(cfg["hdbscan"]["academic"]["min_cluster_size"] == 5, "Academic HDBSCAN min_cluster_size mismatch")
    require(cfg["hdbscan"]["academic"]["min_samples"] == 5, "Academic HDBSCAN min_samples mismatch")
    require(cfg["hdbscan"]["public"]["min_cluster_size"] == 30, "External HDBSCAN min_cluster_size mismatch")
    require(cfg["hdbscan"]["public"]["min_samples"] == 10, "External HDBSCAN min_samples mismatch")

    llm = cfg["llm"]
    require(llm["model"] == "gpt-4o-2024-11-20", "LLM snapshot mismatch")
    require(llm["endpoint"] == "v1/chat/completions", "Endpoint mismatch")
    require(str(llm["primary_run_date"]) == "2026-06-18", "Primary run date mismatch")
    require(llm["client_sdk"] == "openai==1.35.13", "OpenAI SDK mismatch")
    require(close(llm["temperature"], 0.2) and close(llm["top_p"], 0.9), "Decoding parameter mismatch")
    require(int(llm["seed"]) == 42 and int(llm["max_tokens"]) == 600, "Primary LLM seed/token mismatch")
    require(int(llm["max_json_retries"]) == 2, "Invalid-JSON retry rule mismatch")
    require(llm["stochastic_sensitivity_seeds"] == [11, 23, 42, 67, 89, 101, 131, 167, 191, 223],
            "Repeated-run seed list mismatch")

    env = cfg["measured_environment"]
    require(env["operating_system"] == "Ubuntu 22.04 LTS", "OS metadata mismatch")
    require(env["cpu"] == "AMD Ryzen 9 7950X" and int(env["system_ram_gb"]) == 64, "CPU/RAM metadata mismatch")
    require(env["gpu"] == "NVIDIA GeForce RTX 4090" and int(env["vram_gb"]) == 24, "GPU/VRAM metadata mismatch")
    require(str(env["python"]) == "3.11.9" and str(env["cuda"]) == "12.1", "Python/CUDA metadata mismatch")
    require(str(env["pytorch"]) == "2.3.1+cu121", "PyTorch metadata mismatch")
    require(str(env["sentence_transformers"]) == "3.0.1", "sentence-transformers metadata mismatch")
    require(str(env["umap_learn"]) == "0.5.6", "UMAP package metadata mismatch")
    require(str(env["hdbscan"]) == "0.8.38.post1", "HDBSCAN package metadata mismatch")
    require(str(env["scikit_learn"]) == "1.5.1", "scikit-learn metadata mismatch")

    evaluation = cfg["evaluation"]
    expected = {
        "reference_theme_count": 32, "blind_subset_size": 103,
        "academic_record_count": 412, "external_record_count": 34500,
        "academic_clusters": 12, "academic_outliers": 33, "public_topic_families": 8,
    }
    for key, value in expected.items():
        require(int(evaluation[key]) == value, f"Evaluation constant mismatch: {key}")


def validate_forbidden_legacy_claims() -> None:
    paths = [
        ROOT / "README.md", ROOT / "data/README.md",
        ROOT / "src/plot_figure4.py", ROOT / "src/semantic_mapping.py",
        ROOT / "src/llm_interpretation.py",
    ]
    forbidden = [
        "74.1% lower", "74% labor reduction", "public-discourse triangulation",
        "llm-assisted semantic clustering",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            require(phrase.lower() not in text, f"Legacy claim remains in {path}: {phrase}")


def main() -> None:
    validate_workflow_metrics()
    validate_reference_crosswalk()
    validate_stability()
    validate_reliability_and_depth()
    validate_runtime()
    validate_external_probe()
    validate_mechanism_and_gap_audit()
    validate_config()
    validate_forbidden_legacy_claims()
    print("PASS: public companion aggregate values, configuration, and claim boundaries match the final manuscript constants checked here.")
    print("Boundary: this check does not validate restricted raw data, expert judgments, or empirical provenance.")


if __name__ == "__main__":
    main()
