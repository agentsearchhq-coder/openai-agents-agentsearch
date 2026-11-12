"""Framework-neutral operations. Each returns a JSON string, or an "Error: ..." string (never raises)."""
from __future__ import annotations

import base64
import os
import tempfile
import time
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


def _filters(kw: dict[str, Any]) -> dict[str, Any]:
    return {k: kw[k] for k in c.FILTER_KEYS if kw.get(k) is not None}


def search(query: str, max_results: Optional[int] = None, mode: Optional[str] = None, **filters: Any) -> str:
    try:
        if not query or not str(query).strip():
            raise c.AgentSearchError("query must not be empty")
        if max_results is not None:
            max_results = max(1, min(int(max_results), 5))
        if resolve_search_mode(mode) == "paid":
            body: dict[str, Any] = {"query": query, **_filters(filters)}
            if max_results:
                body["max_results"] = max_results
            return c.dumps(c.call_portal("search", body))
        out = c.free_search(query, max_results)
        if _filters(filters) and isinstance(out, dict):
            out = {**out, "note": "Filters (freshness, dates, country, language, domains) apply only to paid search; free search ignored them."}
        return c.dumps(out)
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

def search_and_read(query: str, num_results: Optional[int] = None, max_chars: Optional[int] = None,
                    render_fallback: Optional[bool] = None, **filters: Any) -> str:
    """Search the live web and read the top pages in one paid call ($0.009, direct x402 only)."""
    try:
        if not query or not str(query).strip():
            raise c.AgentSearchError("query must not be empty")
        body: dict[str, Any] = {"query": query, **_filters(filters)}
        if num_results is not None:
            body["num_results"] = int(num_results)
        if max_chars is not None:
            body["max_chars"] = int(max_chars)
        if render_fallback is not None:
            body["render_fallback"] = bool(render_fallback)
        return c.dumps(c.call_portal("search_and_read", body))
    except Exception as e:
        return f"Error: {e}"


def news(query: str, max_results: Optional[int] = None, **filters: Any) -> str:
    """Recent news articles in one paid call ($0.008, direct x402 only; no results, no charge)."""
    try:
        if not query or not str(query).strip():
            raise c.AgentSearchError("query must not be empty")
        if not c.has_wallet_key():
            raise c.AgentSearchError(c.paid_only_message("agentsearch_news_search"))
        body: dict[str, Any] = {"query": query, **_filters(filters)}
        if max_results is not None:
            body["max_results"] = max(1, min(int(max_results), 10))
        return c.dumps(c.call_portal("news", body))
    except Exception as e:
        return f"Error: {e}"


def _shot_dir() -> str:
    d = (os.environ.get("AGENTSEARCH_SCREENSHOT_DIR") or "").strip() or os.path.join(tempfile.gettempdir(), "agentsearch-screenshots")
    os.makedirs(d, exist_ok=True)
    return d


def screenshot(url: str, format: Optional[str] = None, full_page: Optional[bool] = None,
               viewport: Optional[dict[str, int]] = None) -> str:
    """Website screenshot in one paid call ($0.010, direct x402 only).

    The image is saved to a file (AGENTSEARCH_SCREENSHOT_DIR, default a temp folder) and the returned JSON holds
    its path plus metadata, not the base64 bytes, so the image does not flood the model's context."""
    try:
        if not url or not str(url).strip().lower().startswith(("http://", "https://")):
            raise c.AgentSearchError("url must be a full http(s) URL")
        if not c.has_wallet_key():
            raise c.AgentSearchError(c.paid_only_message("agentsearch_screenshot"))
        body: dict[str, Any] = {"url": str(url).strip()}
        if format is not None:
            body["format"] = format
        if full_page is not None:
            body["full_page"] = bool(full_page)
        if viewport is not None:
            body["viewport"] = {"width": int(viewport["width"]), "height": int(viewport["height"])}
        out = c.call_portal("screenshot", body)
        shot = out.get("screenshot") if isinstance(out, dict) else None
        if isinstance(shot, dict) and isinstance(shot.get("base64"), str):
            ext = "jpg" if str(shot.get("format") or format or "png").lower() in ("jpeg", "jpg") else "png"
            path = os.path.join(_shot_dir(), f"agentsearch-{int(time.time() * 1000)}.{ext}")
            with open(path, "wb") as f:
                f.write(base64.b64decode(shot["base64"]))
            out = {**out, "screenshot": {**{k: v for k, v in shot.items() if k != "base64"}, "path": path,
                                         "base64": "(omitted from text; image saved at path)"}}
        return c.dumps(out)
    except Exception as e:
        return f"Error: {e}"
