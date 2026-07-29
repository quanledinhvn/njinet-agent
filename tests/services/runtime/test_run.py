from contextlib import asynccontextmanager

import pytest
from langchain_core.messages import AIMessage

import njinet_agent.services.runtime.run as run_module
from njinet_agent.services.runtime.run import run_agent


class FakeGraph:
    def __init__(self, reply="done"):
        self.reply = reply
        self.calls = []

    async def ainvoke(self, state, cfg):
        self.calls.append((state, cfg))
        return {"messages": [AIMessage(content=self.reply)]}


@asynccontextmanager
async def fake_checkpointer(settings):
    yield None


async def _async_return(value):
    return value


@pytest.fixture
def graph() -> FakeGraph:
    return FakeGraph()


@pytest.fixture
def sent_replies(monkeypatch) -> list:
    """Records the kwargs of every send_reply call."""
    calls: list = []

    async def fake_send_reply(settings, **kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(run_module, "send_reply", fake_send_reply)
    return calls


@pytest.fixture
def patched_run(monkeypatch, graph) -> FakeGraph:
    """Replace the LLM, MCP tools and checkpointer with fakes."""
    monkeypatch.setattr(run_module, "load_tools", lambda *a, **k: _async_return([]))
    monkeypatch.setattr(run_module, "build_llm", lambda settings: None)
    monkeypatch.setattr(run_module, "build_graph", lambda llm, tools, cp: graph)
    monkeypatch.setattr(run_module, "open_checkpointer", fake_checkpointer)
    return graph


async def test_publishes_final_event(settings, sent_replies, patched_run):
    await run_agent(
        settings=settings,
        room_id="r",
        agent_id="agent-1",
        agent_username="agent-bot",
        text="hi",
        jwt="j",
        request_id="req-1",
    )

    assert len(sent_replies) == 1
    call = sent_replies[0]
    assert call["status"] == "final"
    assert call["text"] == "done"
    assert call["agent_id"] == "agent-1"
    assert call["agent_username"] == "agent-bot"


async def test_passes_thread_id_and_recursion_limit(
    settings, sent_replies, patched_run
):
    await run_agent(
        settings=settings,
        room_id="r",
        agent_id="agent-1",
        agent_username="agent-bot",
        text="hi",
        jwt="j",
        request_id="req-1",
    )

    state, cfg = patched_run.calls[0]
    assert state == {"messages": [("user", "hi")]}
    assert cfg["configurable"]["thread_id"] == "room:r"
    assert cfg["recursion_limit"] == settings.recursion_limit


async def test_publishes_error_event_on_failure(
    settings, sent_replies, monkeypatch, patched_run
):
    def boom(*args, **kwargs):
        raise RuntimeError("mcp down")

    monkeypatch.setattr(run_module, "load_tools", boom)

    await run_agent(
        settings=settings,
        room_id="r",
        agent_id="agent-1",
        agent_username="agent-bot",
        text="hi",
        jwt="j",
        request_id="req-1",
    )

    call = sent_replies[0]
    assert call["status"] == "error"
