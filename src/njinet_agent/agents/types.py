from collections.abc import Awaitable, Callable

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from njinet_agent.core.config import Settings

LLMFactory = Callable[[Settings], BaseChatModel]
SearchToolFactory = Callable[[Settings], BaseTool]
ToolLoader = Callable[[Settings, str], Awaitable[list[BaseTool]]]
