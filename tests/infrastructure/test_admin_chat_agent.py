from njinet_agent.agents.room_admin.workflow import RoomAdminWorkflow
from njinet_agent.application.admin_chat import AdminChatRequest
from njinet_agent.infrastructure.agents.admin_chat import LangGraphAdminChatAgent


def test_agent_depends_on_workflow_protocol():
    annotation = LangGraphAdminChatAgent.__annotations__["admin_workflow"]

    assert annotation.__name__ == "AgentWorkflow"


def test_agent_creates_its_own_room_admin_workflow(settings):
    first = LangGraphAdminChatAgent(settings)
    second = LangGraphAdminChatAgent(settings)

    assert isinstance(first.admin_workflow, RoomAdminWorkflow)
    assert first.admin_workflow is not second.admin_workflow


async def test_agent_id_is_identity_not_workflow_selector(settings):
    captured: dict = {}

    async def load_tools(received_settings, jwt):
        assert received_settings is settings
        assert jwt == "jwt"
        return ["tool"]

    class Workflow:
        async def invoke(self, llm, tools, text, recursion_limit):
            captured.update(
                llm=llm,
                tools=tools,
                text=text,
                recursion_limit=recursion_limit,
            )
            return "done"

    agent = LangGraphAdminChatAgent(
        settings,
        llm_factory=lambda received_settings: "model",
        tool_loader=load_tools,
        admin_workflow=Workflow(),
    )

    reply = await agent.reply(
        AdminChatRequest("room-1", "agent-instance-42", "bot", "hi", "jwt", "request-1")
    )

    assert reply.text == "done"
    assert captured == {
        "llm": "model",
        "tools": ["tool"],
        "text": "hi",
        "recursion_limit": settings.recursion_limit,
    }
