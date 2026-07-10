import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from textwrap import dedent

    return dedent, mo


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        # Lab 02 · Measure the Scissors Gap  ·  Chapter 2 (The Loop No Longer Scales)

        **You can, after this lab:** compute the gap between how fast a loop *generates*
        candidates and how fast it can *trust and reject* them, and show why faster
        generation alone widens the gap rather than closing it.

        > **Recap.** A loop is *rejection-bound, not generation-bound*: when AI makes
        > candidates cheap, the binding rate is how fast the loop can reject or commit
        > with confidence. The first blade (generation) rises fast; the second blade
        > (trusted rejection) does not.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    warmup = mo.ui.radio(
        options={
            "Buy the fastest generator; more candidates is the goal.": "wrong",
            "Grow trusted-rejection capacity to match generation, or the backlog scales your mistakes.": "right",
            "Generation and rejection always scale together.": "wrong2",
        },
        label="**Warm-up (unlocks the lab).** If generation gets 100x cheaper, what should a team invest in?",
    )
    warmup
    return (warmup,)


@app.cell
def _(mo, warmup):
    mo.stop(warmup.value != "right", mo.md("🔒 *Match the recap to continue.*"))
    mo.md("✅ Right. Now put numbers on it.")
    return


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        ## The two rates

        Take a human-era baseline for one design loop (illustrative anchors, order of
        magnitude, in the spirit of the chapter's DSE and verification numbers):

        - **Generation rate** `G0` ≈ **100** candidate configurations explored per engineer-week.
        - **Trusted-rejection rate** `R0` ≈ **20** candidates per engineer-week that a
          team can actually evaluate, reject on evidence, or commit.

        The **gap** is `G / R`: how many generated candidates pile up behind each one the
        loop can trust. Baseline gap = 100 / 20 = **5** waiting per trusted decision.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    predict = mo.ui.radio(
        options={
            "The gap closes (AI helps rejection too).": "close",
            "The gap widens (generation outruns rejection).": "widen",
            "The gap stays the same.": "same",
        },
        label="**Predict.** AI makes generation 100x faster and trusted rejection 3x faster. The gap will…",
    )
    confidence = mo.ui.slider(0, 100, step=5, value=50, label="**Confidence** (%)")
    reason = mo.ui.text_area(
        label="**Reason** (required)", rows=2, placeholder="Why that direction?"
    )
    lock = mo.ui.run_button(label="🔒 Lock my prediction")
    mo.vstack([predict, confidence, reason, lock])
    return lock, predict, reason


@app.cell
def _(lock, mo, reason):
    mo.stop(
        not lock.value or not reason.value.strip(),
        mo.md("*Predict, give a reason, and lock.*"),
    )
    mo.md("Locked. Now move the blades yourself.")
    return


@app.cell
def _(mo):
    gen_speedup = mo.ui.slider(
        1, 1000, value=100, label="**Generation speedup** (x over human era)"
    )
    rej_speedup = mo.ui.slider(
        1, 1000, value=3, label="**Trusted-rejection speedup** (x over human era)"
    )
    mo.vstack([gen_speedup, rej_speedup])
    return gen_speedup, rej_speedup


@app.cell
def _(gen_speedup, mo, rej_speedup):
    G0, R0 = 100, 20
    gap0 = G0 / R0
    G = G0 * gen_speedup.value
    R = R0 * rej_speedup.value
    gap = G / R
    ratio = gap / gap0
    direction = "widened" if ratio > 1.01 else ("closed" if ratio < 0.99 else "held")
    color = "🔴" if direction == "widened" else ("🟢" if direction == "closed" else "🟡")
    mo.md(
        f"""
        ### The measured gap

        | | **Generation `G`** | **Trusted rejection `R`** | **Gap `G/R`** |
        | --- | --- | --- | --- |
        | Human era | {G0}/wk | {R0}/wk | {gap0:.1f} |
        | With your speedups | {G:.0f}/wk | {R:.0f}/wk | **{gap:.1f}** |

        {color} The gap **{direction}** by **{ratio:.1f}x** relative to the human-era baseline.
        A gap of {gap:.0f} means {gap:.0f} generated candidates wait behind every one the
        loop can trust.
        """
    )
    return G0, R0, gap0


@app.cell
def _(gen_speedup, mo, predict, rej_speedup):
    widened = gen_speedup.value > rej_speedup.value
    got_it = (predict.value == "widen" and widened) or (
        predict.value == "close" and not widened
    )
    mo.md(
        f"""
        ### Reconcile

        You predicted the gap would **{ {"widen": "widen", "close": "close", "same": "stay the same"}.get(predict.value, "—")}**.
        The arithmetic says it **{"widens" if widened else "closes"}** whenever generation
        speedup ({gen_speedup.value}x) {">" if widened else "≤"} rejection speedup ({rej_speedup.value}x).
        {"Your mental model held." if got_it else "The gap follows the ratio of the two speedups, not generation alone."}

        **The mechanism.** The gap is `G/R`. Scaling `G` alone multiplies the backlog.
        Only raising `R` (independent, trusted rejection) closes it. That is what
        "rejection-bound" means, in one division.
        """
    )
    return


@app.cell
def _(mo):
    invest = mo.ui.dropdown(
        options=[
            "Invest in a faster generator (raise G further)",
            "Invest in trusted-rejection capacity (raise R to meet G)",
        ],
        label="**Commit.** Your loop's gap is too large. Where does the next dollar go?",
    )
    invest
    return (invest,)


@app.cell
def _(gen_speedup, invest, mo, rej_speedup):
    if invest.value is None:
        _out = mo.md("*Choose where to invest.*")
    elif invest.value.startswith("Invest in trusted"):
        _out = mo.md(
            "✅ Consistent with the arithmetic: closing the gap needs `R` to chase `G`."
        )
    else:
        _out = mo.md(
            f"🛑 Raising G again (already {gen_speedup.value}x) widens the gap further; "
            f"R is the binding rate ({rej_speedup.value}x). This is scaling your backlog, not your wins."
        )
    _out
    return


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        ### Reflect

        These rates are illustrative anchors, not measurements. What would you actually
        measure in your own project to estimate `G` and `R` honestly? The chapter's
        claim is falsifiable exactly here: if a team's trusted-rejection rate scales
        with its generation rate, the loop is *not* rejection-bound and this book's
        remedy buys them little. Most teams find the opposite.
        """
        ).strip()
    )
    return


if __name__ == "__main__":
    app.run()
