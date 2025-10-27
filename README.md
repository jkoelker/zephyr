# Zephyr Trading Agents & Skills

Agents and reusable skills for letting an LLM drive MCP trading workflows.
The project targets Codex for best results but is compatible with Claude
(see `.claude-project`).

## Repository Layout
- `agents/`: Persona files that describe trading-focused assistants.
- `skills/`: Capability modules, each with a `SKILL.md`.

## Setup
Create the UV-managed virtual environment from the repository root:
```bash
uv venv
```
Configure any required MCP servers (for example Schwab) according to their
own instructions, then load the relevant agents and skills within your
orchestrating LLM.
