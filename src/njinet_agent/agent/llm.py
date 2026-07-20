from langchain_openai import ChatOpenAI
from njinet_agent.config import Settings

def build_llm(settings: Settings) -> ChatOpenAI:
  return ChatOpenAI(
    model=settings.llm_model,
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    temperature=0,
  )
