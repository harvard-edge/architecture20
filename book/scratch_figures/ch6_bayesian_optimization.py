"""1D BO plot showing surrogate mean, uncertainty bands, and acquisition function."""
import sys
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Add _python dir to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "_python"))
from arch2_plots import COLORS, apply_style


def main():
    apply_style()

    x = np.linspace(0, 10, 200)

    # Observations
    obs_x = np.array([1.5, 4.0, 7.5])
    obs_y = np.array([0.2, 1.0, 0.4])

    # Fake GP Surrogate Model
    mean = np.zeros_like(x)
    std = np.ones_like(x) * 1.0

    for ox, oy in zip(obs_x, obs_y):
        mean += oy * np.exp(-((x - ox) ** 2) / 1.5)

    for ox in obs_x:
        std *= 1 - 0.95 * np.exp(-((x - ox) ** 2) / 1.5)

    std = np.clip(std, 0.05, None)  # Minimum uncertainty

    # Fake Acquisition Function (UCB)
    kappa = 2.0
    acq = mean + kappa * std

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(8, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )

    # Top plot: Surrogate Model
    ax1.plot(x, mean, color=COLORS["blue"], label="Surrogate Mean", linewidth=2)
    ax1.fill_between(
        x,
        mean - 1.96 * std,
        mean + 1.96 * std,
        color=COLORS["blue"],
        alpha=0.15,
        label="Epistemic Uncertainty",
    )
    ax1.scatter(
        obs_x,
        obs_y,
        facecolor=COLORS["evidence"],
        edgecolor=COLORS["ink"],
        zorder=5,
        s=80,
        linewidth=1,
        label="Observations",
    )

    ax1.set_ylabel("Objective Value", fontweight="bold", color=COLORS["ink"])
    ax1.set_title(
        "Gaussian Process Surrogate Model", fontweight="bold", color=COLORS["ink"]
    )
    ax1.legend(loc="upper right", frameon=False)

    # Bottom plot: Acquisition Function
    ax2.plot(x, acq, color=COLORS["orange"], label="Acquisition Function", linewidth=2)
    ax2.fill_between(x, 0, acq, color=COLORS["orange"], alpha=0.15)

    ax2.set_xlabel("Design Space", fontweight="bold", color=COLORS["ink"])
    ax2.set_ylabel("Acquisition Value", fontweight="bold", color=COLORS["ink"])
    ax2.set_title("Acquisition Function (UCB)", fontweight="bold", color=COLORS["ink"])

    # Highlight exploration vs exploitation
    exploit_idx = np.argmin(np.abs(x - 4.0))
    explore_idx = np.argmin(np.abs(x - 9.5))

    ax2.annotate(
        "Exploitation\n(High Mean)",
        xy=(4.0, acq[exploit_idx]),
        xytext=(3.0, 1.5),
        arrowprops=dict(facecolor=COLORS["ink"], shrink=0.05, width=1, headwidth=5),
        ha="center",
        fontsize=9,
        color=COLORS["methods_ink"],
        fontweight="bold",
    )

    ax2.annotate(
        "Exploration\n(High Uncertainty)",
        xy=(9.5, acq[explore_idx]),
        xytext=(8.0, 2.5),
        arrowprops=dict(facecolor=COLORS["ink"], shrink=0.05, width=1, headwidth=5),
        ha="center",
        fontsize=9,
        color=COLORS["methods_ink"],
        fontweight="bold",
    )

    for ax in [ax1, ax2]:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(COLORS["ink"])
        ax.spines["bottom"].set_color(COLORS["ink"])
        ax.tick_params(colors=COLORS["ink"])

    ax2.set_ylim(0, 3.5)

    plt.tight_layout()
    out_path = Path(__file__).with_suffix(".png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
