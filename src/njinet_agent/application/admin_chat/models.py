from dataclasses import dataclass
from typing import Literal

ReplyStatus = Literal["final", "error"]


@dataclass(frozen=True)
class AdminChatRequest:
    room_id: str
    agent_id: str
    agent_username: str
    text: str
    jwt: str
    request_id: str


@dataclass(frozen=True)
class AdminChatReply:
    text: str
    status: ReplyStatus = "final"
