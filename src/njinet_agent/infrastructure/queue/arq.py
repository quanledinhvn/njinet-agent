from dataclasses import dataclass

from arq.connections import ArqRedis
from redis.exceptions import RedisError

from njinet_agent.application.admin_chat import AdminChatRequest
from njinet_agent.application.errors import EnqueueError


def job_id_for(room_id: str, request_id: str) -> str:
    return f"room:{room_id}:{request_id}"


@dataclass
class ArqAdminChatQueue:
    pool: ArqRedis

    async def enqueue(self, request: AdminChatRequest) -> None:
        await enqueue_admin_chat(self.pool, request)


async def enqueue_admin_chat(pool: ArqRedis, request: AdminChatRequest) -> None:
    try:
        job = await pool.enqueue_job(
            "run_admin_chat_job",
            request.room_id,
            request.agent_id,
            request.agent_username,
            request.text,
            request.jwt,
            request.request_id,
            _job_id=job_id_for(request.room_id, request.request_id),
        )
    except RedisError as exc:
        raise EnqueueError("queue unavailable") from exc

    if job is None:
        raise EnqueueError(
            f"request {request.request_id} is already enqueued for room "
            f"{request.room_id}"
        )
