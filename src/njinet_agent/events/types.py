from typing import Literal

from pydantic import BaseModel


class AgentEvent(BaseModel):
  type: Literal["token", "tool_start", "tool_end", "final", "error"]
  data: dict