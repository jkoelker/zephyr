#!/usr/bin/env -S uv run --with pandas python
"""
Calculate Average True Range (ATR) from OHLC candle data.

Usage:
    ./calculate_atr.py '<json_array>' --period 10
"""

import sys
import json
import argparse

import pandas as pd


def calculate_atr(candles: list[dict], period: int = 10) -> dict:
    """Calculate ATR from OHLC candle data.

    Args:
        candles: List of dicts with 'open', 'high', 'low', 'close' keys
        period: Number of periods for ATR calculation

    Returns:
        Dict with atr, half_atr, double_atr, and period

    Raises:
        ValueError: If insufficient data or missing required fields
    """
    if len(candles) < period + 1:
        raise ValueError(f"Need at least {period + 1} candles, got {len(candles)}")

    required_fields = ["open", "high", "low", "close"]
    for i, candle in enumerate(candles):
        missing = [f for f in required_fields if f not in candle]
        if missing:
            raise ValueError(f"Candle {i} missing fields: {', '.join(missing)}")

    df = pd.DataFrame(candles)
    df["prev_close"] = df["close"].shift(1)

    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["prev_close"]).abs()
    low_close = (df["low"] - df["prev_close"]).abs()
    df["tr"] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    tr_clean = df["tr"].dropna()
    atr_value = tr_clean.tail(period).mean()

    return {
        "atr": round(atr_value, 2),
        "half_atr": round(atr_value * 0.5, 2),
        "double_atr": round(atr_value * 2.0, 2),
        "period": period,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate ATR from OHLC candle data")
    parser.add_argument("candles", help="JSON array of candles")
    parser.add_argument(
        "--period", type=int, default=10, help="Number of periods (default: 10)"
    )
    args = parser.parse_args()

    try:
        candles = json.loads(args.candles)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_atr(candles, args.period)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
