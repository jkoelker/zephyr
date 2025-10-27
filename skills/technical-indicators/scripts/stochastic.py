#!/usr/bin/env -S uv run --with pandas python
"""
Calculate Stochastic Oscillator from OHLC candle data.

Usage:
    ./stochastic.py '<json_array>'
    ./stochastic.py '<json_array>' --k_period 14 --d_period 3
"""

import sys
import json
import argparse

import pandas as pd


def calculate_stochastic(
    candles: list[dict],
    k_period: int = 14,
    d_period: int = 3,
    overbought: int = 80,
    oversold: int = 20,
) -> dict:
    """Calculate Stochastic Oscillator from OHLC data.

    Args:
        candles: List of dicts with 'high', 'low', 'close' keys
        k_period: Period for %K calculation (default: 14)
        d_period: Period for %D (signal line) calculation (default: 3)
        overbought: Overbought threshold (default: 80)
        oversold: Oversold threshold (default: 20)

    Returns:
        Dict with %K, %D, and signal

    Raises:
        ValueError: If insufficient data or missing required fields
    """
    min_required = k_period + d_period - 1
    if len(candles) < min_required:
        raise ValueError(f"Need at least {min_required} candles, got {len(candles)}")

    required_fields = ["high", "low", "close"]
    for i, candle in enumerate(candles):
        missing = [f for f in required_fields if f not in candle]
        if missing:
            raise ValueError(f"Candle {i} missing fields: {', '.join(missing)}")

    df = pd.DataFrame(candles)

    # Calculate %K (Fast Stochastic)
    low_min = df["low"].rolling(window=k_period).min()
    high_max = df["high"].rolling(window=k_period).max()

    df["k_percent"] = 100 * ((df["close"] - low_min) / (high_max - low_min))

    # Calculate %D (Slow Stochastic - SMA of %K)
    df["d_percent"] = df["k_percent"].rolling(window=d_period).mean()

    # Get latest values
    k_value = df["k_percent"].iloc[-1]
    d_value = df["d_percent"].iloc[-1]

    # Previous values for crossover detection
    prev_k = df["k_percent"].iloc[-2]
    prev_d = df["d_percent"].iloc[-2]

    # Determine signal
    signal = "neutral"

    # Check for crossovers
    if prev_k <= prev_d and k_value > d_value:
        if k_value < oversold:
            signal = "bullish_crossover_oversold"
        else:
            signal = "bullish_crossover"
    elif prev_k >= prev_d and k_value < d_value:
        if k_value > overbought:
            signal = "bearish_crossover_overbought"
        else:
            signal = "bearish_crossover"
    # Check for overbought/oversold conditions
    elif k_value > overbought and d_value > overbought:
        signal = "overbought"
    elif k_value < oversold and d_value < oversold:
        signal = "oversold"
    elif k_value > overbought:
        signal = "near_overbought"
    elif k_value < oversold:
        signal = "near_oversold"

    return {
        "k_percent": round(k_value, 2),
        "d_percent": round(d_value, 2),
        "signal": signal,
        "k_period": k_period,
        "d_period": d_period,
        "overbought": overbought,
        "oversold": oversold,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate Stochastic Oscillator from OHLC data"
    )
    parser.add_argument("candles", help="JSON array of candles with OHLC data")
    parser.add_argument(
        "--k_period", type=int, default=14, help="Period for %%K (default: 14)"
    )
    parser.add_argument(
        "--d_period", type=int, default=3, help="Period for %%D (default: 3)"
    )
    parser.add_argument(
        "--overbought", type=int, default=80, help="Overbought threshold (default: 80)"
    )
    parser.add_argument(
        "--oversold", type=int, default=20, help="Oversold threshold (default: 20)"
    )
    args = parser.parse_args()

    try:
        candles = json.loads(args.candles)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_stochastic(
            candles, args.k_period, args.d_period, args.overbought, args.oversold
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()