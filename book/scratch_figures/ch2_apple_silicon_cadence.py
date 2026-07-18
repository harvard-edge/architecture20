"""Plot showing the accelerating pace of Apple Silicon and NVIDIA GPU releases."""
import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Add _python dir to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "_python"))
from arch2_plots import COLORS, apply_style


def main():
    apply_style()

    fig, ax = plt.subplots(figsize=(10, 4))

    # Apple Data
    apple_months = [0, 19, 35, 42]
    apple_labels = ["M1\nNov 2020", "M2\nJun 2022", "M3\nOct 2023", "M4\nMay 2024"]
    apple_gaps = [19, 16, 7]

    # GPU Data
    gpu_months = [-6, 16, 40, 62]
    gpu_labels = [
        "A100\nMay 2020",
        "H100\nMar 2022",
        "B100\nMar 2024",
        "R100\nJan 2026",
    ]
    gpu_gaps = [22, 24, 22]

    # Draw Apple timeline (y=0.5)
    ax.plot([-10, 68], [0.5, 0.5], color=COLORS["grid"], linewidth=2, zorder=1)
    ax.plot(
        apple_months,
        [0.5] * len(apple_months),
        color=COLORS["ink"],
        linewidth=3,
        zorder=2,
    )
    ax.scatter(
        apple_months,
        [0.5] * len(apple_months),
        facecolor=COLORS["note_fill"],
        edgecolor=COLORS["blue"],
        s=150,
        linewidth=2.5,
        zorder=3,
    )
    ax.text(
        -8,
        0.5,
        "Apple\nSilicon",
        ha="right",
        va="center",
        fontweight="bold",
        color=COLORS["ink"],
        fontsize=10,
    )

    for m, l in zip(apple_months, apple_labels):
        ax.text(
            m,
            0.55,
            l,
            ha="center",
            va="bottom",
            fontweight="bold",
            color=COLORS["ink"],
            fontsize=9,
        )
    for i in range(len(apple_months) - 1):
        mid = (apple_months[i] + apple_months[i + 1]) / 2
        ax.annotate(
            "",
            xy=(apple_months[i + 1] - 0.5, 0.47),
            xytext=(apple_months[i] + 0.5, 0.47),
            arrowprops=dict(
                arrowstyle="<->",
                color=COLORS["magenta"],
                linewidth=1.5,
                shrinkA=0,
                shrinkB=0,
            ),
        )
        ax.text(
            mid,
            0.43,
            f"{apple_gaps[i]}mo",
            ha="center",
            va="top",
            color=COLORS["decision_ink"],
            fontweight="bold",
            fontsize=9,
        )

    # Draw GPU timeline (y=-0.5)
    ax.plot([-10, 68], [-0.5, -0.5], color=COLORS["grid"], linewidth=2, zorder=1)
    ax.plot(
        gpu_months, [-0.5] * len(gpu_months), color=COLORS["ink"], linewidth=3, zorder=2
    )
    ax.scatter(
        gpu_months,
        [-0.5] * len(gpu_months),
        facecolor=COLORS["note_fill"],
        edgecolor=COLORS["blue"],
        s=150,
        linewidth=2.5,
        zorder=3,
    )
    ax.text(
        -8,
        -0.5,
        "NVIDIA\nDatacenter",
        ha="right",
        va="center",
        fontweight="bold",
        color=COLORS["ink"],
        fontsize=10,
    )

    for m, l in zip(gpu_months, gpu_labels):
        ax.text(
            m,
            -0.45,
            l,
            ha="center",
            va="bottom",
            fontweight="bold",
            color=COLORS["ink"],
            fontsize=9,
        )
    for i in range(len(gpu_months) - 1):
        mid = (gpu_months[i] + gpu_months[i + 1]) / 2
        ax.annotate(
            "",
            xy=(gpu_months[i + 1] - 0.5, -0.53),
            xytext=(gpu_months[i] + 0.5, -0.53),
            arrowprops=dict(
                arrowstyle="<->",
                color=COLORS["magenta"],
                linewidth=1.5,
                shrinkA=0,
                shrinkB=0,
            ),
        )
        ax.text(
            mid,
            -0.57,
            f"{gpu_gaps[i]}mo",
            ha="center",
            va="top",
            color=COLORS["decision_ink"],
            fontweight="bold",
            fontsize=9,
        )

    ax.set_ylim(-1.0, 1.0)
    ax.set_xlim(-15, 68)
    ax.axis("off")
    ax.set_title(
        "Silicon Release Cadence: Apple vs. NVIDIA",
        fontweight="bold",
        color=COLORS["ink"],
        pad=20,
    )

    plt.tight_layout()
    out_path = Path(__file__).with_suffix(".png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
