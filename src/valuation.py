"""
valuation.py — Core company valuation tools for Seven Hudson.

Provides:
  - Relative valuation metrics (P/E, P/B, EV/EBITDA)
  - A simple Discounted Cash Flow (DCF) intrinsic value calculator

Usage (as a script):
    python valuation.py AAPL

Usage (as a library):
    from valuation import get_relative_metrics, dcf_intrinsic_value
"""

import sys
import yfinance as yf


def get_relative_metrics(ticker: str) -> dict:
    """
    Pull key relative valuation metrics for a given stock ticker.

    Returns a dict with P/E, P/B, EV/EBITDA, and a few supporting fields.
    Any metric Yahoo Finance doesn't provide will come back as None.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "ticker": ticker.upper(),
        "name": info.get("longName"),
        "price": info.get("currentPrice"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb_ratio": info.get("priceToBook"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),
        "profit_margin": info.get("profitMargins"),
        "debt_to_equity": info.get("debtToEquity"),
        "free_cash_flow": info.get("freeCashflow"),
        "market_cap": info.get("marketCap"),
    }


def dcf_intrinsic_value(
    free_cash_flow: float,
    growth_rate: float,
    discount_rate: float,
    terminal_growth: float,
    years: int = 5,
    shares_outstanding: float = None,
) -> dict:
    """
    Very simple single-stage-growth-then-terminal-value DCF model.

    Args:
        free_cash_flow: most recent annual FCF (in dollars)
        growth_rate: assumed annual FCF growth rate during projection period (e.g. 0.08 for 8%)
        discount_rate: discount rate / required return (e.g. 0.10 for 10%)
        terminal_growth: perpetual growth rate after projection period (e.g. 0.025 for 2.5%)
        years: number of years to project explicitly (default 5)
        shares_outstanding: if provided, also returns per-share intrinsic value

    Returns:
        dict with projected cash flows, PV of each, terminal value, and total intrinsic value.
    """
    if discount_rate <= terminal_growth:
        raise ValueError("Discount rate must be greater than terminal growth rate.")

    projected_fcf = []
    pv_fcf = []
    fcf = free_cash_flow

    for year in range(1, years + 1):
        fcf = fcf * (1 + growth_rate)
        pv = fcf / ((1 + discount_rate) ** year)
        projected_fcf.append(round(fcf, 2))
        pv_fcf.append(round(pv, 2))

    terminal_value = (fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    pv_terminal_value = terminal_value / ((1 + discount_rate) ** years)

    intrinsic_value = sum(pv_fcf) + pv_terminal_value

    result = {
        "projected_fcf": projected_fcf,
        "pv_of_projected_fcf": pv_fcf,
        "terminal_value": round(terminal_value, 2),
        "pv_of_terminal_value": round(pv_terminal_value, 2),
        "intrinsic_value_total": round(intrinsic_value, 2),
    }

    if shares_outstanding:
        result["intrinsic_value_per_share"] = round(intrinsic_value / shares_outstanding, 2)

    return result


def print_report(ticker: str):
    """Print a readable valuation report for a given ticker to the console."""
    metrics = get_relative_metrics(ticker)

    print(f"\n=== Valuation Report: {metrics['name']} ({metrics['ticker']}) ===")
    print(f"Price:              ${metrics['price']}")
    print(f"P/E Ratio:          {metrics['pe_ratio']}")
    print(f"Forward P/E:        {metrics['forward_pe']}")
    print(f"P/B Ratio:          {metrics['pb_ratio']}")
    print(f"EV/EBITDA:          {metrics['ev_to_ebitda']}")
    print(f"Profit Margin:      {metrics['profit_margin']}")
    print(f"Debt/Equity:        {metrics['debt_to_equity']}")
    print(f"Free Cash Flow:     {metrics['free_cash_flow']}")
    print(f"Market Cap:         {metrics['market_cap']}")

    if metrics["free_cash_flow"]:
        stock = yf.Ticker(ticker)
        shares = stock.info.get("sharesOutstanding")
        dcf = dcf_intrinsic_value(
            free_cash_flow=metrics["free_cash_flow"],
            growth_rate=0.08,
            discount_rate=0.10,
            terminal_growth=0.025,
            years=5,
            shares_outstanding=shares,
        )
        print("\n--- Simple DCF Estimate (8% growth, 10% discount, 2.5% terminal) ---")
        print(f"Intrinsic Value (Total):     ${dcf['intrinsic_value_total']:,.0f}")
        if "intrinsic_value_per_share" in dcf:
            print(f"Intrinsic Value (Per Share): ${dcf['intrinsic_value_per_share']}")
            if metrics["price"]:
                upside = (dcf["intrinsic_value_per_share"] / metrics["price"] - 1) * 100
                print(f"Implied Upside/Downside:     {upside:.1f}%")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python valuation.py TICKER")
        sys.exit(1)

    print_report(sys.argv[1])
