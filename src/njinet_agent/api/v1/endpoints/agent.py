from arq import ArqRedis
from fastapi import APIRouter, Depends

from njinet_agent.api.deps import get_arq_pool
from njinet_agent.core.security import service_auth
from njinet_agent.schemas.agent import InvokeReq, InvokeResponse
from njinet_agent.services.runtime.launcher import enqueue_run

router = APIRouter()


@router.post(
    "/invoke",
    response_model=InvokeResponse,
    dependencies=[Depends(service_auth)],
)
async def invoke(
    req: InvokeReq,
    pool: ArqRedis = Depends(get_arq_pool),
) -> InvokeResponse:
    await enqueue_run(
        pool,
        req.roomId,
        req.agentId,
        req.agentUsername,
        req.text,
        req.jwt,
        req.requestId,
    )

    return InvokeResponse(status="accepted", runId=req.requestId)
