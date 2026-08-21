from langchain_core.tools import StructuredTool
from langgraph.graph import END

from njinet_agent.agents.reflexion.agent import ReflexionAgent
from njinet_agent.agents.reflexion.schemas import ReflexionState


def search_tool_factory(_: object) -> StructuredTool:
    return StructuredTool.from_function(
        lambda query: query,
        name="search",
        description="Return the query without using an external search provider.",
    )


def test_agent_continues_before_search_budget_is_reached(settings) -> None:
    agent = ReflexionAgent(
        settings=settings,
        llm=object(),
        search_tool_factory=search_tool_factory,
        max_iterations=2,
    )
    state: ReflexionState = {
        "messages": [],
        "revision_number": 1,
    }

    assert agent._should_continue(state) == "tools"


def test_agent_stops_when_search_budget_is_reached(settings) -> None:
    agent = ReflexionAgent(
        settings=settings,
        llm=object(),
        search_tool_factory=search_tool_factory,
        max_iterations=2,
    )
    state: ReflexionState = {
        "messages": [],
        "revision_number": 2,
    }

    assert agent._should_continue(state) == END
