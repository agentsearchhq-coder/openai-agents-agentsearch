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


# ---- 0.2.1 ----
from openai_agents_agentsearch import _ops, agentsearch_extract, agentsearch_render


def _no_mode(monkeypatch):
    monkeypatch.delenv("AGENTSEARCH_MODE", raising=False)


def _spy_portal(monkeypatch):
    calls = []
    monkeypatch.setattr(_client, "call_portal", lambda op, body, client=None: calls.append((op, body)) or {"ok": True})
    return calls


def test_key_alone_does_not_force_paid(monkeypatch):
    seen = mock(monkeypatch, _client, 200, {"results": []})
    _no_mode(monkeypatch)
    monkeypatch.setenv("AGENTSEARCH_WALLET_PRIVATE_KEY", "0x" + "1" * 64)
    monkeypatch.setattr(_client, "paid_extra_installed", lambda: True)
    portal = _spy_portal(monkeypatch)
    json.loads(call(agentsearch_search, {"query": "hi"}))
    assert not portal and len(seen) == 1 and "relay" in str(seen[0].url)


def test_pocket_key_alone_does_not_force_paid(monkeypatch):
    mock(monkeypatch, _client, 200, {"results": []})
    _no_mode(monkeypatch)
    monkeypatch.setenv("POCKET_PRIVATE_KEY", "0x" + "1" * 64)
    assert _ops.resolve_search_mode(None) == "free"


def test_explicit_paid_and_env_override(monkeypatch):
    mock(monkeypatch, _client, 200, {})
    monkeypatch.setenv("AGENTSEARCH_WALLET_PRIVATE_KEY", "0x" + "1" * 64)
    monkeypatch.setattr(_client, "paid_extra_installed", lambda: True)
    _no_mode(monkeypatch)
    assert _ops.resolve_search_mode("paid") == "paid"
    assert _ops.resolve_search_mode("auto") == "paid"
    monkeypatch.setenv("AGENTSEARCH_MODE", "free")
    assert _ops.resolve_search_mode("paid") == "free"
    monkeypatch.setenv("AGENTSEARCH_MODE", "paid")
    portal = _spy_portal(monkeypatch)
    call(agentsearch_search, {"query": "hi"})
    assert portal and portal[0][0] == "search"


def test_paid_without_extra_falls_back(monkeypatch, caplog):
    seen = mock(monkeypatch, _client, 200, {"results": []})
    _no_mode(monkeypatch)
    monkeypatch.setenv("AGENTSEARCH_WALLET_PRIVATE_KEY", "0x" + "1" * 64)
    monkeypatch.setattr(_client, "paid_extra_installed", lambda: False)
    portal = _spy_portal(monkeypatch)
    with caplog.at_level("WARNING"):
        out = call(agentsearch_search, {"query": "hi", "mode": "paid"})
    assert not out.startswith("Error") and not portal and seen
    assert "[paid] extra" in caplog.text and "0x111" not in caplog.text
    assert _ops.resolve_search_mode("auto") == "free"


def test_bad_mode(monkeypatch):
    _no_mode(monkeypatch)
    assert _ops.search("hi", None, "bogus").startswith("Error: mode must be")


def test_per_ip_wording():
    import openai_agents_agentsearch.tools as t
    assert "per IP" in _client.FREE_LIMIT_MESSAGE and "per user" not in _client.FREE_LIMIT_MESSAGE
    assert "per IP" in agentsearch_search.description
    for tool in agentsearch_tools():
        assert "$" not in tool.description and "per user" not in tool.description
    readme = open(os.path.join(os.path.dirname(__file__), "..", "README.md")).read()
    assert "per user" not in readme and "per IP" in readme and "$0.005" in readme


def test_extract_render_new_params(monkeypatch):
    mock(monkeypatch, _client, 200, {})
    monkeypatch.setenv("AGENTSEARCH_WALLET_PRIVATE_KEY", "0x" + "1" * 64)
    portal = _spy_portal(monkeypatch)
    call(agentsearch_render, {"url": "https://a", "formats": ["html", "links"], "wait_for_selector": "#app"})
    assert portal[-1] == ("render", {"url": "https://a", "formats": ["html", "links"], "wait_for_selector": "#app"})
    assert "wait_for_selector" in agentsearch_render.params_json_schema["properties"]
    assert "formats" in agentsearch_extract.params_json_schema["properties"]
