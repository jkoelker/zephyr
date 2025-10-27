#!/usr/bin/env -S uv run --with pandas --with numpy python
"""
Calculate ADX (Average Directional Index) from OHLC candle data.

Usage:
    ./adx.py '<json_array>'
    ./adx.py '<json_array>' --period 14
"""

import sys
import json
import argparse

import pandas as pd
import numpy as np


def calculate_adx(candles: list[dict], period: int = 14) -> dict:
    """Calculate ADX (Average Directional Index) from OHLC data.

    ADX measures trend strength, not direction.
    0-25: Weak/No trend
    25-50: Strong trend
    50-75: Very strong trend
    75-100: Extremely strong trend

    Args:
        candles: List of dicts with 'high', 'low', 'close' keys
        period: Period for ADX calculation (default: 14)

    Returns:
        Dict with ADX, +DI, -DI, and trend strength assessment

    Raises:
        ValueError: If insufficient data or missing required fields
    """
    min_required = period * 2 + 1  # Need extra data for smoothing
    if len(candles) < min_required:
        raise ValueError(f"Need at least {min_required} candles, got {len(candles)}")

    required_fields = ["high", "low", "close"]
    for i, candle in enumerate(candles):
        missing = [f for f in required_fields if f not in candle]
        if missing:
            raise ValueError(f"Candle {i} missing fields: {', '.join(missing)}")

    df = pd.DataFrame(candles)

    # Calculate True Range (TR)
    df["prev_close"] = df["close"].shift(1)
    df["hl"] = df["high"] - df["low"]
    df["hc"] = (df["high"] - df["prev_close"]).abs()
    df["lc"] = (df["low"] - df["prev_close"]).abs()
    df["tr"] = df[["hl", "hc", "lc"]].max(axis=1)

    # Calculate directional movements
    df["high_diff"] = df["high"] - df["high"].shift(1)
    df["low_diff"] = df["low"].shift(1) - df["low"]

    # +DM and -DM
    df["plus_dm"] = np.where((df["high_diff"] > df["low_diff"]) & (df["high_diff"] > 0), df["high_diff"], 0)
    df["minus_dm"] = np.where((df["low_diff"] > df["high_diff"]) & (df["low_diff"] > 0), df["low_diff"], 0)

    # Smooth the values using Wilder's smoothing (similar to EMA)
    # First values use SMA
    df["atr"] = df["tr"].rolling(window=period).mean()
    df["plus_dm_smooth"] = df["plus_dm"].rolling(window=period).mean()
    df["minus_dm_smooth"] = df["minus_dm"].rolling(window=period).mean()

    # Apply Wilder's smoothing for subsequent values
    for i in range(period, len(df)):
        if i == period:
            continue
        df.loc[i, "atr"] = (df.loc[i - 1, "atr"] * (period - 1) + df.loc[i, "tr"]) / period
        df.loc[i, "plus_dm_smooth"] = (df.loc[i - 1, "plus_dm_smooth"] * (period - 1) + df.loc[i, "plus_dm"]) / period
        df.loc[i, "minus_dm_smooth"] = (df.loc[i - 1, "minus_dm_smooth"] * (period - 1) + df.loc[i, "minus_dm"]) / period

    # Calculate +DI and -DI
    df["plus_di"] = 100 * df["plus_dm_smooth"] / df["atr"]
    df["minus_di"] = 100 * df["minus_dm_smooth"] / df["atr"]

    # Calculate DX
    df["di_sum"] = df["plus_di"] + df["minus_di"]
    df["di_diff"] = (df["plus_di"] - df["minus_di"]).abs()
    df["dx"] = 100 * df["di_diff"] / df["di_sum"]

    # Calculate ADX (smoothed DX)
    df["adx"] = df["dx"].rolling(window=period).mean()

    # Apply Wilder's smoothing for ADX
    for i in range(period * 2, len(df)):
        df.loc[i, "adx"] = (df.loc[i - 1, "adx"] * (period - 1) + df.loc[i, "dx"]) / period

    # Get latest values
    adx_value = df["adx"].iloc[-1]
    plus_di = df["plus_di"].iloc[-1]
    minus_di = df["minus_di"].iloc[-1]

    # Previous values for trend detection
    prev_adx = df["adx"].iloc[-2]
    prev_plus_di = df["plus_di"].iloc[-2]
    prev_minus_di = df["minus_di"].iloc[-2]

    # Determine trend strength
    if adx_value < 20:
        strength = "no_trend"
    elif adx_value < 25:
        strength = "weak_trend"
    elif adx_value < 50:
        strength = "strong_trend"
    elif adx_value < 75:
        strength = "very_strong_trend"
    else:
        strength = "extremely_strong_trend"

    # Determine direction and momentum
    if plus_di > minus_di:
        direction = "bullish"
    elif minus_di > plus_di:
        direction = "bearish"
    else:
        direction = "neutral"

    # Check for crossovers
    signal = strength
    if prev_plus_di <= prev_minus_di and plus_di > minus_di:
        signal = "bullish_crossover"
    elif prev_plus_di >= prev_minus_di and plus_di < minus_di:
        signal = "bearish_crossover"
    elif adx_value > prev_adx and adx_value > 25:
        signal = "trend_strengthening"
    elif adx_value < prev_adx and adx_value > 25:
        signal = "trend_weakening"

    return {
        "adx": round(adx_value, 2),
        "plus_di": round(plus_di, 2),
        "minus_di": round(minus_di, 2),
        "trend_strength": strength,
        "trend_direction": direction,
        "signal": signal,
        "period": period,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate ADX from OHLC candle data"
    )
    parser.add_argument("candles", help="JSON array of candles with OHLC data")
    parser.add_argument(
        "--period", type=int, default=14, help="Period for ADX calculation (default: 14)"
    )
    args = parser.parse_args()

    try:
        candles = json.loads(args.candles)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_adx(candles, args.period)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()