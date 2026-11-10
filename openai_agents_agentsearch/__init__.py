"""OpenAI Agents SDK function tools for AgentSearch."""
from importlib import metadata

from ._client import AgentSearchError, FREE_LIMIT_MESSAGE, reset_session_budget, session_spent_atomic
from .tools import agentsearch_extract, agentsearch_render, agentsearch_search, agentsearch_search_and_read, agentsearch_tools, make_agentsearch_search

try:
    __version__ = metadata.version("openai-agents-agentsearch")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = ""

__all__ = ["agentsearch_search", "agentsearch_extract", "agentsearch_render", "agentsearch_search_and_read", "agentsearch_tools", "make_agentsearch_search", "AgentSearchError",
           "FREE_LIMIT_MESSAGE", "reset_session_budget", "session_spent_atomic", "__version__"]
