# Changelog

## 0.2.1 (unreleased)

### Changed: paid search is now explicit opt-in (safety)

- `agentsearch_search` defaults to free search. Having `AGENTSEARCH_WALLET_PRIVATE_KEY` or `POCKET_PRIVATE_KEY` set no longer switches search to paid.
- New `mode` argument (`"free"` | `"paid"` | `"auto"`) and `AGENTSEARCH_MODE` env override (takes precedence over the argument).
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
