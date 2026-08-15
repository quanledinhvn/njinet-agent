from njinet_agent.agents.room_admin.prompt import ORCHESTRATOR_SYSTEM_PROMPT

TOOL_NAMES = (
    "list_members",
    "list_catalog",
    "kick_users",
    "add_sub_agents",
    "remove_sub_agents",
)
FORBIDDEN = ("resolve_members", "resolve_catalog", "all=true", "at most 10 words")


def test_prompt_contains_all_tool_names():
    for name in TOOL_NAMES:
        assert name in ORCHESTRATOR_SYSTEM_PROMPT


def test_prompt_does_not_contain_old_names_or_placeholder():
    for forbidden in FORBIDDEN:
        assert forbidden not in ORCHESTRATOR_SYSTEM_PROMPT
