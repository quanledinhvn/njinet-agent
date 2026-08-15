from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from njinet_agent.agents.room_admin.workflow import RoomAdminWorkflow


@tool
def echo(text: str) -> str:
    """Return the text it receives."""
    return f"echo: {text}"


class FakeLLM:
    """Fake LLM: asks for a tool call first, returns text afterwards."""

    def __init__(self):
        self.calls = 0

    def bind_tools(self, tools):
        return self

    async def ainvoke(self, messages):
        self.calls += 1
        if self.calls == 1:
            return AIMessage(
                content="",
                tool_calls=[{"name": "echo", "args": {"text": "hi"}, "id": "1"}],
            )
        return AIMessage(content="done")


async def test_graph_runs_agent_tool_loop():
    graph = RoomAdminWorkflow().build_graph(FakeLLM(), [echo])

    result = await graph.ainvoke({"messages": [("user", "hello")]}, {})

    contents = [m.content for m in result["messages"]]
    assert "echo: hi" in contents
    assert "done" in contents
