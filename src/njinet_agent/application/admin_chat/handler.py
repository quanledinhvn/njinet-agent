import logging

from njinet_agent.application.admin_chat.models import (
    AdminChatReply,
    AdminChatRequest,
)
from njinet_agent.application.admin_chat.ports import (
    AdminChatAgent,
    AdminChatReplySender,
)

logger = logging.getLogger(__name__)


async def handle_admin_chat(
    request: AdminChatRequest,
    *,
    agent: AdminChatAgent,
    reply_sender: AdminChatReplySender,
) -> None:
    try:
        reply = await agent.reply(request)
    except Exception:
        logger.exception("admin chat failed for request %s", request.request_id)
        reply = AdminChatReply(
            status="error",
            text="Something went wrong while processing your request.",
        )

    await reply_sender.send(request, reply)
