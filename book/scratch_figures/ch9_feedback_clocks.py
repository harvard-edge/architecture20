"""Timeline chart showing the three feedback clocks operating on different timescales."""
import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Add _python dir to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "_python"))
from arch2_plots import COLORS, apply_style, top_log_axis, row_axis, draw_range_rows


def main():
    apply_style()

    fig, ax = plt.subplots(figsize=(8, 3.2))

    # Data for the three feedback clocks
    # Scale: Time in Seconds
    rows = [
        {
            "low": 1e-3,  # 1 ms
            "high": 86400 * 7,  # Days
            "color": COLORS["green"],
            "display_label": "In-field",
            "display_note": "Dynamic adaptation",
            "right_label": "ms to days",
        },
        {
            "low": 86400 * 30,  # Months
            "high": 3.15e7 * 2,  # 2 Years
            "color": COLORS["orange"],
            "display_label": "Continuing Enablement",
            "display_note": "Firmware / Software tuning",
            "right_label": "months to years",
        },
        {
            "low": 3.15e7 * 1,  # 1 Year
            "high": 3.15e7 * 5,  # 5 Years
            "color": COLORS["blue"],
            "display_label": "Design-time",
            "display_note": "Next-gen architecture",
            "right_label": "years",
        },
    ]

    row_axis(ax, len(rows))

    top_log_axis(
        ax,
        xlim=(1e-4, 1e9),
        xticks=[1e-3, 1, 60, 3600, 86400, 2.6e6, 3.15e7, 3.15e7 * 10],
        xticklabels=["1 ms", "1 s", "1 min", "1 hr", "1 day", "1 mo", "1 yr", "10 yr"],
        xlabel="Timescale (Seconds)",
    )

    draw_range_rows(
        ax,
        rows,
        low_key="low",
        high_key="high",
        label_x=-0.25,
        right_x=1.02,
        label_fontsize=8,
        note_fontsize=6.5,
        right_fontsize=7.5,
        show_notes=True,
        label_dy=-0.15,
        note_dy=0.20,
    )

    plt.tight_layout()
    out_path = Path(__file__).with_suffix(".png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
