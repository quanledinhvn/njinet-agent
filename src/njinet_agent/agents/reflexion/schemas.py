from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing.")
    superfluous: str = Field(description="Critique of what is superfluous.")


class AnswerQuestion(BaseModel):
    answer: str = Field(description="Detailed answer to the question.")
    reflection: Reflection = Field(description="Critique of the initial answer.")
    search_queries: list[str] = Field(
        description="One to three queries to improve the answer."
    )


class ReviseAnswer(AnswerQuestion):
    references: list[str] = Field(description="Sources for the revised answer.")


class ReflexionState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    revision_number: int
