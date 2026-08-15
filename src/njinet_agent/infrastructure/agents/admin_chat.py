from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from langchain_core.language_models import BaseChatModel

from njinet_agent.agents.room_admin.workflow import RoomAdminWorkflow
from njinet_agent.agents.workflow import AgentWorkflow
from njinet_agent.application.admin_chat import AdminChatReply, AdminChatRequest
from njinet_agent.core.config import Settings
from njinet_agent.infrastructure.llm.openai import build_openai_llm
from njinet_agent.infrastructure.mcp.client import load_tools

ToolLoader = Callable[[Settings, str], Awaitable[list[Any]]]
LLMFactory = Callable[[Settings], BaseChatModel]


@dataclass
class LangGraphAdminChatAgent:
    settings: Settings
    llm_factory: LLMFactory = build_openai_llm
    tool_loader: ToolLoader = load_tools
    admin_workflow: AgentWorkflow = field(default_factory=RoomAdminWorkflow)

    async def reply(self, request: AdminChatRequest) -> AdminChatReply:
        tools = await self.tool_loader(self.settings, request.jwt)
        text = await self.admin_workflow.invoke(
            self.llm_factory(self.settings),
            tools,
            request.text,
            self.settings.recursion_limit,
        )
        return AdminChatReply(text=text)
