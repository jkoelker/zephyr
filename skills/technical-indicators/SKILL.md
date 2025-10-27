---
name: technical-indicators
description: Calculate comprehensive technical indicators from price and OHLC data. Includes trend indicators (SMA, EMA, MACD, ADX), momentum oscillators (RSI, Stochastic), volatility measures (ATR, Bollinger Bands, Historical Volatility), support/resistance (Pivot Points, VWAP), and options-specific calculations (Expected Move). Use when analyzing price action, volatility, trends, momentum, support/resistance levels, or calculating expected moves for options strategies.
allowed-tools: Read, Bash
---

# Technical Indicators

Standalone Python scripts for price-derived indicators. Use them on demand—no extra environment setup needed.

## Quick Index (0DTE Focus)

| Script | Purpose | One-Liner |
| --- | --- | --- |
| `atr.py` | 10-day volatility + spacing guards | `skills/technical-indicators/scripts/atr.py "$json" --period 10` |
| `rsi.py` | Momentum bias (default 14) | `skills/technical-indicators/scripts/rsi.py "$json" --period 14` |
| `expected_move.py` | Session expected move & condor bands | `skills/technical-indicators/scripts/expected_move.py --spot <price> --iv <vol> --days 1` |

## Usage Pattern

1. Pull price/option data from your source.
2. Convert it to JSON inline:
   ```bash
   json=$(python - <<'PY'
import json
candles = [...]  # replace with your OHLC or close-price data
print(json.dumps(candles))
PY
)
   ```
3. Call the needed script with that JSON (or supply spot/IV for options tools).
4. Parse the JSON response—fields are flat and script-specific.

## Primary 0DTE Indicators

### ATR (Average True Range)
- Input: JSON array of OHLC candles (≥ period + 1 records; default period 10 → 11 candles).
- Command: `skills/technical-indicators/scripts/atr.py "$json" --period 10`
- Output: `atr`, `half_atr`, `double_atr`.

### RSI (Relative Strength Index)
- Input: JSON array of close prices (≥ period + 1; default 14 → 15 closes).
- Command: `skills/technical-indicators/scripts/rsi.py "$json" --period 14`
- Output: `rsi`, `signal` (`overbought` / `oversold` / `neutral`).

### Expected Move
- Input: Use spot + ATM call/put OR spot + IV (`--iv`).
- Command (IV style): `skills/technical-indicators/scripts/expected_move.py --spot 6875.16 --iv 0.29 --days 1`
- Output: `one_std` move plus upper/lower bands and probability estimates.

## Additional Indicators

<details>
<summary>Trend / Momentum / Volatility / Support scripts</summary>

| Category | Script | Example |
| --- | --- | --- |
| Trend | `sma.py`, `ema.py`, `macd.py`, `adx.py` | `skills/technical-indicators/scripts/sma.py "$json" --period 20` |
| Momentum | `stochastic.py` | `skills/technical-indicators/scripts/stochastic.py "$json" --k_period 14 --d_period 3` |
| Volatility | `bollinger_bands.py`, `historical_volatility.py` | `skills/technical-indicators/scripts/bollinger_bands.py "$json" --period 20 --std_dev 2` |
| Support/Resistance | `pivot_points.py`, `vwap.py` | `skills/technical-indicators/scripts/pivot_points.py '{"high":110,"low":95,"close":105}' --type standard` |
</details>

## Data Requirements & Troubleshooting

| Script | Input Fields | Minimum Samples |
| --- | --- | --- |
| `atr.py` | OHLC candles | period + 1 (default 11) |
| `rsi.py` | Close prices | period + 1 (default 15) |
| `expected_move.py` | Spot + ATM call/put **or** spot + IV | N/A (single snapshot) |
| `sma.py` / `ema.py` | Close prices | period (e.g., 20) |
| `macd.py` | Close prices | slow + signal (default 35) |
| `adx.py` | OHLC candles | 2×period + 1 (default 29) |
| `stochastic.py` | OHLC candles | k + d - 1 (default 16) |
| `bollinger_bands.py` | Close prices | period (default 20) |
| `historical_volatility.py` | Close prices | period + 1 |
| `pivot_points.py` | Prior high/low/close | 1 record |
| `vwap.py` | OHLCV candles | ≥1 bar |

JSON tips:
- Always wrap JSON payloads in single quotes when invoking scripts.
- Double-check commas/quotes—parse errors almost always trace to malformed JSON.
