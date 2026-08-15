import asyncio
import importlib

from fastapi.testclient import TestClient


def test_create_app_uses_injected_redis_settings(monkeypatch, settings):
    main_module = importlib.import_module("njinet_agent.main")
    injected = settings.model_copy(
        update={"redis_url": "redis://injected-cache.internal:6380/2"}
    )
    captured = {}

    class Pool:
        async def aclose(self):
            pass

    class Worker:
        async def async_run(self):
            pass

        async def close(self):
            pass

    async def create_pool(redis_settings):
        captured["pool"] = redis_settings
        return Pool()

    def create_worker(worker_settings, *, handle_signals):
        captured["worker"] = worker_settings.redis_settings
        captured["worker_type"] = worker_settings
        return Worker()

    monkeypatch.setattr(main_module, "create_pool", create_pool)
    monkeypatch.setattr(main_module, "create_worker", create_worker)

    with TestClient(main_module.create_app(injected)):
        pass

    assert captured["pool"].host == "injected-cache.internal"
    assert captured["pool"].port == 6380
    assert captured["pool"].database == 2
    assert captured["worker"] == captured["pool"]

    context = {}
    asyncio.run(captured["worker_type"].on_startup(context))
    assert context["settings"] is injected
