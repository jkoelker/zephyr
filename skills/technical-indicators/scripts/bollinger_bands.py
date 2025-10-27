#!/usr/bin/env -S uv run --with pandas python
"""
Calculate Bollinger Bands from price data.

Usage:
    ./bollinger_bands.py '<json_array>' --period 20 --std_dev 2
"""

import sys
import json
import argparse

import pandas as pd


def calculate_bollinger_bands(
    prices: list[float], period: int = 20, std_dev: float = 2.0
) -> dict:
    """Calculate Bollinger Bands.

    Args:
        prices: List of close prices
        period: Number of periods for moving average
        std_dev: Number of standard deviations for bands

    Returns:
        Dict with upper_band, middle_band (SMA), lower_band, bandwidth,
        percent_b, and signal

    Raises:
        ValueError: If insufficient data
    """
    if len(prices) < period:
        raise ValueError(f"Need at least {period} prices, got {len(prices)}")

    series = pd.Series(prices)

    # Middle band is SMA
    middle_band = series.rolling(window=period).mean().iloc[-1]

    # Calculate standard deviation
    std = series.rolling(window=period).std().iloc[-1]

    # Upper and lower bands
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)

    # Current price
    current_price = prices[-1]

    # Bandwidth (measure of volatility)
    bandwidth = upper_band - lower_band

    # %B (position within bands)
    if bandwidth != 0:
        percent_b = (current_price - lower_band) / bandwidth
    else:
        percent_b = 0.5

    # Determine signal
    if percent_b > 1:
        signal = "overbought"
    elif percent_b < 0:
        signal = "oversold"
    elif percent_b > 0.8:
        signal = "near_upper"
    elif percent_b < 0.2:
        signal = "near_lower"
    else:
        signal = "neutral"

    return {
        "upper_band": round(upper_band, 2),
        "middle_band": round(middle_band, 2),
        "lower_band": round(lower_band, 2),
        "bandwidth": round(bandwidth, 2),
        "percent_b": round(percent_b, 3),
        "current_price": round(current_price, 2),
        "signal": signal,
        "period": period,
        "std_dev": std_dev,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate Bollinger Bands from price data")
    parser.add_argument("prices", help="JSON array of prices")
    parser.add_argument(
        "--period", type=int, default=20, help="Number of periods (default: 20)"
    )
    parser.add_argument(
        "--std_dev", type=float, default=2.0, help="Number of standard deviations (default: 2.0)"
    )
    args = parser.parse_args()

    try:
        prices = json.loads(args.prices)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_bollinger_bands(prices, args.period, args.std_dev)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()