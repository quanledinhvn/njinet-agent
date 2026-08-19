from dataclasses import dataclass
from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

from njinet_agent.agents.room_admin.agent import LLMFactory
from njinet_agent.core.config import Settings
from njinet_agent.infrastructure.llm.openai import build_openai_llm


class MessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a viral twitter influencer grading a tweet. Generate "
                "critique and recommendations for the user's tweet. Always "
                "provide detailed recommendations, including requests for length, "
                "virality, style, etc."
            ),
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a twitter techie influencer assistant tasked with writing "
                "excellent twitter posts. Generate the best twitter post possible "
                "for the user's request. If the user provides critique, respond with "
                "a revised version of your previous attempts."
            ),
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


@dataclass
class SimpleReflectionAgent:
    settings: Settings
    llm_factory: LLMFactory = build_openai_llm

    def _build_graph(self, llm: BaseChatModel) -> CompiledStateGraph:
        REFLECT = "reflect"
        GENERATE = "generate"

        generate_chain = generation_prompt | llm
        reflect_chain = reflection_prompt | llm

        async def generation_node(state: MessageGraph):
            return {
                "messages": [
                    await generate_chain.ainvoke({"messages": state["messages"]})
                ]
            }

        async def reflection_node(state: MessageGraph):
            res = await reflect_chain.ainvoke({"messages": state["messages"]})
            return {"messages": [HumanMessage(content=res.content)]}

        def should_continue(state: MessageGraph):
            if len(state["messages"]) > 6:
                return END
            return REFLECT

        builder = StateGraph(state_schema=MessageGraph)
        builder.add_node(GENERATE, generation_node)
        builder.add_node(REFLECT, reflection_node)
        builder.set_entry_point(GENERATE)

        builder.add_conditional_edges(GENERATE, should_continue)
        builder.add_edge(REFLECT, GENERATE)

        return builder.compile()

    async def invoke(self, message: MessageGraph):
        llm = self.llm_factory(self.settings)

        result = await self._build_graph(llm).ainvoke(message)

        return result
