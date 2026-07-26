"""Database models.

No models yet. This service owns no tables of its own: Postgres is used only
as a LangGraph checkpoint store, and that schema is managed by
`langgraph-checkpoint-postgres` (see
`njinet_agent.services.runtime.checkpointer`). Business data lives in the
NestJS backend and is reached through MCP tools.

Put ORM models here if this service ever owns its own tables.
"""
