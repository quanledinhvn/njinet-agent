from arq.connections import ArqRedis
from redis.exceptions import RedisError

from njinet_agent.core.exceptions import EnqueueError


def job_id_for(room_id: str, request_id: str) -> str:
    return f"room:{room_id}:{request_id}"


async def enqueue_run(
    pool: ArqRedis,
    room_id: str,
    actor_id: str,
    agent_id: str,
    agent_username: str,
    text: str,
    jwt: str,
    request_id: str,
) -> None:
    try:
        job = await pool.enqueue_job(
            "run_agent_job",
            room_id,
            actor_id,
            agent_id,
            agent_username,
            text,
            jwt,
            request_id,
            _job_id=job_id_for(room_id, request_id),
        )
    except RedisError as exc:
        raise EnqueueError("queue unavailable") from exc

    if job is None:
        raise EnqueueError(
            f"request {request_id} is already enqueued for room {room_id}"
        )
