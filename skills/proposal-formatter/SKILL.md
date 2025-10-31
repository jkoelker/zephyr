---
name: proposal-formatter
description: Format trading proposals with timestamped headers and disciplined bullet structure. Use when a persona must deliver a single consolidated proposal with Schwab timestamps, bold parent bullets, and one-metric-per-line nested bullets.
---

# Proposal Formatter

Use this skill to present trading output in a concise, scan-friendly proposal. It supports any persona that needs to deliver a Schwab-timestamped summary with consistent structure.

## Instructions

1. **Header**
   - Start responses with `### Proposal ({HH:MM} ET | {HH:MM} UTC)`.
   - Source both timestamps from Schwab data (`schwab-data-sweep` cache, `mcp__schwab__get_datetime`, or another broker response). Never rely on local system time.

2. **Parent Bullets**
   - Organize the body with bold parent bullets (`- **Section Name**`).
   - Choose section names appropriate to the persona (e.g., `Prereqs`, `Capital`, `Market`, `Indicators`, `Structure`, `Plan`, `Next`, `Notes`). Keep them concise and stable so users can scan quickly.

3. **Nested Lines**
   - Under each parent bullet, indent every metric with two leading spaces before `-`.
   - Each nested bullet must present exactly one metric or directive, formatted as `Label: value (status)`.
   - Status tags (`PASS`, `FLAG`, `BLOCK`, `DONE`, etc.) should be short and capitalized. Use them to highlight guardrail checks or action states.

4. **Context Add-ons**
   - If additional commentary is needed, add a follow-up nested bullet immediately below the metric. Keep it brief (~1 sentence) and reference the prior line’s label.
   - Avoid multi-column tables, inline slash-separated metrics, or long paragraphs. The goal is rapid comprehension.

5. **Numerics & Units**
   - Apply consistent number formatting: thousands separators (`6,874.47`), percentage symbols with two decimals when precision matters (`0.75%`), and currency symbols for dollar values (`$7,946`).
   - Highlight threshold breaches by pairing the status tag with a short note inside parentheses (`(FLAG – outside 25% guardrail)`).

6. **Closing Line**
   - End the proposal with the next required decision or acknowledgement so the workflow keeps moving (`Need confirmation to stage order`, `Monitoring until 14:00 ET`, etc.).

## Examples

- **0DTE Iron Condor**
  - Parent bullets: `Prereqs`, `Market`, `Indicators`, `Sizing`, `Structure`, `Plan`.
  - Metrics: `Schwab Auth: ✓ (PASS)`, `Margin Headroom: $142,000 (PASS – ≥$25K target)`.

- **Wheel Cycle**
  - Parent bullets: `Prereqs`, `Capital`, `Market`, `Indicators`, `Entry Score`, `Orders`, `Plan`, `Next`.
  - Metrics: `Net Liq: $512,430 (FLAG – 26% wheels)`, followed by context bullet explaining mitigation.

Use this skill whenever a persona produces proposal-style output so formatting stays uniform across strategies.
