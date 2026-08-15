from langchain_mcp_adapters.client import MultiServerMCPClient

from njinet_agent.core.config import Settings


def build_headers(settings: Settings, jwt: str) -> dict:
    return {
        "njin-secret-key": settings.njin_secret_key,
        "Authorization": f"Bearer {jwt}",
    }


async def load_tools(settings: Settings, jwt: str) -> list:
    client = MultiServerMCPClient(
        {
            "chat": {
                "transport": "streamable_http",
                "url": f"{settings.njinet_backend_url}/mcp",
                "headers": build_headers(settings, jwt),
            }
        }
    )
    return await client.get_tools()
