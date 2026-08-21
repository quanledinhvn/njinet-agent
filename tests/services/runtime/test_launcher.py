import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from njinet_agent.application.admin_chat import AdminChatRequest
from njinet_agent.application.errors import EnqueueError
from njinet_agent.infrastructure.queue.arq import enqueue_admin_chat, job_id_for
from njinet_agent.presentation import worker as worker_module
from njinet_agent.presentation.worker import WorkerSettings, run_admin_chat_job


def test_worker_settings_defines_optional_lifecycle_hooks():
    assert WorkerSettings.on_startup is None
    assert WorkerSettings.on_shutdown is None


async def test_job_uses_settings_from_worker_context(monkeypatch, settings):
    captured = {}
    agent = object()

    async def handle_admin_chat(request, *, agent, reply_sender):
        captured["agent"] = agent
        captured["sender_settings"] = reply_sender.settings

    monkeypatch.setattr(worker_module, "handle_admin_chat", handle_admin_chat)

    await run_admin_chat_job(
        {"settings": settings, "admin_chat_agent": agent},
        "room-1",
        "room-admin",
        "bot",
        "hi",
        "jwt",
        "request-1",
    )

    assert captured == {"agent": agent, "sender_settings": settings}


def test_job_id_is_per_request():
    assert job_id_for("abc", "req-1") == "room:abc:req-1"
    assert job_id_for("abc", "req-1") != job_id_for("abc", "req-2")


async def test_enqueue_passes_args_and_dedupe_id(fake_pool):
    await enqueue_admin_chat(
        fake_pool,
        AdminChatRequest("r-1", "agent-1", "agent-bot", "hi", "jwt-abc", "req-1"),
    )

    args, kwargs = fake_pool.jobs[0]
    assert args == (
        "run_admin_chat_job",
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
        await enqueue_admin_chat(
            fake_pool,
            AdminChatRequest("r-1", "agent-1", "agent-bot", "hi", "j", "req-1"),
        )


async def test_raises_when_redis_unreachable(fake_pool):
    async def redis_down(*args, **kwargs):
        raise RedisConnectionError("connection refused")

    fake_pool.enqueue_job = redis_down

    with pytest.raises(EnqueueError):
        await enqueue_admin_chat(
            fake_pool,
            AdminChatRequest("r-1", "agent-1", "agent-bot", "hi", "j", "req-1"),
        )
