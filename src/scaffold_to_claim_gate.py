#!/usr/bin/env python3
"""Apply the manuscript's recorded scaffold-to-claim and gap-eligibility rules.

Layer 1: scaffold-to-claim gate
  1) document-level trace evidence,
  2) explicit recorded human adjudication,
  3) independent expert confirmation.

Layer 2: optional research-gap eligibility screen
When expert-rating columns are present, all four panel means (novelty,
importance, feasibility, traceability) must be >= 3.5/5 and no individual
traceability rating may be below 3.0.

The script does not generate claims, infer research gaps, or replace expert
judgment. It only checks whether manuscript-defined audit conditions have been
recorded in a supplied ledger.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


CORE_REQUIRED = [
    "proposition_id",
    "document_trace_evidence",
    "recorded_human_adjudication",
    "independent_expert_confirmation",
]

EXPERT_SCORE_COLUMNS = [
    "expert_novelty_mean",
    "expert_importance_mean",
    "expert_feasibility_mean",
    "expert_traceability_mean",
    "expert_traceability_min",
]


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().map(
        {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/demo/gate_demo.csv")
    parser.add_argument("--output", default="outputs/gate_decisions.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    missing = [c for c in CORE_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required gate fields: {missing}")

    for col in CORE_REQUIRED[1:]:
        df[col] = as_bool(df[col])
        if df[col].isna().any():
            raise ValueError(f"Column {col} contains values that cannot be interpreted as boolean")

    df["scaffold_gate_pass"] = df[CORE_REQUIRED[1:]].all(axis=1)

    present_scores = [c for c in EXPERT_SCORE_COLUMNS if c in df.columns]
    if present_scores and len(present_scores) != len(EXPERT_SCORE_COLUMNS):
        missing_scores = [c for c in EXPERT_SCORE_COLUMNS if c not in df.columns]
        raise ValueError(
            "Expert-rating screening is optional, but when used all score columns are required. "
            f"Missing: {missing_scores}"
        )

    if len(present_scores) == len(EXPERT_SCORE_COLUMNS):
        for col in EXPERT_SCORE_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if df[col].isna().any():
                raise ValueError(f"Column {col} contains non-numeric or missing values")

        for col in [
            "expert_novelty_mean",
            "expert_importance_mean",
            "expert_feasibility_mean",
            "expert_traceability_mean",
        ]:
            if ((df[col] < 1.0) | (df[col] > 5.0)).any():
                raise ValueError(f"Column {col} must use the manuscript's 1–5 rating scale")
        if ((df["expert_traceability_min"] < 1.0) | (df["expert_traceability_min"] > 5.0)).any():
            raise ValueError("expert_traceability_min must use the manuscript's 1–5 rating scale")

        mean_pass = (
            (df["expert_novelty_mean"] >= 3.5)
            & (df["expert_importance_mean"] >= 3.5)
            & (df["expert_feasibility_mean"] >= 3.5)
            & (df["expert_traceability_mean"] >= 3.5)
        )
        trace_min_pass = df["expert_traceability_min"] >= 3.0
        df["expert_screen_pass"] = mean_pass & trace_min_pass
        df["gap_eligible"] = df["scaffold_gate_pass"] & df["expert_screen_pass"]
        df["claim_status"] = df["gap_eligible"].map(
            {True: "eligible after recorded audit and expert screen", False: "not eligible / remains provisional or rejected"}
        )
    else:
        df["expert_screen_pass"] = pd.NA
        df["gap_eligible"] = pd.NA
        df["claim_status"] = df["scaffold_gate_pass"].map(
            {True: "passes scaffold-to-claim gate; gap rating screen not supplied", False: "provisional scaffold"}
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)

    display_cols = ["proposition_id", "scaffold_gate_pass", "expert_screen_pass", "gap_eligible", "claim_status"]
    print(df[display_cols].to_string(index=False))
    print(f"\nSaved: {output}")
    print(
        "Boundary: this checker verifies recorded conditions only. It does not create propositions, "
        "judge novelty, or substitute for independent human expert assessment."
    )


if __name__ == "__main__":
    main()
