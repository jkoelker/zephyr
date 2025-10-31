# Agent and Skill Integration Guide

## Purpose
- Provide a single reference for coordinating personalities in `agents/` with actionable capabilities in `skills/`.
- Ensure large language models (LLMs) activate personas and skills only when the user explicitly requests them.

## Directory Map
- `agents/`: One markdown file per persona (for example, `0dte-iron-condor.md`). Filenames describe the personality’s focus area.
- `skills/`: One subdirectory per reusable capability (for example, `skills/schwab-data-sweep/`). Each contains a `SKILL.md` that documents inputs, outputs, and usage patterns.

## Global Market Data Conventions
- Always prefix index and volatility symbols with `$` when calling Schwab tools (e.g., `$SPX`, `$VIX`, `$DJI`, `$NDX`). Schwab treats bare tickers as equities/ETFs and will return incorrect products.
- Keep bare tickers for single-name equities and ETFs to avoid accidentally requesting index instruments.
- Reference `$SPX` explicitly for SPX index options; do **not** substitute `SPX`, `SPXW`, or ETF proxies like `SPY`.

## Working With Agents
- **Discovery**: Start by listing filenames in `agents/` to understand available personas. Infer the high-level personality from the filename alone.
- **On-Demand Loading**: Do **not** open any agent file proactively. Only read a specific agent markdown when the user explicitly requests that personality or when the request clearly requires it, and once you reach that point just load it—no extra confirmation steps.
- **Persona Activation**:
  1. Interpret the user’s request.
  2. Match the request to the best-fitting agent based on filename semantics.
  3. Load the agent file just-in-time, extract guidance, and respond in that persona’s voice or workflow.
- **Multiple Personas**: If the user wants to switch personas mid-conversation, unload previous context and repeat the activation flow for the new agent.

## Working With Skills
- **Structure**: Each skill directory includes scripts/resources plus a `SKILL.md` reference guide.
- **Lazy Access**: Do **not** preload skill documentation. Inspect a skill’s `SKILL.md` only when the active persona needs that capability for the current task.
- **Reusability**: Skills are persona-agnostic. Any agent may invoke them if the workflow calls for it.

## Recommended LLM Workflow
1. **Understand the request**: Determine whether a specific personality or capability is implied.
2. **Select a persona**: Infer the best agent by filename; defer opening the file until the user confirms or the task demands it.
3. **Read agent guidance** (just-in-time): Use the agent file to set tone, decision rules, and domain constraints.
4. **Locate needed skills**: Identify relevant skills by directory name; consult `SKILL.md` only when execution details are required.
5. **Execute and respond**: Combine persona guidance with skill instructions to fulfill the user’s request.
6. **Stay modular**: When tasks finish, release persona- and skill-specific context so fresh requests restart at step 1.

## Operational Tips
- Favor filename inference first; use file contents only when necessary.
- Document which agent and skills were used in your final response if transparency is helpful to the user.
- If a required persona or skill is missing, note the gap and proceed with best-effort reasoning or ask for clarification.
