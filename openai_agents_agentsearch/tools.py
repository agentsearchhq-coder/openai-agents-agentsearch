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
    def agentsearch_search(query: str, max_results: Optional[int] = None, freshness: Optional[Literal["day", "week", "month", "year"]] = None,
        date_from: Optional[str] = None, date_to: Optional[str] = None, country: Optional[str] = None,
        language: Optional[str] = None, include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None) -> str:
        """Live web search. Returns JSON with up to 5 ranked results (title, url, content).
        Free by default (up to 25 searches/day per IP, no key needed). Paid search also honors the filters below;
        free search ignores them. For recent news use agentsearch_news_search.

        Args:
            query: the search query.
            max_results: 1-5, default 5.
            freshness: only results from the past day, week, month or year (paid only).
            date_from: earliest publish date YYYY-MM-DD (paid only).
            date_to: latest publish date YYYY-MM-DD (paid only).
            country: 2-letter country code such as us or gb (paid only).
            language: language code such as en, es or pt-BR (paid only).
            include_domains: only these domains, up to 5 (paid only).
            exclude_domains: never these domains, up to 5 (paid only).
        """
        return _ops.search(query, max_results, mode, freshness=freshness, date_from=date_from, date_to=date_to, country=country,
                       language=language, include_domains=include_domains, exclude_domains=exclude_domains)

    return agentsearch_search


agentsearch_search = make_agentsearch_search()


@function_tool
def agentsearch_extract(url: str, max_chars: Optional[int] = None, render_fallback: Optional[bool] = None,
                        formats: Optional[List[Literal["markdown", "text", "html", "links"]]] = None,
                        include_links: Optional[bool] = None) -> str:
    """Fetch a URL and return its main content as clean markdown. Best for articles, docs and static pages.
    If the result is empty or thin (JavaScript-heavy page, SPA, app shell), call agentsearch_render on the same URL,
    or pass render_fallback=true to do that automatically (makes a second paid call). Paid tool (needs a wallet).

    Args:
        url: http(s) URL to extract.
        max_chars: optional cap on returned characters (up to 50000).
        render_fallback: if extract returns thin content, retry once with render (a second paid call).
        formats: any of "markdown", "text", "html", "links"; default ["markdown"].
        include_links: also return the page's links.
    """
    return _ops.paid("extract", url=url, formats=list(formats) if formats else ["markdown"], max_chars=max_chars,
                     include_links=include_links, render_fallback=render_fallback)


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


@function_tool
def agentsearch_search_and_read(query: str, num_results: Optional[int] = None, max_chars: Optional[int] = None,
                                render_fallback: Optional[bool] = None, freshness: Optional[Literal["day", "week", "month", "year"]] = None,
        date_from: Optional[str] = None, date_to: Optional[str] = None, country: Optional[str] = None,
        language: Optional[str] = None, include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None) -> str:
    """Search the live web and return the top results with each page's main text in one paid call on AgentSearch's direct x402 API (charged only when at least one page returns text).
    Cheaper than a separate search plus three extracts, and one payment instead of four. Default 3 results (max 5), default 8000 characters per page (max 20000).
    Pass render_fallback=true to render at most one thin page in the same call. Direct x402 only — not available on Pocket. Search itself stays free by default. Paid tool (needs a wallet).

    Args:
        query: the search query.
        num_results: how many top results to read, 1-5, default 3.
        max_chars: max characters of page text per result, default 8000, max 20000.
        render_fallback: if extract is thin, render at most one page in the same $0.009 call.
        freshness: only results from the past day, week, month or year.
        date_from: earliest publish date YYYY-MM-DD.
        date_to: latest publish date YYYY-MM-DD.
        country: 2-letter country code such as us or gb.
        language: language code such as en, es or pt-BR.
        include_domains: only these domains, up to 5.
        exclude_domains: never these domains, up to 5.
    """
    return _ops.search_and_read(query, num_results=num_results, max_chars=max_chars, render_fallback=render_fallback,
                                freshness=freshness, date_from=date_from, date_to=date_to, country=country,
                       language=language, include_domains=include_domains, exclude_domains=exclude_domains)


@function_tool
def agentsearch_news_search(query: str, max_results: Optional[int] = None, freshness: Optional[Literal["day", "week", "month", "year"]] = None,
        date_from: Optional[str] = None, date_to: Optional[str] = None, country: Optional[str] = None,
        language: Optional[str] = None, include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None) -> str:
    """Search recent news articles and return title, URL, snippet, source domain and publish date for each (1-10, default 5).
    Use for current events, company or product news, and anything where recency matters. To read an article in full, pass its
    URL to agentsearch_extract. Paid tool on AgentSearch's direct x402 API (no results, no charge). Needs a wallet.

    Args:
        query: the news search query.
        max_results: 1-10, default 5.
        freshness: only results from the past day, week, month or year.
        date_from: earliest publish date YYYY-MM-DD.
        date_to: latest publish date YYYY-MM-DD.
        country: 2-letter country code such as us or gb.
        language: language code such as en, es or pt-BR.
        include_domains: only these domains, up to 5.
        exclude_domains: never these domains, up to 5.
    """
    return _ops.news(query, max_results, freshness=freshness, date_from=date_from, date_to=date_to, country=country,
                       language=language, include_domains=include_domains, exclude_domains=exclude_domains)


@function_tool
def agentsearch_screenshot(url: str, format: Optional[Literal["png", "jpeg"]] = None, full_page: Optional[bool] = None,
                           viewport_width: Optional[int] = None, viewport_height: Optional[int] = None) -> str:
    """Load a public URL in a real headless browser and capture a PNG or JPEG screenshot of the viewport or the full page
    (up to 4000 px tall), plus title, final URL and HTTP status. Use for visual checks and layout or UI questions; for page
    text use agentsearch_extract. The image is saved to a local file and its path is returned (no base64 in the output).
    Paid tool on AgentSearch's direct x402 API. Needs a wallet.

    Args:
        url: full public http(s) URL to capture.
        format: "png" (default) or "jpeg".
        full_page: capture the whole page instead of the viewport.
        viewport_width: viewport width in CSS pixels (320-1920), e.g. 390 for mobile; default 1280.
        viewport_height: viewport height in CSS pixels (320-1920), e.g. 844 for mobile; default 800.
    """
    vp = None
    if viewport_width or viewport_height:
        vp = {"width": max(320, min(int(viewport_width or 1280), 1920)), "height": max(320, min(int(viewport_height or 800), 1920))}
    return _ops.screenshot(url, format=format, full_page=full_page, viewport=vp)


def agentsearch_tools(include_paid: bool = True,
                      search_mode: Optional[Literal["free", "paid", "auto"]] = None) -> List[FunctionTool]:
    """All AgentSearch tools. Pass include_paid=False for free search only.

    search_mode is a developer setting for search ("free" default, "paid" or "auto"); the model never sees it.
    """
    search = agentsearch_search if search_mode is None else make_agentsearch_search(search_mode)
    paid = [agentsearch_news_search, agentsearch_extract, agentsearch_render, agentsearch_screenshot, agentsearch_search_and_read]
    return [search, *paid] if include_paid else [search]
