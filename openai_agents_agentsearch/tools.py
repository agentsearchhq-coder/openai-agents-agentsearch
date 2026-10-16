from __future__ import annotations

from typing import List, Literal, Optional

from agents import FunctionTool, function_tool

from . import _ops


@function_tool
def agentsearch_search(query: str, max_results: Optional[int] = None) -> str:
    """Live web search. Returns JSON with up to 5 ranked results (title, url, content). Free by default.

    Args:
        query: the search query.
        max_results: 1-5, default 5.
    """
    return _ops.search(query, max_results)


@function_tool
def agentsearch_extract(url: str, max_chars: Optional[int] = None, render_fallback: Optional[bool] = None) -> str:
    """Fetch a URL and return its main content as clean markdown. Best for articles, docs and static pages.
    If the result is empty or thin (JavaScript-heavy page, SPA, app shell), call agentsearch_render on the same URL,
    or pass render_fallback=true to do that automatically (a second $0.005 call). Paid: $0.005 per call (needs a wallet).

    Args:
        url: http(s) URL to extract.
        max_chars: optional cap on returned characters.
        render_fallback: if extract returns thin content, retry with render (extra $0.005).
    """
    return _ops.paid("extract", url=url, formats=["markdown"], max_chars=max_chars, render_fallback=render_fallback)


@function_tool
def agentsearch_render(url: str, max_chars: Optional[int] = None,
                       wait_until: Optional[Literal["domcontentloaded", "load", "networkidle"]] = None) -> str:
    """Render a page in a real headless browser and return markdown. Use when agentsearch_extract returns empty or thin
    content, or for JavaScript-heavy pages (SPAs, content loaded by scripts). Paid: $0.005 per call (needs a wallet).

    Args:
        url: http(s) URL to render.
        max_chars: optional cap on returned characters.
        wait_until: page load event to wait for.
    """
    return _ops.paid("render", url=url, formats=["markdown"], max_chars=max_chars, wait_until=wait_until)


def agentsearch_tools(include_paid: bool = True) -> List[FunctionTool]:
    """All AgentSearch tools. Pass include_paid=False for free search only."""
    return [agentsearch_search, agentsearch_extract, agentsearch_render] if include_paid else [agentsearch_search]
