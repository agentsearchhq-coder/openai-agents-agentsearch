# Changelog

## 0.5.0 (2026-11-12)
- **News search.** New `agentsearch_news_search` ($0.008): recent articles with title, URL, snippet, source and publish date (1-10, default 5); calls with no results are not charged.
- **Screenshots.** New `agentsearch_screenshot` ($0.010): PNG or JPEG of the viewport or full page (up to 4000 px), optional `viewport_width`/`viewport_height`. The image is saved to a file (`AGENTSEARCH_SCREENSHOT_DIR`, default a temp folder) and the tool returns its path and metadata, not base64.
- **Search filters** on paid search, news and search-and-read: `freshness`, `date_from`/`date_to`, `country`, `language`, `include_domains`/`exclude_domains` (up to 5). Free search ignores them; the Pocket route drops them (listed in `payment.droppedFields`). The search mode stays developer-only and is still not in the model-visible schema.
- **Extract options on direct:** `max_chars` (up to 50000) and new `include_links` are now forwarded (0.4.0 dropped them).
- **Lower prices:** extract $0.004 (was $0.007), search-and-read $0.009 (was $0.015). `agentsearch_tools()` now returns search, news, extract, render, screenshot and search-and-read. Matches `@agentsearchhq/agentsearch-mcp` 1.8.0, `langchain-agentsearch` 0.7.0 and `crewai-agentsearch` 0.5.0.

## 0.4.0 (2026-11-10)
- **Search + Read in one paid call.** New ``agentsearch_search_and_read`` posts to `https://api.agentsearchhq.com/x402/v1/search_and_read` at **$0.015**, charged only when at least one page returns text. Default 3 results (max 5), default 8000 characters per page (max 20000); `render_fallback=true` renders at most one thin page in the same call. About 48% less than a $0.008 search plus three $0.007 extracts ($0.029), and one payment instead of four.
- Direct-only: not on the Pocket route, not on a self-hosted base URL. A Pocket or no-wallet call refuses with nothing signed. Search itself stays free by default.
- Direct per-call ceiling raised to **$0.020** (`DIRECT_MAX_PER_CALL_ATOMIC = 20000`) so a $0.015 search-and-read can settle. An old `10000` cap now refuses with a hint to raise it to `20000`. Matches `@agentsearchhq/agentsearch-mcp` 1.7.0.

## 0.3.0 (2026-11-09)

### Changed: paid calls go directly to AgentSearch's x402 API by default

- With a wallet key, paid calls now go to AgentSearch's own x402 API on Base (`https://api.agentsearchhq.com/x402/v1/...`, payee `0xC49B157887e51c21CB655f39CF65D6a4c2a4C337`) instead of the Pocket Network Agentic Portal.
- **Price change for wallet users:** search $0.008, extract $0.007, render $0.010 per call (was $0.005 on Pocket). Failed and empty calls are not charged on the direct API.
- To keep the Pocket route and its $0.005 price, set `AGENTSEARCH_PAYMENT_ROUTE=pocket` (`AGENTSEARCH_X402_DIRECT=0` also works). Any other value refuses paid calls with nothing signed.
- Per-call hard cap is now `10000` atomic units ($0.010) on the direct route; it stays `5000` on Pocket. If you set `AGENTSEARCH_MAX_PER_CALL_ATOMIC` below the direct price, the refusal tells you how to fix it.
- On the direct route, extract and render take only `url` (and search `query`, `max_results`); other options are dropped and listed in `payment.droppedFields`. Use the Pocket route for options like `formats`, `max_chars` or screenshots.
- Free search with no wallet is unchanged.

## 0.2.1 (unreleased)

### Changed: paid search is now explicit opt-in (safety)

- `agentsearch_search` defaults to free search. Having `AGENTSEARCH_WALLET_PRIVATE_KEY` or `POCKET_PRIVATE_KEY` set no longer switches search to paid.
- Search mode (`"free"` | `"paid"` | `"auto"`) is a developer setting only: `agentsearch_tools(search_mode=...)` or `make_agentsearch_search(mode)`, plus the `AGENTSEARCH_MODE` env override (takes precedence). It is not in the tool schema, so the model can never choose paid search.
- If you relied on 0.2.0 auto-switching to paid when a key was set, set `AGENTSEARCH_MODE=paid`.
- Extract and render are unchanged: they are paid tools and still need the wallet key.

### Fixed

- If paid search is chosen without the `[paid]` extra (or without a wallet key), search falls back to free with a logged warning instead of returning an error.

### Added

- `formats` on `agentsearch_extract` and `agentsearch_render`; `wait_for_selector` on `agentsearch_render`.

### Docs

- The free tier is described as up to 25 searches/day per IP (README, package description, docstrings, free-limit message).
- Prices removed from the tool docstrings the model sees; pricing is unchanged ($0.005 per paid call, including render).

## 0.2.0

- Client tag header, render guidance for extract/render, repository metadata.
