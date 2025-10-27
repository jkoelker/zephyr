#!/usr/bin/env -S uv run --with pandas python
"""
Calculate Exponential Moving Average (EMA) from price data.

Usage:
    ./ema.py '<json_array>' --period 12
    ./ema.py '<json_array>' --period 26 --smoothing 2.0
"""

import sys
import json
import argparse

import pandas as pd


def calculate_ema(prices: list[float], period: int = 12, smoothing: float = 2.0) -> dict:
    """Calculate Exponential Moving Average.

    Args:
        prices: List of close prices
        period: Number of periods for EMA calculation
        smoothing: Smoothing factor (default: 2.0)

    Returns:
        Dict with ema, period, and price_trend

    Raises:
        ValueError: If insufficient data
    """
    if len(prices) < period:
        raise ValueError(f"Need at least {period} prices, got {len(prices)}")

    series = pd.Series(prices)
    ema_value = series.ewm(span=period, adjust=False).mean().iloc[-1]

    # Determine trend
    current_price = prices[-1]
    if current_price > ema_value:
        trend = "above_ema"
    elif current_price < ema_value:
        trend = "below_ema"
    else:
        trend = "at_ema"

    return {
        "ema": round(ema_value, 2),
        "period": period,
        "current_price": round(current_price, 2),
        "price_trend": trend,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate EMA from price data")
    parser.add_argument("prices", help="JSON array of prices")
    parser.add_argument(
        "--period", type=int, default=12, help="Number of periods (default: 12)"
    )
    parser.add_argument(
        "--smoothing", type=float, default=2.0, help="Smoothing factor (default: 2.0)"
    )
    args = parser.parse_args()

    try:
        prices = json.loads(args.prices)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_ema(prices, args.period, args.smoothing)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()