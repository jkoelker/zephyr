#!/usr/bin/env -S uv run --with numpy python
"""
Calculate Expected Move from options prices.

Usage:
    ./expected_move.py --atm_call 5.50 --atm_put 5.30 --spot 100
    ./expected_move.py --straddle 10.80 --spot 100
"""

import sys
import json
import argparse

import numpy as np


def calculate_expected_move(
    spot_price: float,
    atm_call: float = None,
    atm_put: float = None,
    straddle_price: float = None,
    multiplier: float = 0.85,
) -> dict:
    """Calculate expected move from ATM options prices.

    The expected move represents the market's expectation of price movement
    by expiration, derived from option prices.

    Args:
        spot_price: Current spot price of underlying
        atm_call: ATM call option price
        atm_put: ATM put option price
        straddle_price: Combined ATM straddle price (alternative to call+put)
        multiplier: Statistical adjustment factor (default: 0.85 for ~1 std dev)

    Returns:
        Dict with expected move calculations and strike recommendations

    Raises:
        ValueError: If insufficient option prices provided
    """
    # Calculate straddle price
    if straddle_price is not None:
        straddle = straddle_price
    elif atm_call is not None and atm_put is not None:
        straddle = atm_call + atm_put
    else:
        raise ValueError(
            "Must provide either straddle_price or both atm_call and atm_put"
        )

    # Raw expected move (straddle price)
    raw_expected_move = straddle

    # Adjusted expected move (typical multiplier is 0.85)
    adjusted_move = raw_expected_move * multiplier

    # Calculate absolute move points
    move_up = spot_price + adjusted_move
    move_down = spot_price - adjusted_move

    # Calculate percentage moves
    move_pct = (adjusted_move / spot_price) * 100
    raw_move_pct = (raw_expected_move / spot_price) * 100

    # Calculate 2x expected move (for wider strategies)
    two_x_move_up = spot_price + (adjusted_move * 2)
    two_x_move_down = spot_price - (adjusted_move * 2)

    # Iron Condor strike recommendations
    # Short strikes at ~0.5x expected move (higher probability)
    short_call_strike = round(spot_price + (adjusted_move * 0.5), 1)
    short_put_strike = round(spot_price - (adjusted_move * 0.5), 1)

    # Long strikes at 1x expected move
    long_call_strike = round(move_up, 1)
    long_put_strike = round(move_down, 1)

    # Wide Iron Condor (short at 1x, long at 1.5x)
    wide_short_call = round(move_up, 1)
    wide_short_put = round(move_down, 1)
    wide_long_call = round(spot_price + (adjusted_move * 1.5), 1)
    wide_long_put = round(spot_price - (adjusted_move * 1.5), 1)

    # Probability estimates (rough approximations)
    # Based on normal distribution assumptions
    prob_within_1x = 68  # ~1 standard deviation
    prob_within_2x = 95  # ~2 standard deviations
    prob_touch_1x = 100 - prob_within_1x  # Probability of touching boundary

    return {
        "spot_price": round(spot_price, 2),
        "straddle_price": round(straddle, 2),
        "expected_move": {
            "raw": round(raw_expected_move, 2),
            "adjusted": round(adjusted_move, 2),
            "percentage": round(move_pct, 2),
            "raw_percentage": round(raw_move_pct, 2),
        },
        "move_boundaries": {
            "upper_1x": round(move_up, 2),
            "lower_1x": round(move_down, 2),
            "upper_2x": round(two_x_move_up, 2),
            "lower_2x": round(two_x_move_down, 2),
        },
        "iron_condor_strikes": {
            "conservative": {
                "short_call": short_call_strike,
                "short_put": short_put_strike,
                "long_call": long_call_strike,
                "long_put": long_put_strike,
                "description": "Short at 0.5x, Long at 1x move",
            },
            "aggressive": {
                "short_call": wide_short_call,
                "short_put": wide_short_put,
                "long_call": wide_long_call,
                "long_put": wide_long_put,
                "description": "Short at 1x, Long at 1.5x move",
            },
        },
        "probability_estimates": {
            "stay_within_1x": prob_within_1x,
            "stay_within_2x": prob_within_2x,
            "touch_1x_boundary": prob_touch_1x,
        },
        "multiplier_used": multiplier,
    }


def calculate_expected_move_from_iv(
    spot_price: float, iv: float, days_to_expiry: float
) -> dict:
    """Calculate expected move from implied volatility.

    Alternative method using IV instead of option prices.

    Args:
        spot_price: Current spot price
        iv: Implied volatility (as decimal, e.g., 0.30 for 30%)
        days_to_expiry: Days until expiration

    Returns:
        Dict with expected move calculations
    """
    # Convert days to years
    time_to_expiry = days_to_expiry / 365

    # Calculate 1 standard deviation move
    one_std_move = spot_price * iv * np.sqrt(time_to_expiry)

    # Percentage move
    move_pct = (one_std_move / spot_price) * 100

    # Boundaries
    upper_1std = spot_price + one_std_move
    lower_1std = spot_price - one_std_move
    upper_2std = spot_price + (2 * one_std_move)
    lower_2std = spot_price - (2 * one_std_move)

    return {
        "spot_price": round(spot_price, 2),
        "implied_volatility": round(iv * 100, 2),
        "days_to_expiry": days_to_expiry,
        "expected_move": {
            "one_std": round(one_std_move, 2),
            "percentage": round(move_pct, 2),
        },
        "move_boundaries": {
            "upper_1std": round(upper_1std, 2),
            "lower_1std": round(lower_1std, 2),
            "upper_2std": round(upper_2std, 2),
            "lower_2std": round(lower_2std, 2),
        },
        "probability_estimates": {
            "stay_within_1std": 68,
            "stay_within_2std": 95,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate expected move from options prices"
    )
    parser.add_argument(
        "--spot", type=float, required=True, help="Current spot price"
    )
    parser.add_argument("--atm_call", type=float, help="ATM call option price")
    parser.add_argument("--atm_put", type=float, help="ATM put option price")
    parser.add_argument(
        "--straddle", type=float, help="ATM straddle price (alternative to call+put)"
    )
    parser.add_argument(
        "--multiplier",
        type=float,
        default=0.85,
        help="Statistical adjustment (default: 0.85)",
    )
    parser.add_argument(
        "--iv", type=float, help="Implied volatility (as decimal) for IV-based calc"
    )
    parser.add_argument(
        "--days", type=float, help="Days to expiry (for IV-based calculation)"
    )
    args = parser.parse_args()

    try:
        if args.iv is not None and args.days is not None:
            # IV-based calculation
            result = calculate_expected_move_from_iv(args.spot, args.iv, args.days)
        else:
            # Option price-based calculation
            result = calculate_expected_move(
                args.spot, args.atm_call, args.atm_put, args.straddle, args.multiplier
            )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()