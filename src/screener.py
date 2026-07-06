"""
screener.py — Scan a list of stocks for value-investing candidates.

Screens for classic value criteria:
  - Low P/E relative to a threshold
  - Low P/B relative to a threshold
  - Positive free cash flow
  - Reasonable debt levels

Usage (as a script):
    python screener.py AAPL MSFT KO JNJ XOM

Usage (as a library):
    from screener import screen_stocks
"""

import sys
from valuation import get_relative_metrics


def screen_stocks(
    tickers: list,
    max_pe: float = 20,
    max_pb: float = 3,
    max_debt_to_equity: float = 150,
) -> list:
    """
    Screen a list of tickers against basic value-investing thresholds.

    Args:
        tickers: list of stock ticker symbols
        max_pe: maximum acceptable trailing P/E ratio
        max_pb: maximum acceptable price-to-book ratio
        max_debt_to_equity: maximum acceptable debt-to-equity (as a percentage)

    Returns:
        List of dicts, one per ticker, with metrics and a pass/fail flag per criterion.
    """
    results = []

    for ticker in tickers:
        try:
            metrics = get_relative_metrics(ticker)
        except Exception as e:
            results.append({"ticker": ticker.upper(), "error": str(e)})
            continue

        pe = metrics.get("pe_ratio")
        pb = metrics.get("pb_ratio")
        de = metrics.get("debt_to_equity")
        fcf = metrics.get("free_cash_flow")

        checks = {
            "pe_pass": (pe is not None and pe > 0 and pe <= max_pe),
            "pb_pass": (pb is not None and pb > 0 and pb <= max_pb),
            "debt_pass": (de is not None and de <= max_debt_to_equity),
            "fcf_positive": (fcf is not None and fcf > 0),
        }

        score = sum(checks.values())

        results.append({
            **metrics,
            **checks,
            "value_score": f"{score}/4",
        })

    # Sort by how many criteria each stock passes, best first
    results.sort(key=lambda r: r.get("value_score", "0/4"), reverse=True)
    return results


def print_screen_report(tickers: list, **kwargs):
    """Print a readable screening report to the console."""
    results = screen_stocks(tickers, **kwargs)

    print(f"\n{'Ticker':<8}{'Score':<8}{'P/E':<8}{'P/B':<8}{'D/E':<8}{'FCF+':<6}")
    print("-" * 46)
    for r in results:
        if "error" in r:
            print(f"{r['ticker']:<8}ERROR: {r['error']}")
            continue
        print(
            f"{r['ticker']:<8}"
            f"{r['value_score']:<8}"
            f"{str(round(r['pe_ratio'], 1)) if r['pe_ratio'] else '-':<8}"
            f"{str(round(r['pb_ratio'], 1)) if r['pb_ratio'] else '-':<8}"
            f"{str(round(r['debt_to_equity'], 1)) if r['debt_to_equity'] else '-':<8}"
            f"{'Y' if r['fcf_positive'] else 'N':<6}"
        )
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python screener.py TICKER1 TICKER2 TICKER3 ...")
        sys.exit(1)

    print_screen_report(sys.argv[1:])
