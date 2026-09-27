#!/usr/bin/env python3
"""Paper-trade (simulated) copies of the traders in copytrade/paper/portfolio.json.

No real money, no broker, no logins. Holdings and prices come from public
Bullaware pages (eToro data). Each run:
  1. Fetches the trader's current holdings and prices.
  2. Marks the paper copy to market (value = shares x current price + cash).
  3. Mirrors the trader like eToro CopyTrader would: if they opened, closed or
     resized a position, rebalance the paper copy to their current weights and
     log each simulated trade.
  4. Checks the copy stop-loss.
Writes portfolio.json (state), history.csv (one row per copy per run),
trades.csv (simulated trades) and status.json (for the dashboard).

Usage: python copytrade/paper/update.py [--init] [--date YYYY-MM-DD]
  --init  start fresh copies from the "copies" config in portfolio.json.

Limits: prices are in each instrument's own currency and FX moves are ignored;
fills are at the last price with no spread or slippage (real copies do worse).
"""
import csv
import json
import os
import re
import sys
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "portfolio.json")
REBALANCE_THRESHOLD = 1.0  # percentage points of weight drift before we mirror a change


def fetch(trader):
    req = urllib.request.Request(f"https://bullaware.com/etoro/{trader}",
                                 headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    raw = raw.replace('\\"', '"')
    m = re.search(r'"positions":(\[\{"direction".*?\])', raw)
    if not m:
        raise RuntimeError(f"no positions found for {trader}")
    positions = json.loads(m.group(1))
    prices = {s: float(p) for s, p in
              re.findall(r'"symbol":"([^"]+)"[^{}]{0,200}?"price":([\d.]+)', raw)}
    weights = {p["symbol"]: p["value"] for p in positions if p["direction"] == 1}
    missing = [s for s in weights if s not in prices]
    if missing:
        raise RuntimeError(f"{trader}: no price for {missing}")
    return weights, prices


def value(copy, prices):
    return copy["cash"] + sum(sh * prices.get(s, copy["last_price"].get(s, 0))
                              for s, sh in copy["shares"].items())


def rebalance(copy, weights, prices, total, today, trades):
    wsum = sum(weights.values()) or 1
    target = {s: total * w / wsum / prices[s] for s, w in weights.items()}
    for s in sorted(set(copy["shares"]) | set(target)):
        old, new = copy["shares"].get(s, 0.0), target.get(s, 0.0)
        if abs(new - old) * prices.get(s, 0) < 0.01:
            continue
        action = ("OPEN" if old == 0 else "CLOSE" if new == 0 else
                  "ADD" if new > old else "TRIM")
        trades.append([today, copy["trader"], action, s, round(new - old, 6),
                       prices.get(s, copy["last_price"].get(s)),
                       round((new - old) * prices.get(s, 0), 2)])
    copy["shares"] = {s: sh for s, sh in target.items() if sh > 0}
    copy["cash"] = 0.0
    copy["weights"] = {s: round(w / wsum * 100, 3) for s, w in weights.items()}


def main():
    args = sys.argv[1:]
    today = args[args.index("--date") + 1] if "--date" in args else date.today().isoformat()
    state = json.load(open(STATE))
    trades, rows = [], []

    for copy in state["copies"]:
        weights, prices = fetch(copy["trader"])
        if "--init" in args or not copy.get("shares"):
            copy.update(start_date=today, shares={}, cash=copy["amount"], last_price={},
                        weights={}, stopped=False, peak=copy["amount"])
            rebalance(copy, weights, prices, copy["amount"], today, trades)
        elif not copy.get("stopped"):
            total = value(copy, prices)
            cur = {s: w / (sum(weights.values()) or 1) * 100 for s, w in weights.items()}
            changed = set(cur) != set(copy["weights"]) or any(
                abs(cur[s] - copy["weights"].get(s, 0)) > REBALANCE_THRESHOLD for s in cur)
            if changed:
                rebalance(copy, weights, prices, total, today, trades)
        copy["last_price"] = {s: prices[s] for s in copy["shares"] if s in prices}
        v = value(copy, prices)
        copy["peak"] = max(copy.get("peak", v), v)
        pnl = v - copy["amount"]
        if not copy.get("stopped") and pnl <= -copy["stop_loss"]:
            copy["stopped"] = True
            trades.append([today, copy["trader"], "STOP-LOSS: close all", "*", "", "", round(v, 2)])
            copy["cash"], copy["shares"] = v, {}
        copy["value"] = round(v, 2)
        copy["updated"] = today
        rows.append([today, copy["trader"], round(v, 2), round(pnl, 2),
                     round(pnl / copy["amount"] * 100, 2),
                     round((v / copy["peak"] - 1) * 100, 2), copy.get("stopped", False)])

    json.dump(state, open(STATE, "w"), indent=1)

    hist = os.path.join(HERE, "history.csv")
    new = not os.path.exists(hist) or "--init" in args
    with open(hist, "w" if new else "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "trader", "value", "pnl", "pnl_pct", "from_peak_pct", "stopped"])
        w.writerows(rows)

    tpath = os.path.join(HERE, "trades.csv")
    new = not os.path.exists(tpath) or "--init" in args
    with open(tpath, "w" if new else "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "trader", "action", "symbol", "shares", "price", "usd"])
        w.writerows(trades)

    history = list(csv.DictReader(open(hist)))
    status = {"updated": today, "copies": [], "trades_today": trades}
    for c in state["copies"]:
        status["copies"].append({
            "trader": c["trader"], "amount": c["amount"], "stop_loss": c["stop_loss"],
            "start_date": c["start_date"], "value": c["value"], "stopped": c.get("stopped", False),
            "holdings": len(c["shares"]),
            "history": [[h["date"], float(h["value"])] for h in history if h["trader"] == c["trader"]],
        })
    json.dump(status, open(os.path.join(HERE, "status.json"), "w"), indent=1)

    for r in rows:
        print(f"{r[1]}: ${r[2]:,.2f}  P/L {r[3]:+,.2f} ({r[4]:+.2f}%)  from peak {r[5]:+.2f}%"
              f"{'  STOPPED' if r[6] else ''}")
    print(f"{len(trades)} simulated trades logged")


if __name__ == "__main__":
    main()
