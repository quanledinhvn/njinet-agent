from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver

from njinet_agent.agent.graph import build_graph


@tool
def echo(text: str) -> str:
    """Trả lại text nhận vào."""
    return f"echo: {text}"


class FakeLLM:
    """LLM giả: lần đầu đòi gọi tool, lần sau trả text."""

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
    graph = build_graph(FakeLLM(), [echo], MemorySaver())

    cfg = {"configurable": {"thread_id": "room:test"}}
    result = await graph.ainvoke({"messages": [("user", "hello")]}, cfg)
    
    contents = [m.content for m in result["messages"]]
    assert "echo: hi" in contents      # tool đã chạy
    assert "done" in contents          # LLM trả text cuối