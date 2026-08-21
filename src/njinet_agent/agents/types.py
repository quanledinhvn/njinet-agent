from collections.abc import Awaitable, Callable

from langchain_core.tools import BaseTool

from njinet_agent.core.config import Settings

SearchToolFactory = Callable[[Settings], BaseTool]
ToolLoader = Callable[[Settings, str], Awaitable[list[BaseTool]]]
