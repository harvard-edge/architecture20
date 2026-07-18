import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from arch2_plots import apply_style, COLORS
from pathlib import Path

apply_style()


def draw_grid(ax, rows, cols, cell_size=1.0):
    for r in range(rows + 1):
        ax.plot(
            [0, cols * cell_size],
            [r * cell_size, r * cell_size],
            color=COLORS["grid"],
            linewidth=0.5,
            zorder=1,
        )
    for c in range(cols + 1):
        ax.plot(
            [c * cell_size, c * cell_size],
            [0, rows * cell_size],
            color=COLORS["grid"],
            linewidth=0.5,
            zorder=1,
        )


fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.5))
fig.subplots_adjust(wspace=0.3, left=0.05, right=0.95, top=0.85, bottom=0.15)

titles = [
    "Step 1: Place Macro A",
    "Step 2: Place Macro B",
    "Step 3: Place Macro C\n(Reward Calculation)",
]
colors = [COLORS["blue"], COLORS["orange"], COLORS["green"]]
macro_sizes = [(3, 3), (2, 4), (4, 2)]
positions = [(1, 1), (5, 2), (2, 5)]

for i, ax in enumerate(axes):
    draw_grid(ax, 8, 8)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titles[i], fontsize=8, color=COLORS["ink"], pad=10)

    # Draw placed macros
    for j in range(i + 1):
        x, y = positions[j]
        w, h = macro_sizes[j]
        rect = patches.Rectangle(
            (x, y),
            w,
            h,
            linewidth=1.5,
            edgecolor=colors[j],
            facecolor=colors[j] + "33",
            zorder=2,
        )
        ax.add_patch(rect)
        ax.text(
            x + w / 2,
            y + h / 2,
            f"M{j+1}",
            ha="center",
            va="center",
            fontsize=8,
            color=colors[j],
            fontweight="bold",
        )

    if i == 2:
        # Draw some routing wires
        ax.plot(
            [2.5, 2.5, 4.0],
            [4.0, 6.0, 6.0],
            color=COLORS["red"],
            linewidth=1.5,
            linestyle="--",
            zorder=3,
        )
        ax.plot(
            [6.0, 7.0, 7.0],
            [4.0, 4.0, 6.0],
            color=COLORS["red"],
            linewidth=1.5,
            linestyle="--",
            zorder=3,
        )
        ax.text(
            4,
            -1,
            "Agent optimizes for Wirelength & Congestion",
            ha="center",
            va="center",
            fontsize=7,
            color=COLORS["ink"],
            style="italic",
        )

plt.savefig(
    Path(__file__).parent / "google_rl.png",
    dpi=300,
    bbox_inches="tight",
    transparent=True,
)
print("Saved google_rl.png")
