from langchain_openai import ChatOpenAI

from njinet_agent.core.config import Settings


def build_llm(settings: Settings) -> ChatOpenAI:
  return ChatOpenAI(
    model=settings.llm_model,
    api_key=settings.llm_api_key,
    temperature=0,
  )
