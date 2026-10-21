"""Framework-neutral operations. Each returns a JSON string, or an "Error: ..." string (never raises)."""
from __future__ import annotations

from typing import Any, Optional

from . import _client as c


def resolve_search_mode(mode: Optional[str] = None) -> str:
    """Return "paid" or "free" for one search call.

    Precedence: AGENTSEARCH_MODE (operator override) > the ``mode`` argument > "free".
    "auto" means paid only if a wallet key is set AND the [paid] extra is installed, otherwise free.
    A wallet key alone never switches the default to paid. If paid is chosen but the [paid] extra
    (or a wallet key) is missing, search falls back to free with a logged warning instead of an error.
    """
    chosen = c.env_mode() or (str(mode).strip().lower() if mode else "") or "free"
    if chosen not in c.SEARCH_MODES:
        raise c.AgentSearchError(f"mode must be one of 'free', 'paid', 'auto' (got {mode!r}). No call was made.")
    if chosen == "free":
        return "free"
    ready = c.paid_extra_installed() and c.has_wallet_key()
    if chosen == "auto":
        return "paid" if ready else "free"
    if not c.paid_extra_installed():
        c.logger.warning("AgentSearch: paid search requested, but the [paid] extra is not installed; "
                         "using free search instead. To enable paid search: %s", c.PAID_INSTALL_HINT)
        return "free"
    if not c.has_wallet_key():
        c.logger.warning("AgentSearch: paid search requested, but no wallet key is set "
                         "(AGENTSEARCH_WALLET_PRIVATE_KEY); using free search instead.")
        return "free"
    return "paid"


def search(query: str, max_results: Optional[int] = None, mode: Optional[str] = None) -> str:
    try:
        if not query or not str(query).strip():
            raise c.AgentSearchError("query must not be empty")
        if max_results is not None:
            max_results = max(1, min(int(max_results), 5))
        if resolve_search_mode(mode) == "paid":
            body: dict[str, Any] = {"query": query}
            if max_results:
                body["max_results"] = max_results
            return c.dumps(c.call_portal("search", body))
        return c.dumps(c.free_search(query, max_results))
    except Exception as e:
        return f"Error: {e}"


def paid(op: str, **kwargs: Any) -> str:
    try:
        if not c.has_wallet_key():
            raise c.AgentSearchError(c.paid_only_message(f"agentsearch_{op}"))
        fb = kwargs.pop("render_fallback", None)
        body = {k: v for k, v in kwargs.items() if v is not None}
        if op == "extract":
            return c.dumps(c.extract_with_fallback(body, fb))
        return c.dumps(c.call_portal(op, body))
    except Exception as e:
        return f"Error: {e}"
