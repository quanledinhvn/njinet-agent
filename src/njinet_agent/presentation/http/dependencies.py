from fastapi import Request

from njinet_agent.application.admin_chat import AdminChatQueue


def get_admin_chat_queue(request: Request) -> AdminChatQueue:
    return request.app.state.admin_chat_queue
