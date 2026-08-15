from typing import Protocol

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool


class AgentWorkflow(Protocol):
    async def invoke(
        self,
        llm: BaseChatModel,
        tools: list[BaseTool],
        text: str,
        recursion_limit: int,
    ) -> str: ...
