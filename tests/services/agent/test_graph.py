from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from njinet_agent.agents.room_admin.agent import LangGraphAdminChatAgent
from njinet_agent.application.admin_chat import AdminChatRequest


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


async def test_agent_runs_tool_loop(settings):
    llm = FakeLLM()

    async def load_tools(received_settings, jwt):
        assert received_settings is settings
        assert jwt == "jwt"
        return [echo]

    agent = LangGraphAdminChatAgent(
        settings,
        llm_factory=lambda received_settings: llm,
        tool_loader=load_tools,
    )

    reply = await agent.reply(
        AdminChatRequest("room-1", "agent-1", "bot", "hello", "jwt", "request-1")
    )

    assert reply.text == "done"
    assert llm.calls == 2
