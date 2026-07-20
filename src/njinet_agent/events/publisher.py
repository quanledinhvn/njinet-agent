from redis.asyncio import Redis

from njinet_agent.events.types import AgentEvent


def channel_for(room_id: str) -> str:
  return f"room:{room_id}"

def encode_event(event: AgentEvent) -> str:
  return event.model_dump_json()


async def publish(redis: Redis, room_id: str, event: AgentEvent) -> None:
  await redis.publish(channel_for(room_id), encode_event(event))