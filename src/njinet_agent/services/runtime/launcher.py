from arq.connections import ArqRedis
from redis.exceptions import RedisError

from njinet_agent.core.exceptions import EnqueueError


def job_id_for(room_id: str) -> str:
    return f"room:{room_id}"


async def enqueue_run(
    pool: ArqRedis,
    room_id: str,
    actor_id: str,
    text: str,
    jwt: str,
    request_id: str,
) -> None:
    try:
        job = await pool.enqueue_job(
            "run_agent_job",
            room_id,
            actor_id,
            text,
            jwt,
            request_id,
            _job_id=job_id_for(room_id),
        )
    except RedisError as exc:
        raise EnqueueError("queue unavailable") from exc

    if job is None:
        raise EnqueueError(f"a run is already in progress for room {room_id}")
