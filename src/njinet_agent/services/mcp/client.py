from langchain_mcp_adapters.client import MultiServerMCPClient

from njinet_agent.core.config import Settings


def build_headers(settings: Settings, actor_id: str, room_id: str, jwt: str) -> dict:
  return {
    "X-Service-Token": settings.service_token,
    "X-Act-As": actor_id,
    "X-Room-Id": room_id,
    "Authorization": f"Bearer {jwt}"
  }

async def load_tools(
  settings: Settings, actor_id: str, room_id: str, jwt: str
) -> list:
  client = MultiServerMCPClient({
    "chat": {
      "transport": "streamable_http",
      "url": f"{settings.nest_url}/mcp",
      "headers": build_headers(settings, actor_id, room_id, jwt),
    }
  })

  return await client.get_tools()