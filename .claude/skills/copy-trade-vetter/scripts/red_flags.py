#!/usr/bin/env python3
"""First-pass red-flag checker for a copy-trading strategy.

Usage: python red_flags.py '<json>'   (or pipe JSON on stdin)

Recognized keys (all optional; percentages as numbers, e.g. 76.4):
  total_return_pct, max_drawdown_pct, avg_monthly_return_pct, win_rate_pct,
  avg_win, avg_loss, num_trades, sharpe, balance, equity,
  track_record_start, joined_date (YYYY-MM-DD), is_demo (bool),
  broker_regulated (bool), martingale_or_grid (bool), uses_stop_loss (bool),
  avg_hold_minutes, monthly_returns_pct (list of numbers)
"""
import json
import sys
from datetime import date


def _d(s):
    return date.fromisoformat(s[:10])


def check(s):
    flags = []  # (severity, message)

    def add(sev, msg):
        flags.append((sev, msg))

    if s.get("is_demo"):
        add("FATAL", "Demo account — results aren't real-money trading.")
    if s.get("martingale_or_grid"):
        add("FATAL", "Martingale/grid behavior — eventual blow-up risk.")
    if s.get("uses_stop_loss") is False:
        add("FATAL", "No stop-losses — losses are unbounded.")
    if s.get("broker_regulated") is False:
        add("FATAL", "Unregulated broker — counterparty/withdrawal risk.")

    start, joined = s.get("track_record_start"), s.get("joined_date")
    if start and joined and _d(start) < _d(joined):
        months = (_d(joined) - _d(start)).days / 30.4
        add("FATAL", f"Track record starts ~{months:.0f} months before the account joined/was "
                     f"verified ({start} vs {joined}) — only post-{joined} data is verified.")
    ref = joined or start
    if ref:
        months = (date.today() - _d(ref)).days / 30.4
        if months < 12:
            add("CAUTION", f"Only ~{months:.0f} months of verified history (< 12).")

    n = s.get("num_trades")
    if n is not None and n < 200:
        add("CAUTION", f"Only {n} trades — too small a sample to prove skill.")

    wr, aw, al = s.get("win_rate_pct"), s.get("avg_win"), s.get("avg_loss")
    if aw and al:
        ratio = abs(al) / abs(aw)
        if wr and wr > 75 and ratio >= 3:
            add("FATAL", f"Win rate {wr:.0f}% with avg loss {ratio:.1f}x avg win — "
                         "classic no-stop/martingale payoff.")
        elif ratio >= 2:
            add("CAUTION", f"Avg loss is {ratio:.1f}x avg win.")
    elif wr and wr > 80:
        add("CAUTION", f"Win rate {wr:.0f}% — check avg loss vs avg win for hidden tail risk.")

    bal, eq = s.get("balance"), s.get("equity")
    if bal and eq:
        gap = (eq - bal) / bal * 100
        if gap < -5:
            add("FATAL" if gap < -15 else "CAUTION",
                f"Equity {abs(gap):.1f}% below balance — open losing positions not reflected "
                "in realized stats/drawdown.")

    tr, dd = s.get("total_return_pct"), s.get("max_drawdown_pct")
    if tr and dd:
        r = tr / abs(dd)
        if r > 10:
            add("CAUTION", f"Return/max-DD ratio {r:.1f} — unusually high; confirm drawdown is "
                           "equity-based, not balance-based.")

    amr = s.get("avg_monthly_return_pct")
    if amr and amr > 5:
        add("CAUTION", f"Avg monthly return {amr:.1f}% (~{((1+amr/100)**12-1)*100:.0f}%/yr) — "
                       "implies high leverage or tail risk.")

    sh = s.get("sharpe")
    if sh and sh > 3:
        add("CAUTION", f"Sharpe {sh:.2f} — rare on retail accounts; demand extra proof.")

    hold = s.get("avg_hold_minutes")
    if hold is not None and hold < 15:
        add("CAUTION", f"Avg hold {hold} min — copier slippage will eat much of the edge.")

    mr = s.get("monthly_returns_pct")
    if mr and len(mr) >= 4 and tr:
        top2 = sum(sorted(mr, reverse=True)[:2])
        total = sum(mr)
        if total > 0 and top2 / total > 0.6:
            add("CAUTION", f"Top 2 months = {top2/total*100:.0f}% of summed returns — luck concentration.")

    if dd:
        add("INFO", f"Plan for a future drawdown of at least {2*abs(dd):.0f}% (2x historical max).")
    return flags


def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    flags = check(json.loads(raw))
    order = {"FATAL": 0, "CAUTION": 1, "INFO": 2}
    icon = {"FATAL": "🔴", "CAUTION": "🟡", "INFO": "ℹ️"}
    for sev, msg in sorted(flags, key=lambda f: order[f[0]]):
        print(f"{icon[sev]} {sev}: {msg}")
    fatal = sum(1 for f in flags if f[0] == "FATAL")
    caution = sum(1 for f in flags if f[0] == "CAUTION")
    print(f"\nSummary: {fatal} fatal, {caution} caution. "
          "Checklist only — combine with broker, incentive, and curve-shape review.")


if __name__ == "__main__":
    main()
