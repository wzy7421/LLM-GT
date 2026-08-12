#!/usr/bin/env python3
"""Regenerate the manuscript-aligned role-specific comparison (Fig. 4).

The script uses only aggregate values already reported in the manuscript.
Panel A compares shared reference-theme metrics across the four workflows.
Panel B reports recorded person-time only at its documented, non-equivalent
activity endpoints; it does not estimate a percentage labor reduction and does
not treat the 22.0 h post-GT stage as a standalone full-hybrid total.
Panel C compares interpretive depth only for GT-containing workflows.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PERFORMANCE_ORDER = [
    "GT-only",
    "Semantic map only",
    "Semantic map + LLM",
    "Full hybrid",
]

TIME_ORDER = [
    "GT-only",
    "Semantic map only",
    "Semantic map + LLM",
    "Post-GT hybrid integration and adjudication",
]

TIME_LABELS = {
    "GT-only": "GT-only\n(complete workflow)",
    "Semantic map only": "Semantic map\n(mapping stage)",
    "Semantic map + LLM": "Map + LLM\n(mapping + interpretation)",
    "Post-GT hybrid integration and adjudication": "Post-GT integration\n(additional stage)",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="data/derived/workflow_metrics.csv")
    parser.add_argument("--depth", default="data/derived/interpretive_depth.csv")
    parser.add_argument("--output", default="outputs/figure4_role_aligned.png")
    args = parser.parse_args()

    raw_metrics = pd.read_csv(args.metrics)
    performance = (
        raw_metrics.set_index("workflow")
        .loc[PERFORMANCE_ORDER]
        .reset_index()
    )
    time_data = (
        raw_metrics.set_index("workflow")
        .loc[TIME_ORDER]
        .reset_index()
    )
    depth = pd.read_csv(args.depth)

    plt.rcParams.update(
        {
            "font.family": "Times New Roman",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
        }
    )

    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.25], hspace=0.42, wspace=0.30)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :])

    # Panel A: shared reference-theme performance against the frozen 32-theme inventory.
    y = np.arange(len(performance))[::-1]
    offsets = {"coverage": 0.16, "precision": 0.0, "f1": -0.16}
    markers = {"coverage": "o", "precision": "s", "f1": "D"}
    labels = {"coverage": "Coverage", "precision": "Precision", "f1": "F1"}

    for metric in ["coverage", "precision", "f1"]:
        yy = y + offsets[metric]
        values = performance[metric].astype(float).to_numpy()
        ax_a.hlines(yy, 60, values, linewidth=1.0, alpha=0.55)
        ax_a.scatter(values, yy, marker=markers[metric], s=34, label=labels[metric], zorder=3)
        for x, y_i in zip(values, yy):
            ax_a.text(x + 0.8, y_i, f"{x:.1f}%", va="center", fontsize=8)

    ax_a.set_yticks(y)
    ax_a.set_yticklabels(performance["workflow"])
    ax_a.set_xlim(60, 100)
    ax_a.set_xticks([60, 70, 80, 90, 100])
    ax_a.set_xticklabels(["60%", "70%", "80%", "90%", "100%"])
    ax_a.set_xlabel("Performance (%)")
    ax_a.set_title("A   Shared reference-theme performance", loc="left", fontweight="bold")
    ax_a.text(
        0.0,
        1.02,
        "Frozen 32-theme reference inventory",
        transform=ax_a.transAxes,
        fontsize=8,
    )
    ax_a.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.52, 1.16))
    ax_a.grid(axis="x", alpha=0.2)

    # Panel B: stage-specific analyst time. Endpoints are deliberately not normalized.
    y_b = np.arange(len(time_data))[::-1]
    times = pd.to_numeric(time_data["recorded_person_hours"], errors="coerce").to_numpy()
    if np.isnan(times).any():
        raise ValueError("Panel B requires a recorded_person_hours value for each stage in TIME_ORDER")

    ax_b.barh(y_b, times)
    ax_b.set_yticks(y_b)
    ax_b.set_yticklabels([TIME_LABELS[x] for x in time_data["workflow"]])
    ax_b.set_xlim(0, 90)
    ax_b.set_xticks([0, 15, 30, 45, 60, 75, 90])
    ax_b.set_xlabel("Recorded person-hours")
    ax_b.set_title("B   Recorded activity time", loc="left", fontweight="bold")
    ax_b.text(
        0.0,
        1.02,
        "Non-equivalent endpoints; descriptive stage planning only",
        transform=ax_b.transAxes,
        fontsize=8,
    )
    for x, y_i in zip(times, y_b):
        ax_b.text(x + 1.2, y_i, f"{x:.1f} h", va="center", fontsize=8)
    ax_b.grid(axis="x", alpha=0.2)

    # Panel C: interpretive depth only for GT-containing workflows.
    cat = depth[depth["category"] != "Mean"].copy()
    mean_row = depth[depth["category"] == "Mean"].iloc[0]
    y_c = np.arange(len(cat))[::-1] + 1

    for y_i, (_, row) in zip(y_c, cat.iterrows()):
        ax_c.plot([row["gt_only"], row["full_hybrid"]], [y_i, y_i], color="0.65", linewidth=1.2)
        ax_c.scatter(
            row["gt_only"],
            y_i,
            marker="o",
            s=34,
            label="GT-only" if y_i == y_c[0] else None,
            zorder=3,
        )
        ax_c.scatter(
            row["full_hybrid"],
            y_i,
            marker="D",
            s=34,
            label="Full hybrid" if y_i == y_c[0] else None,
            zorder=3,
        )
        ax_c.text(row["gt_only"] + 0.035, y_i, f"{row['gt_only']:.1f}", va="center", fontsize=8)
        ax_c.text(
            row["full_hybrid"] - 0.035,
            y_i,
            f"{row['full_hybrid']:.1f}",
            va="center",
            ha="right",
            fontsize=8,
        )
        ax_c.text(5.14, y_i, f"{row['delta_hybrid_minus_gt']:+.1f}", va="center", ha="center", fontsize=8)

    mean_y = 0
    ax_c.axhline(0.55, linestyle="--", linewidth=0.8, alpha=0.45)
    ax_c.plot([mean_row["gt_only"], mean_row["full_hybrid"]], [mean_y, mean_y], color="0.5", linewidth=1.4)
    ax_c.scatter(mean_row["gt_only"], mean_y, marker="o", s=38, zorder=3)
    ax_c.scatter(mean_row["full_hybrid"], mean_y, marker="D", s=38, zorder=3)
    ax_c.text(mean_row["gt_only"] + 0.035, mean_y, f"{mean_row['gt_only']:.2f}", va="center", fontsize=8)
    ax_c.text(
        mean_row["full_hybrid"] - 0.035,
        mean_y,
        f"{mean_row['full_hybrid']:.2f}",
        va="center",
        ha="right",
        fontsize=8,
    )
    ax_c.text(5.14, mean_y, f"{mean_row['delta_hybrid_minus_gt']:+.2f}", va="center", ha="center", fontsize=8)

    ax_c.set_yticks(list(y_c) + [mean_y])
    ax_c.set_yticklabels(cat["category"].tolist() + ["Mean"])
    ax_c.set_xlim(3.5, 5.25)
    ax_c.set_xticks([3.5, 4.0, 4.5, 5.0])
    ax_c.set_xlabel("Expert rating (1–5)")
    ax_c.set_title("C   Interpretive depth by category", loc="left", fontweight="bold")
    ax_c.text(
        0.0,
        1.02,
        "GT-containing workflows only; category means are based on locked expert ratings",
        transform=ax_c.transAxes,
        fontsize=8,
    )
    ax_c.text(5.14, y_c[0] + 0.65, "Δ (hybrid − GT)", ha="center", fontsize=8, fontweight="bold")
    ax_c.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.50, 1.13))
    ax_c.grid(axis="x", alpha=0.15)

    for ax in [ax_a, ax_b, ax_c]:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_alpha(0.25)
        ax.spines["bottom"].set_alpha(0.25)

    fig.suptitle(
        "Fig. 4. Role-aligned component comparison. Panel A uses the frozen 32-theme reference inventory; "
        "Panel B reports non-equivalent activity endpoints without a percentage labor-reduction claim; "
        "Panel C compares interpretive depth only for GT-containing workflows.",
        y=0.02,
        fontsize=9,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, bbox_inches="tight")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
