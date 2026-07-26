import json
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
def patched_run(monkeypatch, graph) -> FakeGraph:
    """Replace the LLM, MCP tools and checkpointer with fakes."""
    monkeypatch.setattr(run_module, "load_tools", lambda *a, **k: _async_return([]))
    monkeypatch.setattr(run_module, "build_llm", lambda settings: None)
    monkeypatch.setattr(run_module, "build_graph", lambda llm, tools, cp: graph)
    monkeypatch.setattr(run_module, "open_checkpointer", fake_checkpointer)
    return graph


async def test_publishes_final_event(settings, fake_redis, patched_run):
    await run_agent(
        settings=settings,
        redis=fake_redis,
        room_id="r",
        actor_id="u",
        text="hi",
        jwt="j",
    )

    assert len(fake_redis.published) == 1
    channel, payload = fake_redis.published[0]
    assert channel == "room:r"
    assert json.loads(payload) == {"type": "final", "data": {"text": "done"}}


async def test_passes_thread_id_and_recursion_limit(settings, fake_redis, patched_run):
    await run_agent(
        settings=settings,
        redis=fake_redis,
        room_id="r",
        actor_id="u",
        text="hi",
        jwt="j",
    )

    state, cfg = patched_run.calls[0]
    assert state == {"messages": [("user", "hi")]}
    assert cfg["configurable"]["thread_id"] == "room:r"
    assert cfg["recursion_limit"] == settings.recursion_limit


async def test_publishes_error_event_on_failure(
    settings, fake_redis, monkeypatch, patched_run
):
    def boom(*args, **kwargs):
        raise RuntimeError("mcp down")

    monkeypatch.setattr(run_module, "load_tools", boom)

    await run_agent(
        settings=settings,
        redis=fake_redis,
        room_id="r",
        actor_id="u",
        text="hi",
        jwt="j",
    )

    channel, payload = fake_redis.published[0]
    assert channel == "room:r"
    assert json.loads(payload) == {"type": "error", "data": {"message": "mcp down"}}
