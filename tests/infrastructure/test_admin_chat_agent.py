from langchain_core.messages import AIMessage

from njinet_agent.agents.room_admin.agent import LangGraphAdminChatAgent
from njinet_agent.application.admin_chat import AdminChatRequest


async def test_agent_builds_reply_from_request_scoped_dependencies(settings):
    captured: dict = {}

    async def load_tools(received_settings, jwt):
        assert received_settings is settings
        assert jwt == "jwt"
        return []

    class LLM:
        def bind_tools(self, tools):
            captured["tools"] = tools
            return self

        async def ainvoke(self, messages):
            captured["messages"] = messages
            return AIMessage(content="done")

    agent = LangGraphAdminChatAgent(
        settings,
        llm=LLM(),
        tool_loader=load_tools,
    )

    reply = await agent.reply(
        AdminChatRequest("room-1", "agent-instance-42", "bot", "hi", "jwt", "request-1")
    )

    assert reply.text == "done"
    assert captured["tools"] == []
    assert captured["messages"][-1].content == "hi"
