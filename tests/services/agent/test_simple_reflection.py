from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage, HumanMessage

from njinet_agent.agents.simple_reflection.agent import SimpleReflectionAgent


async def test_agent_alternates_generation_and_reflection_until_limit(settings):
    llm = FakeListChatModel(
        responses=[f"response-{index}" for index in range(1, 8)]
    )

    agent = SimpleReflectionAgent(
        settings=settings,
        llm_factory=lambda _: llm,
    )

    result = await agent.invoke({"messages": [HumanMessage(content="Write a tweet")]})

    assert [type(message) for message in result["messages"]] == [
        HumanMessage,
        AIMessage,
        HumanMessage,
        AIMessage,
        HumanMessage,
        AIMessage,
        HumanMessage,
        AIMessage,
    ]
    assert [message.content for message in result["messages"]] == [
        "Write a tweet",
        "response-1",
        "response-2",
        "response-3",
        "response-4",
        "response-5",
        "response-6",
        "response-7",
    ]
