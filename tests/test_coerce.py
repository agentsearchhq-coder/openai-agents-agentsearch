"""0.5.4: free_search / check_query tolerate tool-input dicts and other wrong-typed args."""
import json

import httpx
import pytest

from openai_agents_agentsearch import _client as c


def _client():
    seen = []

    def handler(req):
        seen.append(json.loads(req.content))
        return httpx.Response(200, json={"results": []})

    return httpx.Client(transport=httpx.MockTransport(handler)), seen


def test_query_dict_is_unwrapped():
    cl, seen = _client()
    c.free_search({"query": "llama release", "max_results": 3}, None, client=cl)
    assert seen == [{"query": "llama release"}]


def test_config_dict_in_max_results_slot_is_ignored():
    cl, seen = _client()
    c.free_search("hello world", {"callbacks": [], "tags": [], "configurable": {}}, client=cl)
    assert seen == [{"query": "hello world"}]


def test_max_results_variants():
    cl, seen = _client()
    for v in ({"max_results": 3}, {"value": {"max_results": "2"}}, "4", 99.7, "lots", 0, True, float("nan")):
        c.free_search("hello", v, client=cl)
    assert [b.get("max_results") for b in seen] == [3, 2, 4, 5, None, 1, None, None]


@pytest.mark.parametrize("q", [None, "", "   ", {}, {"query": ""}, {"max_results": 3}, [], True, "a"])
def test_bad_query_fails_locally(q):
    cl, seen = _client()
    with pytest.raises(c.AgentSearchError) as e:
        c.free_search(q, None, client=cl)
    assert "query" in str(e.value) and "Nothing was sent or charged" in str(e.value)
    assert seen == []


def test_check_query_and_coerce():
    assert c.check_query({"query": " abc "}) == "abc"
    assert c.check_query({"input": {"q": "xyz"}}) == "xyz"
    assert c.check_query(2026) == "2026"
    assert c.coerce_max_results({"foo": 1}) is None
    assert c.coerce_max_results({"num_results": "12"}, 1, 10) == 10
    assert c.coerce_max_results(" 7 ") == 5


def test_tool_path_dict_max_results_and_query_never_reach_relay(monkeypatch):
    from openai_agents_agentsearch import _ops
    cl, seen = _client()
    monkeypatch.setenv("AGENTSEARCH_MODE", "free")
    real = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda *a, **k: cl)
    out = _ops.search({"query": "hello there"}, {"callbacks": []}, "free")
    assert not out.startswith("Error"), out
    assert seen == [{"query": "hello there"}]
    seen.clear()
    assert _ops.search(None, 3, "free").startswith("Error: query")
    assert seen == []
