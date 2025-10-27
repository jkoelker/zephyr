#!/usr/bin/env -S uv run --with pandas python
"""
Calculate Simple Moving Average (SMA) from price data.

Usage:
    ./calculate_sma.py '<json_array>' --period 5
"""

import sys
import json
import argparse

import pandas as pd


def calculate_sma(prices: list[float], period: int = 20) -> dict:
    """Calculate Simple Moving Average.

    Args:
        prices: List of close prices
        period: Number of periods for SMA calculation

    Returns:
        Dict with sma and period

    Raises:
        ValueError: If insufficient data
    """
    if len(prices) < period:
        raise ValueError(f"Need at least {period} prices, got {len(prices)}")

    sma_value = pd.Series(prices).rolling(window=period).mean().iloc[-1]

    return {
        "sma": round(sma_value, 2),
        "period": period,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate SMA from price data")
    parser.add_argument("prices", help="JSON array of prices")
    parser.add_argument(
        "--period", type=int, default=20, help="Number of periods (default: 20)"
    )
    args = parser.parse_args()

    try:
        prices = json.loads(args.prices)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_sma(prices, args.period)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
