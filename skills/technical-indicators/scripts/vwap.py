#!/usr/bin/env -S uv run --with pandas python
"""
Calculate Volume Weighted Average Price (VWAP) from OHLCV candle data.

Usage:
    ./vwap.py '<json_array>'

Input format: Array of candles with 'high', 'low', 'close', 'volume' keys
"""

import sys
import json
import argparse

import pandas as pd


def calculate_vwap(candles: list[dict]) -> dict:
    """Calculate VWAP from OHLCV candle data.

    Args:
        candles: List of dicts with 'high', 'low', 'close', 'volume' keys

    Returns:
        Dict with vwap, current_price, deviation, and signal

    Raises:
        ValueError: If insufficient data or missing required fields
    """
    if len(candles) < 1:
        raise ValueError("Need at least 1 candle")

    required_fields = ["high", "low", "close", "volume"]
    for i, candle in enumerate(candles):
        missing = [f for f in required_fields if f not in candle]
        if missing:
            raise ValueError(f"Candle {i} missing fields: {', '.join(missing)}")

    df = pd.DataFrame(candles)

    # Typical price (high + low + close) / 3
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3

    # Calculate VWAP
    df["pv"] = df["typical_price"] * df["volume"]
    cumulative_pv = df["pv"].cumsum()
    cumulative_volume = df["volume"].cumsum()

    vwap_value = cumulative_pv.iloc[-1] / cumulative_volume.iloc[-1]
    current_price = df["close"].iloc[-1]

    # Calculate percentage deviation from VWAP
    deviation = ((current_price - vwap_value) / vwap_value) * 100

    # Determine signal
    if deviation > 2:
        signal = "significantly_above"
    elif deviation > 0.5:
        signal = "above"
    elif deviation < -2:
        signal = "significantly_below"
    elif deviation < -0.5:
        signal = "below"
    else:
        signal = "near_vwap"

    # Calculate upper and lower deviation bands (1 std dev)
    df["squared_diff"] = (df["typical_price"] - vwap_value) ** 2
    variance = (df["squared_diff"] * df["volume"]).sum() / df["volume"].sum()
    std_dev = variance ** 0.5

    return {
        "vwap": round(float(vwap_value), 2),
        "current_price": round(float(current_price), 2),
        "deviation_pct": round(float(deviation), 2),
        "upper_band": round(float(vwap_value + std_dev), 2),
        "lower_band": round(float(vwap_value - std_dev), 2),
        "signal": signal,
        "total_volume": int(df["volume"].sum()),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate VWAP from OHLCV candle data"
    )
    parser.add_argument("candles", help="JSON array of candles with OHLCV data")
    args = parser.parse_args()

    try:
        candles = json.loads(args.candles)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_vwap(candles)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()