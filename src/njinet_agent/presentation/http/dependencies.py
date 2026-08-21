from fastapi import Request
from langchain_core.language_models import BaseChatModel

from njinet_agent.application.admin_chat import AdminChatQueue


def get_admin_chat_queue(request: Request) -> AdminChatQueue:
    return request.app.state.admin_chat_queue


def get_llm(request: Request) -> BaseChatModel:
    return request.app.state.llm
