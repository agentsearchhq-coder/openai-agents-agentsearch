# openai-agents-agentsearch

Function tools for the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) backed by [AgentSearch](https://agentsearchhq.com/?utm_source=openai-agents-agentsearch&utm_medium=package): live web search for agents. Free search needs no API key.

| Tool | Cost |
|---|---|
| `agentsearch_search` | **Free** (25 searches/day per user, up to 5 results, no key). Paid and unlimited if a wallet is set. |
| `agentsearch_extract` | $0.005/call (USDC on Base via x402) |
| `agentsearch_render` | $0.005/call (headless browser for JS pages) |

## Install

```bash
pip install -U openai-agents-agentsearch
```

## Quickstart

```python
from agents import Agent, Runner
from openai_agents_agentsearch import agentsearch_search, agentsearch_tools

agent = Agent(
    name="Researcher",
    instructions="Answer with current facts. Cite URLs.",
    tools=[agentsearch_search],          # or agentsearch_tools() for search + extract + render
)
result = Runner.run_sync(agent, "What changed in the latest OpenAI Agents SDK release?")
print(result.final_output)
```

## Paid mode

Install the `paid` extra (`pip install "openai-agents-agentsearch[paid]"`) and set `AGENTSEARCH_WALLET_PRIVATE_KEY` to the private key of a **new wallet made only for this**, funded with a little USDC on Base (e.g. $1; no ETH needed). Each call costs $0.005 and is paid over x402 through the Pocket Network Agentic Portal using the official x402 Python SDK. With a key set, search also goes paid and unlimited.

| Env var | Default |
|---|---|
| `AGENTSEARCH_MAX_TOTAL_ATOMIC` | `1000000` ($1.00 per process) |
| `AGENTSEARCH_MAX_PER_CALL_ATOMIC` | `5000` ($0.005; can only be lowered) |
| `AGENTSEARCH_TIMEOUT_MS` | `30000` |

Limits are checked before anything is signed. The key is never logged or returned. Paid results include a `payment` object.

## Errors

Tools return `"Error: ..."` strings instead of raising. A 429 from the free relay means the daily limit (25 searches/day per user) was hit, and the message explains how to upgrade.

## Development

```bash
pip install -e ".[test]" && pytest     # unit tests (mocked)
AGENTSEARCH_LIVE=1 pytest -k live       # one real free search
```

Docs: https://agentsearchhq.com/agents.md?utm_source=openai-agents-agentsearch&utm_medium=package

MIT
