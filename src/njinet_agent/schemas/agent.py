from pydantic import BaseModel


class InvokeReq(BaseModel):
    roomId: str
    threadId: str
    text: str
    actorId: str
    requestId: str
    jwt: str


class InvokeResponse(BaseModel):
    status: str
    runId: str