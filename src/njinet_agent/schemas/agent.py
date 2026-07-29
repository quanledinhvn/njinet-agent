from pydantic import BaseModel


class InvokeReq(BaseModel):
    roomId: str
    text: str
    actorId: str
    agentId: str
    agentUsername: str
    requestId: str
    jwt: str


class InvokeResponse(BaseModel):
    status: str
    runId: str