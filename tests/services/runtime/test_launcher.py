from njinet_agent.services.runtime.launcher import enqueue_run, job_id_for


def test_job_id_is_per_room():
    assert job_id_for("abc") == "room:abc"


async def test_enqueue_passes_args_and_dedupe_id(fake_pool):
    ok = await enqueue_run(fake_pool, "r-1", "u-1", "hi", "jwt-abc", "req-1")

    assert ok is True
    args, kwargs = fake_pool.jobs[0]
    assert args == ("run_agent_job", "r-1", "u-1", "hi", "jwt-abc", "req-1")
    assert kwargs["_job_id"] == "room:r-1"


async def test_returns_false_when_job_deduped(fake_pool):
    async def already_queued(*args, **kwargs):
        return None

    fake_pool.enqueue_job = already_queued

    assert await enqueue_run(fake_pool, "r-1", "u-1", "hi", "j", "req-1") is False
