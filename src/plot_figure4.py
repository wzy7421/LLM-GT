#!/usr/bin/env python3
"""Regenerate the revised role-aligned component comparison (Fig. 4).

Uses only aggregate values already reported in the manuscript. The purpose is
to make figure generation auditable without exposing restricted source data.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


WORKFLOW_ORDER = [
    "GT-only",
    "Semantic map only",
    "Semantic map + LLM",
    "Full hybrid",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="data/derived/workflow_metrics.csv")
    parser.add_argument("--depth", default="data/derived/interpretive_depth.csv")
    parser.add_argument("--output", default="outputs/figure4_role_aligned.png")
    args = parser.parse_args()

    metrics = pd.read_csv(args.metrics).set_index("workflow").loc[WORKFLOW_ORDER].reset_index()
    depth = pd.read_csv(args.depth)

    plt.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
    })

    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.25], hspace=0.38, wspace=0.28)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :])

    # Panel A: shared retrieval performance
    y = np.arange(len(metrics))[::-1]
    offsets = {"coverage": 0.16, "precision": 0.0, "f1": -0.16}
    markers = {"coverage": "o", "precision": "s", "f1": "D"}
    labels = {"coverage": "Coverage", "precision": "Precision", "f1": "F1"}

    for metric in ["coverage", "precision", "f1"]:
        yy = y + offsets[metric]
        values = metrics[metric].to_numpy()
        ax_a.hlines(yy, 60, values, linewidth=1.0, alpha=0.55)
        ax_a.scatter(values, yy, marker=markers[metric], s=34, label=labels[metric], zorder=3)
        for x, y_i in zip(values, yy):
            ax_a.text(x + 0.8, y_i, f"{x:.1f}%", va="center", fontsize=8)

    ax_a.set_yticks(y)
    ax_a.set_yticklabels(metrics["workflow"])
    ax_a.set_xlim(60, 100)
    ax_a.set_xticks([60, 70, 80, 90, 100])
    ax_a.set_xticklabels(["60%", "70%", "80%", "90%", "100%"])
    ax_a.set_xlabel("Performance (%)")
    ax_a.set_title("A   Shared retrieval performance", loc="left", fontweight="bold")
    ax_a.text(0.0, 1.02, "Same target set (32 confirmed themes); percentage scale", transform=ax_a.transAxes, fontsize=8)
    ax_a.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.52, 1.16))
    ax_a.grid(axis="x", alpha=0.2)

    # Panel B: recorded analyst time
    times = metrics["recorded_person_hours"].to_numpy()
    ax_b.barh(y, times)
    ax_b.set_yticks(y)
    ax_b.set_yticklabels(metrics["workflow"])
    ax_b.set_xlim(0, 90)
    ax_b.set_xticks([0, 15, 30, 45, 60, 75, 90])
    ax_b.set_xlabel("Recorded person-hours")
    ax_b.set_title("B   Recorded analyst time", loc="left", fontweight="bold")
    ax_b.text(0.0, 1.02, "Observed person-hours by workflow; descriptive comparison", transform=ax_b.transAxes, fontsize=8)
    for x, y_i in zip(times, y):
        ax_b.text(x + 1.2, y_i, f"{x:.1f} h", va="center", fontsize=8)
    ax_b.text(0.98, 0.06, "Hybrid vs GT-only: 74.1% lower recorded time", transform=ax_b.transAxes, ha="right", fontsize=8)
    ax_b.grid(axis="x", alpha=0.2)

    # Panel C: interpretive depth only for GT-containing workflows
    cat = depth[depth["category"] != "Mean"].copy()
    mean_row = depth[depth["category"] == "Mean"].iloc[0]
    y_c = np.arange(len(cat))[::-1] + 1

    for y_i, (_, row) in zip(y_c, cat.iterrows()):
        ax_c.plot([row["gt_only"], row["full_hybrid"]], [y_i, y_i], color="0.65", linewidth=1.2)
        ax_c.scatter(row["gt_only"], y_i, marker="o", s=34, label="GT-only" if y_i == y_c[0] else None, zorder=3)
        ax_c.scatter(row["full_hybrid"], y_i, marker="D", s=34, label="Full hybrid" if y_i == y_c[0] else None, zorder=3)
        ax_c.text(row["gt_only"] + 0.035, y_i, f"{row['gt_only']:.1f}", va="center", fontsize=8)
        ax_c.text(row["full_hybrid"] - 0.035, y_i, f"{row['full_hybrid']:.1f}", va="center", ha="right", fontsize=8)
        ax_c.text(5.14, y_i, f"{row['delta_hybrid_minus_gt']:+.1f}", va="center", ha="center", fontsize=8)

    mean_y = 0
    ax_c.axhline(0.55, linestyle="--", linewidth=0.8, alpha=0.45)
    ax_c.plot([mean_row["gt_only"], mean_row["full_hybrid"]], [mean_y, mean_y], color="0.5", linewidth=1.4)
    ax_c.scatter(mean_row["gt_only"], mean_y, marker="o", s=38, zorder=3)
    ax_c.scatter(mean_row["full_hybrid"], mean_y, marker="D", s=38, zorder=3)
    ax_c.text(mean_row["gt_only"] + 0.035, mean_y, f"{mean_row['gt_only']:.2f}", va="center", fontsize=8)
    ax_c.text(mean_row["full_hybrid"] - 0.035, mean_y, f"{mean_row['full_hybrid']:.2f}", va="center", ha="right", fontsize=8)
    ax_c.text(5.14, mean_y, f"{mean_row['delta_hybrid_minus_gt']:+.2f}", va="center", ha="center", fontsize=8)

    ax_c.set_yticks(list(y_c) + [mean_y])
    ax_c.set_yticklabels(cat["category"].tolist() + ["Mean"])
    ax_c.set_xlim(3.5, 5.25)
    ax_c.set_xticks([3.5, 4.0, 4.5, 5.0])
    ax_c.set_xlabel("Expert rating (1–5)")
    ax_c.set_title("C   Interpretive depth by category", loc="left", fontweight="bold")
    ax_c.text(0.0, 1.02, "Grounded theory workflows only; 1–5 expert rating scale", transform=ax_c.transAxes, fontsize=8)
    ax_c.text(5.14, y_c[0] + 0.65, "Δ (hybrid − GT)", ha="center", fontsize=8, fontweight="bold")
    ax_c.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.50, 1.13))
    ax_c.grid(axis="x", alpha=0.15)

    for ax in [ax_a, ax_b, ax_c]:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_alpha(0.25)
        ax.spines["bottom"].set_alpha(0.25)

    fig.suptitle(
        "Fig. 4. Role-aligned component comparison. Shared retrieval and analyst-time measures include all four workflows; "
        "interpretive depth is scored only for GT-containing workflows.",
        y=0.02,
        fontsize=9,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, bbox_inches="tight")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
