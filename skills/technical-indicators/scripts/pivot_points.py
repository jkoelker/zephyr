#!/usr/bin/env -S uv run --with pandas python
"""
Calculate Pivot Points from previous OHLC data.

Usage:
    ./pivot_points.py '{"high": 100, "low": 95, "close": 98}'
    ./pivot_points.py '{"high": 100, "low": 95, "close": 98}' --type fibonacci
"""

import sys
import json
import argparse


def calculate_standard_pivots(high: float, low: float, close: float) -> dict:
    """Calculate Standard Pivot Points."""
    pivot = (high + low + close) / 3

    # Resistance levels
    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)

    # Support levels
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)

    return {
        "r3": round(r3, 2),
        "r2": round(r2, 2),
        "r1": round(r1, 2),
        "pivot": round(pivot, 2),
        "s1": round(s1, 2),
        "s2": round(s2, 2),
        "s3": round(s3, 2),
    }


def calculate_fibonacci_pivots(high: float, low: float, close: float) -> dict:
    """Calculate Fibonacci Pivot Points."""
    pivot = (high + low + close) / 3
    range_hl = high - low

    # Resistance levels
    r1 = pivot + (0.382 * range_hl)
    r2 = pivot + (0.618 * range_hl)
    r3 = pivot + (1.000 * range_hl)

    # Support levels
    s1 = pivot - (0.382 * range_hl)
    s2 = pivot - (0.618 * range_hl)
    s3 = pivot - (1.000 * range_hl)

    return {
        "r3": round(r3, 2),
        "r2": round(r2, 2),
        "r1": round(r1, 2),
        "pivot": round(pivot, 2),
        "s1": round(s1, 2),
        "s2": round(s2, 2),
        "s3": round(s3, 2),
    }


def calculate_camarilla_pivots(high: float, low: float, close: float) -> dict:
    """Calculate Camarilla Pivot Points."""
    range_hl = high - low

    # Resistance levels
    r4 = close + (range_hl * 1.1 / 2)
    r3 = close + (range_hl * 1.1 / 4)
    r2 = close + (range_hl * 1.1 / 6)
    r1 = close + (range_hl * 1.1 / 12)

    # Support levels
    s1 = close - (range_hl * 1.1 / 12)
    s2 = close - (range_hl * 1.1 / 6)
    s3 = close - (range_hl * 1.1 / 4)
    s4 = close - (range_hl * 1.1 / 2)

    # Pivot is typically the close price in Camarilla
    pivot = close

    return {
        "r4": round(r4, 2),
        "r3": round(r3, 2),
        "r2": round(r2, 2),
        "r1": round(r1, 2),
        "pivot": round(pivot, 2),
        "s1": round(s1, 2),
        "s2": round(s2, 2),
        "s3": round(s3, 2),
        "s4": round(s4, 2),
    }


def calculate_pivot_points(
    prev_candle: dict, pivot_type: str = "standard", current_price: float = None
) -> dict:
    """Calculate Pivot Points from previous period OHLC data.

    Args:
        prev_candle: Dict with 'high', 'low', 'close' keys from previous period
        pivot_type: Type of pivots ('standard', 'fibonacci', 'camarilla')
        current_price: Current market price for position analysis

    Returns:
        Dict with pivot levels and nearest support/resistance

    Raises:
        ValueError: If missing required fields
    """
    required_fields = ["high", "low", "close"]
    missing = [f for f in required_fields if f not in prev_candle]
    if missing:
        raise ValueError(f"Previous candle missing fields: {', '.join(missing)}")

    high = prev_candle["high"]
    low = prev_candle["low"]
    close = prev_candle["close"]

    # Calculate pivots based on type
    if pivot_type == "fibonacci":
        levels = calculate_fibonacci_pivots(high, low, close)
    elif pivot_type == "camarilla":
        levels = calculate_camarilla_pivots(high, low, close)
    else:
        levels = calculate_standard_pivots(high, low, close)

    result = {
        "type": pivot_type,
        "levels": levels,
    }

    # Add current price analysis if provided
    if current_price is not None:
        result["current_price"] = round(current_price, 2)

        # Find nearest support and resistance
        pivot = levels["pivot"]

        if current_price > pivot:
            # Price above pivot, find nearest resistance and support
            resistances = [(k, v) for k, v in levels.items() if k.startswith("r") and v > current_price]
            supports = [(k, v) for k, v in levels.items() if k.startswith("s") or k == "pivot"]

            if resistances:
                nearest_r = min(resistances, key=lambda x: x[1])
                result["nearest_resistance"] = {"level": nearest_r[0], "price": nearest_r[1]}

            if supports:
                nearest_s = max(supports, key=lambda x: x[1])
                result["nearest_support"] = {"level": nearest_s[0], "price": nearest_s[1]}

            result["position"] = "above_pivot"
        else:
            # Price below pivot, find nearest support and resistance
            supports = [(k, v) for k, v in levels.items() if k.startswith("s") and v < current_price]
            resistances = [(k, v) for k, v in levels.items() if k.startswith("r") or k == "pivot"]

            if supports:
                nearest_s = max(supports, key=lambda x: x[1])
                result["nearest_support"] = {"level": nearest_s[0], "price": nearest_s[1]}

            if resistances:
                nearest_r = min(resistances, key=lambda x: x[1])
                result["nearest_resistance"] = {"level": nearest_r[0], "price": nearest_r[1]}

            result["position"] = "below_pivot"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Calculate Pivot Points from previous OHLC data"
    )
    parser.add_argument(
        "prev_candle", help="JSON object with previous period's high, low, close"
    )
    parser.add_argument(
        "--type",
        choices=["standard", "fibonacci", "camarilla"],
        default="standard",
        help="Type of pivot points (default: standard)",
    )
    parser.add_argument(
        "--current", type=float, help="Current price for position analysis"
    )
    args = parser.parse_args()

    try:
        prev_candle = json.loads(args.prev_candle)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_pivot_points(prev_candle, args.type, args.current)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()