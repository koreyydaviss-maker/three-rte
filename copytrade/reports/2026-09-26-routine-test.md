# Copy-trade watch report: 2026-09-26 (routine test)

_A test of the full routine pipeline. The scheduled trigger was fired at 19:37 UTC, but its run never reached the session, so the steps below were run by hand in the same order. It's Saturday and markets are closed, so no change was expected._

## What changed since last run
- **Nothing.** Returns, risk scores and holdings for all four eToro traders match the 2026-09-26 live run exactly. No positions were opened or closed.
- **Paper test:** Jeppe copy **$960.00** (+$0.00), CPH copy **$750.00** (+$0.00). 0 simulated trades, no stop-loss hits.
- Verdicts unchanged. Small test allocation: @JeppeKirkBonde, @CPHequities. Watch only: @thomaspj. Avoid: @jaynemesis, ReversionTrader.

## Pipeline check
| Step | Result |
|---|---|
| git pull | ✅ up to date |
| Bullaware fetch (4 traders) | ✅ all loaded |
| eToro direct | ❌ Cloudflare bot check (expected) |
| Verdict re-run | ✅ no changes |
| Paper update (`update.py`) | ✅ ran, 0 trades, history row `2026-09-26-test` |
| Dashboard build + republish | ✅ |
| Commit + push | ✅ |
| Scheduled trigger delivery | ⚠️ test fire didn't start a run; recheck on the Monday 08:45 ET run |

Full details: see `2026-09-26-live.md`.

_Education, not financial advice._
