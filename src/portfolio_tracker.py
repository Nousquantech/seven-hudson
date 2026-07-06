"""
portfolio_tracker.py — Track Seven Hudson's portfolio performance over time.

Log entries are stored in a simple CSV (portfolio_log.csv) with columns:
    date, total_value, net_contributions

The tool computes:
  - Investment gain/loss (value change excluding contributions)
  - Cumulative rate of return
  - A simple comparison against a benchmark return (e.g. S&P 500) that you supply

Usage (as a script):
    python portfolio_tracker.py log.csv --benchmark 9.98

Usage (as a library):
    from portfolio_tracker import load_log, compute_performance
"""

import sys
import csv
from datetime import datetime


def load_log(csv_path: str) -> list:
    """Load portfolio log entries from a CSV file, sorted by date."""
    entries = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                "date": datetime.strptime(row["date"], "%Y-%m-%d"),
                "total_value": float(row["total_value"]),
                "net_contributions": float(row["net_contributions"]),
            })
    entries.sort(key=lambda e: e["date"])
    return entries


def compute_performance(entries: list, benchmark_return_pct: float = None) -> dict:
    """
    Compute basic performance stats from a list of log entries.

    The first entry is treated as the starting point (beginning value + contributions to date).
    The last entry is the current/ending point.
    """
    if len(entries) < 2:
        raise ValueError("Need at least two log entries to compute performance.")

    start = entries[0]
    end = entries[-1]

    beginning_value = start["total_value"]
    ending_value = end["total_value"]
    net_contributions_period = end["net_contributions"] - start["net_contributions"]

    investment_gain = ending_value - beginning_value - net_contributions_period
    # Simple return, not time-weighted — good enough for a small personal account,
    # but note this in reports since it's a simplification vs. true TWR/IRR.
    cumulative_return_pct = (investment_gain / beginning_value) * 100 if beginning_value else 0

    result = {
        "start_date": start["date"].strftime("%Y-%m-%d"),
        "end_date": end["date"].strftime("%Y-%m-%d"),
        "beginning_value": round(beginning_value, 2),
        "ending_value": round(ending_value, 2),
        "net_contributions_period": round(net_contributions_period, 2),
        "investment_gain": round(investment_gain, 2),
        "cumulative_return_pct": round(cumulative_return_pct, 2),
    }

    if benchmark_return_pct is not None:
        result["benchmark_return_pct"] = benchmark_return_pct
        result["excess_return_pct"] = round(cumulative_return_pct - benchmark_return_pct, 2)

    return result


def print_performance_report(csv_path: str, benchmark_return_pct: float = None):
    entries = load_log(csv_path)
    perf = compute_performance(entries, benchmark_return_pct)

    print(f"\n=== Seven Hudson Performance: {perf['start_date']} to {perf['end_date']} ===")
    print(f"Beginning Value:      ${perf['beginning_value']:,.2f}")
    print(f"Net Contributions:    ${perf['net_contributions_period']:,.2f}")
    print(f"Ending Value:         ${perf['ending_value']:,.2f}")
    print(f"Investment Gain/Loss: ${perf['investment_gain']:,.2f}")
    print(f"Cumulative Return:    {perf['cumulative_return_pct']}%")

    if benchmark_return_pct is not None:
        print(f"Benchmark Return:     {perf['benchmark_return_pct']}%")
        sign = "+" if perf["excess_return_pct"] >= 0 else ""
        print(f"Excess Return:        {sign}{perf['excess_return_pct']}%")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python portfolio_tracker.py LOG_CSV_PATH [--benchmark X.XX]")
        sys.exit(1)

    csv_path = sys.argv[1]
    benchmark = None
    if "--benchmark" in sys.argv:
        idx = sys.argv.index("--benchmark")
        benchmark = float(sys.argv[idx + 1])

    print_performance_report(csv_path, benchmark)
