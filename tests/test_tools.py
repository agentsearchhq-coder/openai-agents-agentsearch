import json
import os

import httpx
import pytest


def mock(monkeypatch, mod, status, body):
    real = httpx.Client
    seen = []

    def handler(r):
        seen.append(r)
        return httpx.Response(status, json=body)
    monkeypatch.setattr(mod.httpx, "Client", lambda **kw: real(transport=httpx.MockTransport(handler)))
    for n in ("AGENTSEARCH_WALLET_PRIVATE_KEY", "POCKET_PRIVATE_KEY"):
        monkeypatch.delenv(n, raising=False)
    return seen

import asyncio

from openai_agents_agentsearch import agentsearch_search, agentsearch_tools, _client


def call(tool, args):
    from agents.tool_context import ToolContext
    a = json.dumps(args)
    ctx = ToolContext(context=None, tool_name=tool.name, tool_call_id="1", tool_arguments=a)
    return asyncio.run(tool.on_invoke_tool(ctx, a))


def test_tools_list():
    assert [t.name for t in agentsearch_tools()] == ["agentsearch_search", "agentsearch_extract", "agentsearch_render"]
    assert "query" in agentsearch_search.params_json_schema["properties"]


def test_free_search(monkeypatch):
    mock(monkeypatch, _client, 200, {"results": [{"title": "t", "url": "https://a", "content": "c"}]})
    out = json.loads(call(agentsearch_search, {"query": "hi", "max_results": 1}))
    assert out["results"][0]["url"] == "https://a"


def test_paid_without_wallet(monkeypatch):
    seen = mock(monkeypatch, _client, 200, {})
    assert "no call was made" in call(agentsearch_tools()[1], {"url": "https://example.com", "max_chars": None}) and not seen


@pytest.mark.skipif(not os.environ.get("AGENTSEARCH_LIVE"), reason="set AGENTSEARCH_LIVE=1")
def test_live_free_search():
    from openai_agents_agentsearch import _ops
    out = json.loads(_ops.search("OpenAI Agents SDK function tools", 2, "free"))
    assert out["results"][0]["url"].startswith("http")
