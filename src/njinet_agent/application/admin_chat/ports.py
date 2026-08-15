from typing import Protocol

from njinet_agent.application.admin_chat.models import AdminChatReply, AdminChatRequest


class AdminChatAgent(Protocol):
    async def reply(self, request: AdminChatRequest) -> AdminChatReply: ...


class AdminChatReplySender(Protocol):
    async def send(self, request: AdminChatRequest, reply: AdminChatReply) -> None: ...


class AdminChatQueue(Protocol):
    async def enqueue(self, request: AdminChatRequest) -> None: ...
