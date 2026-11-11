#!/usr/bin/env python3
"""Draw manuscript Fig. 4 panel values from reported aggregate tables only.

Panel A: selected workflows against the separately constructed 34-theme inventory
(Table 6); these are not independent raw-data reproductions.
Panel B: full-workflow GT-only (85.0 h) and hybrid (110.5 h), +25.5 h (+30%).
Panel C: seven GT-containing category depth scores (Table C5).
No synthetic empirical execution or candidate-level records are generated.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PERFORMANCE_ORDER = ["GT-only", "Pure automated LLM", "Naïve sequential", "Full hybrid governance"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="data/derived/independent_34_theme_metrics_reported.csv")
    parser.add_argument("--workflow-metrics", default="data/derived/workflow_metrics.csv")
    parser.add_argument("--depth", default="data/derived/interpretive_depth.csv")
    parser.add_argument("--output", default="outputs/figure4_role_aligned.png")
    args = parser.parse_args()

    performance = pd.read_csv(args.metrics).set_index("workflow").loc[PERFORMANCE_ORDER].reset_index()
    effort = pd.read_csv(args.workflow_metrics).set_index("workflow")
    depth = pd.read_csv(args.depth)
    if not (performance["reference_total"] == 34).all():
        raise ValueError("Panel A must use the separate independent 34-theme reference")
    full_gt = float(effort.loc["GT-only", "recorded_person_hours"])
    full_hybrid = float(effort.loc["Full hybrid", "recorded_person_hours"])
    if not (np.isclose(full_gt, 85.0) and np.isclose(full_hybrid, 110.5)):
        raise ValueError("Panel B requires complete-workflow endpoints 85.0 and 110.5 h")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1.25], hspace=0.46, wspace=0.42)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :])

    # Panel A: independent 34-theme comparison, matching Fig. 4A's selected workflows.
    y = np.arange(len(performance))[::-1]
    offsets = {"coverage": 0.17, "reference_precision": 0.0, "f1": -0.17}
    markers = {"coverage": "o", "reference_precision": "s", "f1": "D"}
    labels = {"coverage": "Coverage", "reference_precision": "Ref. precision", "f1": "F1"}
    for field in ("coverage", "reference_precision", "f1"):
        yy = y + offsets[field]
        values = performance[field].astype(float).to_numpy()
        ax_a.hlines(yy, 60, values, lw=1, alpha=0.4)
        ax_a.scatter(values, yy, marker=markers[field], s=35, label=labels[field], zorder=3)
        for v, yi in zip(values, yy):
            ax_a.text(v + 0.5, yi, f"{v:.1f}%", fontsize=7, va="center")
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(["GT-only", "Pure automated LLM", "Naïve sequential", "Full hybrid governance"])
    ax_a.set_xlim(58, 104)
    ax_a.set_xticks([60, 70, 80, 90, 100])
    ax_a.set_xlabel("Performance (%)")
    ax_a.set_title("A   Independent reference performance", loc="left", fontweight="bold")
    ax_a.text(0, 1.02, "Independent 34-theme inventory (reported aggregates)",
              transform=ax_a.transAxes, fontsize=8)
    ax_a.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.52, 1.15))
    ax_a.grid(axis="x", alpha=0.2)

    # Panel B: compare the two complete workflows, not nested stage endpoints.
    labels_b = ["GT-only\\ncomplete workflow", "Full hybrid\\ncomplete workflow"]
    values_b = [full_gt, full_hybrid]
    y_b = [1, 0]
    ax_b.barh(y_b, values_b)
    ax_b.set_yticks(y_b)
    ax_b.set_yticklabels([s.replace("\\\\n", "\\n") for s in labels_b])
    ax_b.set_xlim(0, 132)
    ax_b.set_xlabel("Recorded analyst effort (person-hours)")
    ax_b.set_title("B   Recorded analyst effort", loc="left", fontweight="bold")
    ax_b.text(0, 1.02, "Comparable complete-workflow endpoints",
              transform=ax_b.transAxes, fontsize=8)
    for value, yi in zip(values_b, y_b):
        ax_b.text(value + 1.5, yi, f"{value:.1f} h", fontsize=9, va="center")
    ax_b.text(0.02, 0.04, "+25.5 h (+30.0%) vs GT-only; 85.0 + 3.5 + 22.0 = 110.5 h",
              transform=ax_b.transAxes, fontsize=8)
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

    for ax in (ax_a, ax_b, ax_c):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_alpha(0.25)
        ax.spines["bottom"].set_alpha(0.25)

    fig.suptitle(
        "Fig. 4. Reported independent 34-theme metrics, complete-workflow effort and GT-category depth. "
        "This is a redraw of manuscript tables, not an independent reconstruction of raw records.",
        y=0.015, fontsize=9,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, bbox_inches="tight")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
