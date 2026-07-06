# Seven Hudson

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

**A Python toolkit for value-investing analysis** — company valuation (DCF, P/E, P/B),
multi-stock screening, and portfolio performance tracking.

Built and actively used to manage my own investment portfolio, Seven Hudson, which
returned **19.95%** vs. the S&P 500's 9.98% over its first tracked 6 months (see example below).

This repo serves two purposes:
1. Tracking and analyzing my own investment portfolio ("Seven Hudson").
2. A demonstration of practical financial data analysis skills in Python —
   available for freelance data analysis / research work.

## What's inside

- **`src/valuation.py`** — Pulls relative valuation metrics (P/E, P/B, EV/EBITDA)
  for any public stock ticker, and runs a simple Discounted Cash Flow (DCF) model
  to estimate intrinsic value per share.

- **`src/screener.py`** — Screens a list of tickers against classic value-investing
  thresholds (low P/E, low P/B, manageable debt, positive free cash flow) and ranks
  them by how many criteria they pass.

- **`src/portfolio_tracker.py`** — Tracks portfolio performance over time from a
  simple CSV log (date, total value, net contributions), computing gain/loss,
  cumulative return, and comparison against a benchmark (e.g. S&P 500).

## Example: Seven Hudson performance (Jan–Jul 2026)

Using `examples/portfolio_log_sample.csv`:

```
=== Seven Hudson Performance: 2026-01-01 to 2026-07-04 ===
Beginning Value:      $2,710.66
Net Contributions:    $427.37
Ending Value:         $3,678.75
Investment Gain/Loss: $540.72
Cumulative Return:    19.95%
Benchmark Return:     9.98%
Excess Return:        +9.97%
```

(Note: this is a simple return calculation, not time-weighted — a reasonable
approximation for a small personal account, but not the same method brokerages
use for official reporting.)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

**Valuation report for a single stock:**
```bash
cd src
python valuation.py AAPL
```

**Screen multiple stocks for value characteristics:**
```bash
cd src
python screener.py AAPL MSFT KO JNJ XOM
```

**Track portfolio performance:**
```bash
cd src
python portfolio_tracker.py ../examples/portfolio_log_sample.csv --benchmark 9.98
```

To track your own portfolio, create a CSV with columns `date,total_value,net_contributions`
and add a new row each time you check your balance (weekly or monthly is usually enough).

## Roadmap

- [ ] Add historical price charting
- [ ] Add comparable company analysis (comps) alongside DCF
- [ ] Export screener results to CSV
- [ ] Add simple backtesting for value-based stock selection rules

## Disclaimer

This is a personal project for educational and research purposes. Nothing here is
financial advice. All DCF assumptions (growth rate, discount rate) are simplified
and should be adjusted per company/context — this is a starting framework, not a
finished valuation model.
