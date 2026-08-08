#!/usr/bin/env python3
"""Apply the manuscript's explicit scaffold-to-claim eligibility rule.

The script does not generate or judge claims. It only checks whether three
human-audit conditions have been recorded:
  1) document-level trace evidence,
  2) explicit recorded human adjudication,
  3) independent expert confirmation.

If any condition is absent, the item remains a provisional scaffold.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED = [
    "document_trace_evidence",
    "recorded_human_adjudication",
    "independent_expert_confirmation",
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
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing gate fields: {missing}")

    for col in REQUIRED:
        df[col] = as_bool(df[col])
        if df[col].isna().any():
            raise ValueError(f"Column {col} contains values that cannot be interpreted as boolean")

    df["claim_eligible"] = df[REQUIRED].all(axis=1)
    df["claim_status"] = df["claim_eligible"].map(
        {True: "eligible after recorded audit", False: "provisional scaffold"}
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)

    print(df[["proposition_id", "claim_status"]].to_string(index=False))
    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()
