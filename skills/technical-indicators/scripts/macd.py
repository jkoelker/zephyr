#!/usr/bin/env -S uv run --with pandas python
"""
Calculate MACD (Moving Average Convergence Divergence) from price data.

Usage:
    ./macd.py '<json_array>'
    ./macd.py '<json_array>' --fast 12 --slow 26 --signal 9
"""

import sys
import json
import argparse

import pandas as pd


def calculate_macd(
    prices: list[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9
) -> dict:
    """Calculate MACD indicator.

    Args:
        prices: List of close prices
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)

    Returns:
        Dict with macd, signal, histogram, and crossover signal

    Raises:
        ValueError: If insufficient data
    """
    min_required = slow_period + signal_period
    if len(prices) < min_required:
        raise ValueError(f"Need at least {min_required} prices, got {len(prices)}")

    series = pd.Series(prices)

    # Calculate EMAs
    ema_fast = series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = series.ewm(span=slow_period, adjust=False).mean()

    # MACD line
    macd_line = ema_fast - ema_slow

    # Signal line (EMA of MACD)
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    # MACD histogram
    histogram = macd_line - signal_line

    # Get latest values
    macd_value = macd_line.iloc[-1]
    signal_value = signal_line.iloc[-1]
    histogram_value = histogram.iloc[-1]

    # Previous values for crossover detection
    prev_macd = macd_line.iloc[-2]
    prev_signal = signal_line.iloc[-2]
    prev_histogram = histogram.iloc[-2]

    # Determine signal
    signal = "neutral"

    # Check for crossovers
    if prev_macd <= prev_signal and macd_value > signal_value:
        signal = "bullish_crossover"
    elif prev_macd >= prev_signal and macd_value < signal_value:
        signal = "bearish_crossover"
    # Check histogram momentum
    elif histogram_value > 0 and histogram_value > prev_histogram:
        signal = "bullish_momentum"
    elif histogram_value < 0 and histogram_value < prev_histogram:
        signal = "bearish_momentum"
    elif histogram_value > 0:
        signal = "bullish"
    elif histogram_value < 0:
        signal = "bearish"

    return {
        "macd": round(macd_value, 3),
        "signal": round(signal_value, 3),
        "histogram": round(histogram_value, 3),
        "crossover_signal": signal,
        "fast_period": fast_period,
        "slow_period": slow_period,
        "signal_period": signal_period,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate MACD from price data")
    parser.add_argument("prices", help="JSON array of prices")
    parser.add_argument(
        "--fast", type=int, default=12, help="Fast EMA period (default: 12)"
    )
    parser.add_argument(
        "--slow", type=int, default=26, help="Slow EMA period (default: 26)"
    )
    parser.add_argument(
        "--signal", type=int, default=9, help="Signal EMA period (default: 9)"
    )
    args = parser.parse_args()

    try:
        prices = json.loads(args.prices)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_macd(prices, args.fast, args.slow, args.signal)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()