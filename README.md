# openai-agents-agentsearch

Function tools for the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) backed by [AgentSearch](https://agentsearchhq.com/?utm_source=openai-agents-agentsearch&utm_medium=package): live web search for agents. Free search needs no API key.

| Tool | Cost |
|---|---|
| `agentsearch_search` | **Free** by default (up to 25 searches/day per IP, up to 5 results, no key). Paid and unlimited only when you opt in (`AGENTSEARCH_MODE=paid` or `search_mode="paid"`). |
| `agentsearch_news_search` | $0.008/call (recent news with publish dates; no results, no charge) |
| `agentsearch_extract` | $0.004/call (USDC on Base via x402 to AgentSearch) |
| `agentsearch_render` | $0.010/call (headless browser for JS pages) |
| `agentsearch_screenshot` | $0.010/call (PNG/JPEG saved to a local file; path returned) |
| `agentsearch_search_and_read` | $0.009/call (search plus the top pages' text in one payment) |

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
    tools=[agentsearch_search],          # or agentsearch_tools() for search + news + extract + render + screenshot + search_and_read
)
result = Runner.run_sync(agent, "What changed in the latest OpenAI Agents SDK release?")
print(result.final_output)
```

## Search modes

The model only sees `agentsearch_search(query, max_results=None)`; it can never choose paid search. The search mode is a developer setting:

```python
from openai_agents_agentsearch import agentsearch_tools, make_agentsearch_search

tools = agentsearch_tools(search_mode="paid")   # or make_agentsearch_search("paid")
```

- `free` (default): the free relay.
- `paid`: unlimited paid search ($0.008/call). Falls back to free with a logged warning if the `[paid]` extra or wallet key is missing.
- `auto`: paid if the `[paid]` extra is installed and a wallet key is set, otherwise free.

`AGENTSEARCH_MODE` (`free`/`paid`/`auto`) takes precedence over the developer setting.

`agentsearch_extract` accepts `formats` (`markdown`, `text`, `html`, `links`); `agentsearch_render` also accepts `formats` and `wait_for_selector`.

## Filters, news and screenshots (0.5.0)

Paid search, `agentsearch_news_search` and `agentsearch_search_and_read` accept `freshness` (day/week/month/year), `date_from`/`date_to` (YYYY-MM-DD), `country`, `language`, and up to 5 `include_domains`/`exclude_domains`; free search ignores them. `agentsearch_extract` accepts `max_chars` (up to 50000) and `include_links`. `agentsearch_screenshot` takes `url`, `format` (png/jpeg), `full_page`, `viewport_width`/`viewport_height` (e.g. 390x844 for mobile), saves the image in `AGENTSEARCH_SCREENSHOT_DIR` and returns its path, so base64 never floods the model's context. News, screenshot and search-and-read are direct-only (not on Pocket).

## Paid mode

Install the `paid` extra (`pip install "openai-agents-agentsearch[paid]"`) and set `AGENTSEARCH_WALLET_PRIVATE_KEY` to the private key of a **new wallet made only for this**, funded with a little USDC on Base (e.g. $1; no ETH needed). Since 0.3.0 each call is paid over x402 **directly to AgentSearch's own API** (`https://api.agentsearchhq.com`, USDC on Base, settled only on success) using the official x402 Python SDK: search $0.008, news $0.008, extract $0.004, render $0.010, screenshot $0.010, search-and-read $0.009. $1 covers about 250 extracts or 111 search-and-read calls. Prefer the Pocket Network Agentic Portal ($0.005 per call)? Set `AGENTSEARCH_PAYMENT_ROUTE=pocket`. Extract and render use the key directly. Search stays free unless you opt in to paid search with `AGENTSEARCH_MODE=paid` (or `agentsearch_tools(search_mode="paid")`); a key alone does not switch it. If paid is chosen but the `[paid]` extra or the key is missing, search falls back to free with a logged warning.

| Env var | Default |
|---|---|
| `AGENTSEARCH_MAX_TOTAL_ATOMIC` | `1000000` ($1.00 per process) |
| `AGENTSEARCH_PAYMENT_ROUTE` | `direct` (AgentSearch's x402 API); `pocket` = Pocket Network Agentic Portal at $0.005/call |
| `AGENTSEARCH_MAX_PER_CALL_ATOMIC` | `20000` on the direct route, `5000` on Pocket ($0.020 / $0.005; can only be lowered) |
| `AGENTSEARCH_SCREENSHOT_DIR` | a temp folder (`agentsearch-screenshots`) |
| `AGENTSEARCH_TIMEOUT_MS` | `30000` |
| `AGENTSEARCH_MODE` | unset (`free`, `paid` or `auto`; overrides `search_mode`) |

Limits are checked before anything is signed. The key is not included in tool output or error messages. Paid results include a `payment` object.

## Errors

Tools return `"Error: ..."` strings instead of raising. A 429 from the free relay means the daily limit (up to 25 searches/day per IP) was hit, and the message explains how to upgrade.

## Development

```bash
pip install -e ".[test]" && pytest     # unit tests (mocked)
AGENTSEARCH_LIVE=1 pytest -k live       # one real free search
```

Docs: https://agentsearchhq.com/agents.md?utm_source=openai-agents-agentsearch&utm_medium=package

MIT
