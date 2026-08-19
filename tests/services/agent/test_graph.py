from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from njinet_agent.agents.room_admin.agent import LangGraphAdminChatAgent
from njinet_agent.application.admin_chat import AdminChatRequest


@tool
def echo(text: str) -> str:
    """Return the text it receives."""
    return f"echo: {text}"


class FakeLLM(FakeMessagesListChatModel):
    """Fake LLM: asks for a tool call first, returns text afterwards."""

    def bind_tools(self, tools, **kwargs):
        return self


async def test_agent_runs_tool_loop(settings):
    llm = FakeLLM(
        responses=[
            AIMessage(
                content="",
                tool_calls=[{"name": "echo", "args": {"text": "hi"}, "id": "1"}],
            ),
            AIMessage(content="done"),
            AIMessage(content="unexpected"),
        ]
    )

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
    assert llm.i == 2
