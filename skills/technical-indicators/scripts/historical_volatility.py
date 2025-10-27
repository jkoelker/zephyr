#!/usr/bin/env -S uv run --with pandas --with numpy python
"""
Calculate Historical Volatility from price data.

Usage:
    ./historical_volatility.py '<json_array>'
    ./historical_volatility.py '<json_array>' --period 20 --annualize 252
"""

import sys
import json
import argparse

import pandas as pd
import numpy as np


def calculate_historical_volatility(
    prices: list[float],
    period: int = 20,
    annualize_factor: int = 252,
    method: str = "close_to_close",
) -> dict:
    """Calculate Historical Volatility from price data.

    Args:
        prices: List of close prices
        period: Lookback period for volatility calculation (default: 20)
        annualize_factor: Trading days per year (252 for stocks, 365 for crypto)
        method: Calculation method ('close_to_close' or 'log_returns')

    Returns:
        Dict with various volatility metrics

    Raises:
        ValueError: If insufficient data
    """
    if len(prices) < period + 1:
        raise ValueError(f"Need at least {period + 1} prices, got {len(prices)}")

    series = pd.Series(prices)

    if method == "log_returns":
        # Calculate log returns
        returns = np.log(series / series.shift(1))
    else:
        # Calculate simple returns
        returns = series.pct_change()

    # Drop NaN values
    returns = returns.dropna()

    # Calculate rolling standard deviation
    rolling_std = returns.rolling(window=period).std()

    # Get latest volatility
    daily_vol = rolling_std.iloc[-1]

    # Annualized volatility
    annualized_vol = daily_vol * np.sqrt(annualize_factor)

    # Convert to percentage
    daily_vol_pct = daily_vol * 100
    annualized_vol_pct = annualized_vol * 100

    # Calculate different timeframe volatilities
    weekly_vol = daily_vol * np.sqrt(5) * 100  # Assuming 5 trading days
    monthly_vol = daily_vol * np.sqrt(21) * 100  # Assuming 21 trading days

    # Calculate percentile rank (where does current vol stand historically)
    all_vols = rolling_std.dropna()
    if len(all_vols) > 0:
        percentile_rank = (all_vols < daily_vol).sum() / len(all_vols) * 100
    else:
        percentile_rank = 50

    # Determine volatility regime
    if annualized_vol_pct < 10:
        regime = "very_low"
    elif annualized_vol_pct < 15:
        regime = "low"
    elif annualized_vol_pct < 20:
        regime = "normal"
    elif annualized_vol_pct < 30:
        regime = "elevated"
    elif annualized_vol_pct < 50:
        regime = "high"
    else:
        regime = "extreme"

    # Calculate min and max volatility over the period
    min_vol = all_vols.min() * np.sqrt(annualize_factor) * 100 if len(all_vols) > 0 else 0
    max_vol = all_vols.max() * np.sqrt(annualize_factor) * 100 if len(all_vols) > 0 else 0
    mean_vol = all_vols.mean() * np.sqrt(annualize_factor) * 100 if len(all_vols) > 0 else 0

    return {
        "daily_vol": round(daily_vol_pct, 2),
        "weekly_vol": round(weekly_vol, 2),
        "monthly_vol": round(monthly_vol, 2),
        "annualized_vol": round(annualized_vol_pct, 2),
        "percentile_rank": round(percentile_rank, 1),
        "regime": regime,
        "min_vol": round(min_vol, 2),
        "max_vol": round(max_vol, 2),
        "mean_vol": round(mean_vol, 2),
        "period": period,
        "annualize_factor": annualize_factor,
    }


def calculate_parkinson_volatility(candles: list[dict], period: int = 20, annualize_factor: int = 252) -> dict:
    """Calculate Parkinson volatility using high/low prices.

    More efficient than close-to-close volatility as it uses intraday range.

    Args:
        candles: List of dicts with 'high' and 'low' keys
        period: Lookback period
        annualize_factor: Trading days per year

    Returns:
        Dict with Parkinson volatility metrics
    """
    if len(candles) < period:
        raise ValueError(f"Need at least {period} candles, got {len(candles)}")

    required_fields = ["high", "low"]
    for i, candle in enumerate(candles):
        missing = [f for f in required_fields if f not in candle]
        if missing:
            raise ValueError(f"Candle {i} missing fields: {', '.join(missing)}")

    df = pd.DataFrame(candles)

    # Parkinson's formula: sqrt(1/(4*ln(2)) * sum(ln(H/L)^2))
    df["hl_ratio"] = np.log(df["high"] / df["low"])
    df["hl_ratio_sq"] = df["hl_ratio"] ** 2

    # Rolling calculation
    rolling_sum = df["hl_ratio_sq"].rolling(window=period).sum()
    parkinson_vol = np.sqrt(rolling_sum / (period * 4 * np.log(2)))

    # Get latest value
    daily_vol = parkinson_vol.iloc[-1]
    annualized_vol = daily_vol * np.sqrt(annualize_factor)

    return {
        "parkinson_daily": round(daily_vol * 100, 2),
        "parkinson_annualized": round(annualized_vol * 100, 2),
        "period": period,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate Historical Volatility from price data"
    )
    parser.add_argument("prices", help="JSON array of prices or OHLC candles")
    parser.add_argument(
        "--period", type=int, default=20, help="Lookback period (default: 20)"
    )
    parser.add_argument(
        "--annualize",
        type=int,
        default=252,
        help="Annualization factor - trading days per year (default: 252)",
    )
    parser.add_argument(
        "--method",
        choices=["close_to_close", "log_returns", "parkinson"],
        default="close_to_close",
        help="Calculation method (default: close_to_close)",
    )
    args = parser.parse_args()

    try:
        data = json.loads(args.prices)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.method == "parkinson":
            # Expect OHLC candles
            if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                raise ValueError("Parkinson method requires array of OHLC candles")
            result = calculate_parkinson_volatility(data, args.period, args.annualize)
        else:
            # Expect price array
            if not isinstance(data, list):
                # Try to extract close prices from candles
                if all(isinstance(item, dict) and "close" in item for item in data):
                    data = [item["close"] for item in data]
                else:
                    raise ValueError("Expected array of prices or candles with 'close' field")
            result = calculate_historical_volatility(data, args.period, args.annualize, args.method)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()