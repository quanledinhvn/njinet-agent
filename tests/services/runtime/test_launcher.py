import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from njinet_agent.core.exceptions import EnqueueError
from njinet_agent.services.runtime.launcher import enqueue_run, job_id_for


def test_job_id_is_per_request():
    assert job_id_for("abc", "req-1") == "room:abc:req-1"
    assert job_id_for("abc", "req-1") != job_id_for("abc", "req-2")


async def test_enqueue_passes_args_and_dedupe_id(fake_pool):
    await enqueue_run(
        fake_pool, "r-1", "agent-1", "agent-bot", "hi", "jwt-abc", "req-1"
    )

    args, kwargs = fake_pool.jobs[0]
    assert args == (
        "run_agent_job",
        "r-1",
        "agent-1",
        "agent-bot",
        "hi",
        "jwt-abc",
        "req-1",
    )
    assert kwargs["_job_id"] == "room:r-1:req-1"


async def test_raises_when_job_deduped(fake_pool):
    async def already_queued(*args, **kwargs):
        return None

    fake_pool.enqueue_job = already_queued

    with pytest.raises(EnqueueError):
        await enqueue_run(
            fake_pool, "r-1", "agent-1", "agent-bot", "hi", "j", "req-1"
        )


async def test_raises_when_redis_unreachable(fake_pool):
    async def redis_down(*args, **kwargs):
        raise RedisConnectionError("connection refused")

    fake_pool.enqueue_job = redis_down

    with pytest.raises(EnqueueError):
        await enqueue_run(
            fake_pool, "r-1", "agent-1", "agent-bot", "hi", "j", "req-1"
        )
