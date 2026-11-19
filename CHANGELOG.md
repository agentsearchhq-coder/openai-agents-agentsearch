# Changelog

## 0.6.0 (2026-11-19)
- **With a wallet, search pays by default.** In the default mode, search now pays $0.003 per call over x402 to AgentSearch's own API ($0.005 with `AGENTSEARCH_PAYMENT_ROUTE=pocket`) when a wallet is configured and the `[paid]` extra is installed. With no wallet it uses the free relay exactly as before. `AGENTSEARCH_MODE=free` (or `mode="free"`) is the opt-out. Spend caps are unchanged (per call and `AGENTSEARCH_MAX_TOTAL_ATOMIC`, default $1.00). Previously a wallet key alone kept search free.
- **Reuse an existing wallet:** `AGENTSEARCH_WALLET_FILE` points at a file holding a 64-hex key or JSON with `privateKey` (`agentcash` = AgentCash's `~/.agentcash/wallet.json`). Read only when signing; never logged. Encrypted keystores and remote signers (CDP server wallets) are a follow-up.
- **Mode is visible:** every search result has an `agentsearch_mode` field (`"free: ..."` / `"paid: ..."`), and the first paid search in a process logs one `AgentSearch search mode: paid ...` warning line.

## 0.5.4 (2026-11-18)
- Fix HTTP 400s from the free relay. `free_search()` (also what you get when you pass it to a framework as a plain function) now unwraps a whole tool-input dict passed as `query`, ignores a non-count dict in the `max_results` slot (such as a framework config object passed as the 2nd argument), accepts a numeric string or `{"max_results": n}` for the count and clamps it to 1-5. An empty, missing or non-string query raises `AgentSearchError` before any request (nothing sent or charged). `check_query` unwraps tool-input dicts and no longer stringifies arbitrary objects. The `search` and `news` tools use the same lenient count coercion (clamped, never an error).

## 0.5.3 (2026-11-16)
- Docs only: README tool table: news $0.003/call and screenshot $0.004/call (were still $0.005). Live direct prices: search and news $0.003, extract $0.002, render $0.005, screenshot $0.004, search_and_read $0.005; Pocket route unchanged at $0.005. No code or behavior change.

## 0.5.2 (2026-11-15)
- Direct x402 list prices now match the live API (approved 2026-11-15): search and news $0.003, extract $0.002, render $0.005, screenshot $0.004, search_and_read $0.005. Runtime price constants, tool text, docs and tests updated. Pocket route remains $0.005. The per-call ceiling stays $0.020.

## 0.5.1 (2026-11-14)
- **Short-query guard.** Search, news and search-and-read now reject queries shorter than 2 characters (after trimming) before any network request, returning an `Error: ... rewrite the query (at least 2 characters) ...` string; nothing is sent or charged. Queries are trimmed before sending.
- **Relay input errors are final.** A 4xx from the free relay (other than 408/429) now tells the agent to fix the query instead of retrying it unchanged (the relay marks these `retryable:false`). Matches `langchain-agentsearch` 0.7.1 and `@agentsearchhq/agentsearch-mcp` 1.8.1.

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
