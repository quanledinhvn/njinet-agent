from fastapi import APIRouter, Depends

from njinet_agent.application.admin_chat import AdminChatQueue, AdminChatRequest
from njinet_agent.presentation.http.dependencies import get_admin_chat_queue
from njinet_agent.presentation.http.schemas import InvokeRequest, InvokeResponse
from njinet_agent.presentation.http.security import service_auth

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post(
    "/invoke",
    response_model=InvokeResponse,
    dependencies=[Depends(service_auth)],
)
async def invoke(
    request: InvokeRequest,
    queue: AdminChatQueue = Depends(get_admin_chat_queue),
) -> InvokeResponse:
    admin_request = AdminChatRequest(
        room_id=request.roomId,
        agent_id=request.agentId,
        agent_username=request.agentUsername,
        text=request.text,
        jwt=request.jwt,
        request_id=request.requestId,
    )
    await queue.enqueue(admin_request)

    return InvokeResponse(status="accepted", runId=admin_request.request_id)
