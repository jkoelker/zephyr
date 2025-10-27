#!/usr/bin/env -S uv run --with pandas python
"""
Calculate Relative Strength Index (RSI) from price data.

Usage:
    ./calculate_rsi.py '<json_array>' --period 14
    ./calculate_rsi.py '<json_array>' --overbought 80 --oversold 20
"""

import sys
import json
import argparse

import pandas as pd

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


def get_rsi_signal(
    rsi_value: float, overbought: int = RSI_OVERBOUGHT, oversold: int = RSI_OVERSOLD
) -> str:
    """Determine RSI signal based on thresholds.

    Args:
        rsi_value: Current RSI value
        overbought: Overbought threshold (default: 70)
        oversold: Oversold threshold (default: 30)

    Returns:
        Signal string: 'overbought', 'oversold', or 'neutral'
    """
    if rsi_value > overbought:
        return "overbought"
    if rsi_value < oversold:
        return "oversold"
    return "neutral"


def calculate_rsi(
    prices: list[float],
    period: int = 14,
    overbought: int = RSI_OVERBOUGHT,
    oversold: int = RSI_OVERSOLD,
) -> dict:
    """Calculate RSI from price data.

    Args:
        prices: List of close prices
        period: Number of periods for RSI calculation
        overbought: Overbought threshold (default: 70)
        oversold: Oversold threshold (default: 30)

    Returns:
        Dict with rsi, period, and signal

    Raises:
        ValueError: If insufficient data
    """
    if len(prices) < period + 1:
        raise ValueError(f"Need at least {period + 1} prices, got {len(prices)}")

    series = pd.Series(prices)
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi_series = 100 - (100 / (1 + rs))
    rsi_value = rsi_series.iloc[-1]

    return {
        "rsi": round(rsi_value, 2),
        "period": period,
        "signal": get_rsi_signal(rsi_value, overbought, oversold),
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate RSI from price data")
    parser.add_argument("prices", help="JSON array of prices")
    parser.add_argument(
        "--period", type=int, default=14, help="Number of periods (default: 14)"
    )
    parser.add_argument(
        "--overbought",
        type=int,
        default=RSI_OVERBOUGHT,
        help=f"Overbought threshold (default: {RSI_OVERBOUGHT})",
    )
    parser.add_argument(
        "--oversold",
        type=int,
        default=RSI_OVERSOLD,
        help=f"Oversold threshold (default: {RSI_OVERSOLD})",
    )
    args = parser.parse_args()

    try:
        prices = json.loads(args.prices)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_rsi(prices, args.period, args.overbought, args.oversold)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
