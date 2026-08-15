from njinet_agent.application.admin_chat.handler import handle_admin_chat
from njinet_agent.application.admin_chat.models import AdminChatReply, AdminChatRequest


def request() -> AdminChatRequest:
    return AdminChatRequest(
        room_id="room-1",
        agent_id="room-admin",
        agent_username="bot",
        text="hi",
        jwt="jwt",
        request_id="request-1",
    )


async def test_handle_admin_chat_sends_agent_reply():
    sent: list[tuple[AdminChatRequest, AdminChatReply]] = []

    class Agent:
        async def reply(self, received: AdminChatRequest) -> AdminChatReply:
            assert received == request()
            return AdminChatReply(text="done")

    class Sender:
        async def send(self, received: AdminChatRequest, reply: AdminChatReply) -> None:
            sent.append((received, reply))

    await handle_admin_chat(request(), agent=Agent(), reply_sender=Sender())

    assert sent == [(request(), AdminChatReply(text="done"))]


async def test_handle_admin_chat_sends_error_reply_when_agent_fails():
    sent: list[AdminChatReply] = []

    class FailingAgent:
        async def reply(self, received: AdminChatRequest) -> AdminChatReply:
            raise RuntimeError("LLM unavailable")

    class Sender:
        async def send(self, received: AdminChatRequest, reply: AdminChatReply) -> None:
            sent.append(reply)

    await handle_admin_chat(request(), agent=FailingAgent(), reply_sender=Sender())

    assert sent == [
        AdminChatReply(
            status="error",
            text="Something went wrong while processing your request.",
        )
    ]
