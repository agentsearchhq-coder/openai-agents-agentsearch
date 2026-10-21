from __future__ import annotations

from typing import List, Literal, Optional

from agents import FunctionTool, function_tool

from . import _ops


def make_agentsearch_search(mode: Optional[Literal["free", "paid", "auto"]] = None) -> FunctionTool:
    """Build an agentsearch_search tool pinned to a developer-chosen search mode.

    The mode is a developer setting and is not part of the tool schema the model sees.
    AGENTSEARCH_MODE in the environment still takes precedence. Default: free.
    """
    if mode is not None and mode not in ("free", "paid", "auto"):
        raise ValueError(f"mode must be 'free', 'paid' or 'auto' (got {mode!r})")

    @function_tool(name_override="agentsearch_search")
    def agentsearch_search(query: str, max_results: Optional[int] = None) -> str:
        """Live web search. Returns JSON with up to 5 ranked results (title, url, content).
        Free by default (up to 25 searches/day per IP, no key needed).

        Args:
            query: the search query.
            max_results: 1-5, default 5.
        """
        return _ops.search(query, max_results, mode)

    return agentsearch_search


agentsearch_search = make_agentsearch_search()


@function_tool
def agentsearch_extract(url: str, max_chars: Optional[int] = None, render_fallback: Optional[bool] = None,
                        formats: Optional[List[Literal["markdown", "text", "html", "links"]]] = None) -> str:
    """Fetch a URL and return its main content as clean markdown. Best for articles, docs and static pages.
    If the result is empty or thin (JavaScript-heavy page, SPA, app shell), call agentsearch_render on the same URL,
    or pass render_fallback=true to do that automatically (makes a second paid call). Paid tool (needs a wallet).

    Args:
        url: http(s) URL to extract.
        max_chars: optional cap on returned characters.
        render_fallback: if extract returns thin content, retry once with render (a second paid call).
        formats: any of "markdown", "text", "html", "links"; default ["markdown"].
    """
    return _ops.paid("extract", url=url, formats=list(formats) if formats else ["markdown"], max_chars=max_chars,
                     render_fallback=render_fallback)


@function_tool
def agentsearch_render(url: str, max_chars: Optional[int] = None,
                       wait_until: Optional[Literal["domcontentloaded", "load", "networkidle"]] = None,
                       formats: Optional[List[Literal["markdown", "text", "html", "links"]]] = None,
                       wait_for_selector: Optional[str] = None) -> str:
    """Render a page in a real headless browser and return markdown. Use when agentsearch_extract returns empty or thin
    content, or for JavaScript-heavy pages (SPAs, content loaded by scripts). Paid tool (needs a wallet).

    Args:
        url: http(s) URL to render.
        max_chars: optional cap on returned characters.
        wait_until: page load event to wait for.
        formats: any of "markdown", "text", "html", "links"; default ["markdown"].
        wait_for_selector: optional CSS selector to wait for before capturing the page.
    """
    return _ops.paid("render", url=url, formats=list(formats) if formats else ["markdown"], max_chars=max_chars,
                     wait_until=wait_until, wait_for_selector=wait_for_selector)


def agentsearch_tools(include_paid: bool = True,
                      search_mode: Optional[Literal["free", "paid", "auto"]] = None) -> List[FunctionTool]:
    """All AgentSearch tools. Pass include_paid=False for free search only.

    search_mode is a developer setting for search ("free" default, "paid" or "auto"); the model never sees it.
    """
    search = agentsearch_search if search_mode is None else make_agentsearch_search(search_mode)
    return [search, agentsearch_extract, agentsearch_render] if include_paid else [search]
