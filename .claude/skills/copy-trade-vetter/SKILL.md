---
name: copy-trade-vetter
description: Vet a trading strategy, signal provider, or "top trader" from a copy-trading leaderboard (AlphaLedger, Myfxbook, Darwinex, MQL5 Signals, eToro CopyTrader, ZuluTrade, FXBlue, prop-firm leaderboards, Discord/Telegram signal groups) before the user copies it or puts money in. Produces a red-flag audit, a verdict (avoid / watch / small test allocation), and a position-sizing plan. Use this whenever the user shares a leaderboard screenshot, a strategy link, a trader's stats (return, win rate, drawdown, Sharpe, "Alpha Score"), a TikTok/YouTube/social post pitching copy trading or "just copy and paste what they trade", or asks "should I copy this trader", "is this legit", "which strategy should I follow" — even if they don't say "vet" or "due diligence".
---

# Copy-Trade Vetter

Copy-trading leaderboards are marketed as "just copy the best traders — the stats come straight from the broker, so you know it's legit." Broker-verified numbers prove the trades *happened*; they do not prove the strategy has an edge, will keep working, or will perform the same for the copier. Your job is to close that gap: turn a shiny leaderboard row into an honest risk picture the user can act on.

You are not a licensed financial adviser, and the user is the one risking money. Be direct and concrete rather than preachy — one short line noting this is education, not advice, is enough.

## Workflow

### 1. Collect the stats

Pull whatever is available from what the user shared (screenshots, links, pasted text, a video). If you can browse, open the strategy page. Capture as many of these as you can, and write "unknown" for the rest — missing data is itself a finding:

- Platform/leaderboard, strategy name, provider
- Broker, broker regulation (jurisdiction), account type (real vs demo, personal vs prop-firm/funded)
- Track-record start date **and** the date the account joined/was verified
- Total return, YTD return, avg monthly return, monthly returns table if shown
- Max drawdown (equity-based if possible — balance-based hides open losses)
- Win rate, avg win, avg loss (or profit factor), number of trades, avg holding time
- Sharpe/Sortino/Calmar, any platform score ("Alpha Score", "AI Score", etc.)
- Balance vs equity right now, deposits/withdrawals
- Instruments traded, leverage, lot sizes over time
- Copier count / AUM following, subscription fee or profit share
- Any audit claims (e.g., "US CPA Audit" column) and whether they're actually ticked for this strategy

If the user gave you numbers, run `scripts/red_flags.py` on them (see below) to get a consistent first pass, then add your own judgment.

### 2. Run the red-flag checks

Read `references/red_flags.md` for the full checklist with explanations. The high-value ones:

1. **History mismatch** — equity curve starts before the account's join/verification date → earlier history may be imported, backfilled, or from a different account.
2. **Too short / too few trades** — under ~12 months or under ~200 trades can't distinguish skill from luck, especially in one market regime.
3. **Martingale / grid / no-stop-loss signature** — very high win rate (>80%) with average loss much bigger than average win, a smooth staircase equity curve, lot sizes that grow after losses, or equity sitting well below balance (floating losses parked). These blow up eventually; smoothness is the warning, not the reassurance.
4. **Return/drawdown doesn't add up** — e.g., 200% return with a 12% max drawdown on a leveraged FX account is exceptional; ask whether drawdown is balance-based or on closed trades only.
5. **Balance ≠ equity** — a gap means open positions are losing or winning right now; a large negative gap is a live risk.
6. **Survivorship / leaderboard selection** — the top of any leaderboard is the lucky tail of thousands of strategies; the ones that blew up are gone. Ranking by a proprietary score doesn't fix this.
7. **Broker & verification** — offshore/unregulated broker, demo account, or "audit" column not actually ticked.
8. **Capacity & copier slippage** — copier fills come later and at worse prices; scalpers and news traders degrade the most. Minimum copy size and leverage mismatches change the risk profile.
9. **Incentives** — who profits from the user copying? Affiliate/referral links, IB rebates on volume, paid Discord upsells, "save this before it gets taken down" urgency.

### 3. Decide

Give one verdict:

- **Avoid** — any blow-up signature (martingale/grid, no stops), history that can't be verified, or an obvious scam pattern.
- **Watch only** — no fatal flags but not enough evidence yet (short history, few trades, one regime). Say what would change your mind (e.g., "another 6 months and a drawdown it recovers from").
- **Small test allocation** — long, verified, consistent record with reasonable risk. Still size it as money the user can lose.

### 4. Sizing plan (only for "small test allocation", or if the user insists)

- Size from drawdown, not return: assume the future max drawdown is **2× the historical max** at minimum. Allocation = the dollar loss the user can stomach ÷ (2 × historical max DD).
- Cap any single copied strategy at a small slice of total savings; never borrowed money or money needed within a year.
- Set a hard stop: an account-level equity stop on the copy (most platforms support one) at the loss level the user chose.
- Diversify across uncorrelated strategies rather than piling into the #1 row.
- Review monthly; kill the copy if live results diverge materially from the track record or behavior changes (bigger lots, new instruments, no stops).

## Output format

```
# Copy-trade check: <strategy> on <platform>

**Verdict:** Avoid | Watch only | Small test allocation — <one-line reason>

## What the numbers say
<table of the stats you found, with "unknown" where missing>

## Red flags
- 🔴 <fatal flag> — <why it matters, with the specific number>
- 🟡 <caution flag> — ...
(or "None found" for a category)

## What would change the verdict
<concrete evidence to look for>

## If you still want to try it
<sizing plan with the user's numbers if given>

_Education, not financial advice._
```

Keep it tight — the user wants a decision, not a lecture. Quote the actual numbers ("76% win rate with avg loss 3× avg win") rather than generic warnings.

## The red_flags.py helper

`scripts/red_flags.py` takes a JSON object of stats (any subset) and prints triggered flags with severity. Use it for a consistent first pass:

```bash
python scripts/red_flags.py '{"total_return_pct": 209.2, "max_drawdown_pct": 12.26, "win_rate_pct": 76.38, "track_record_start": "2025-01-16", "joined_date": "2026-02-09", "balance": 252344.61, "equity": 233441.43, "num_trades": 1200}'
```

Recognized keys are listed at the top of the script. The script is a checklist, not a verdict — combine its output with the qualitative checks above (incentives, broker, curve shape) before deciding.
