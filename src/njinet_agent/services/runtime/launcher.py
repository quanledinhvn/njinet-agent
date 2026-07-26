from arq.connections import ArqRedis


def job_id_for(room_id: str) -> str:
    return f"room:{room_id}"


async def enqueue_run(
    pool: ArqRedis,
    room_id: str,
    actor_id: str,
    text: str,
    jwt: str,
    request_id: str,
) -> bool:
    job = await pool.enqueue_job(
        "run_agent_job",
        room_id,
        actor_id,
        text,
        jwt,
        request_id,
        _job_id=job_id_for(room_id),
    )
    return job is not None
