class AgentError(Exception):
    """Business error raised by the agent service."""

    status_code = 500
    code = "agent_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class EnqueueError(AgentError):
    """Failed to push a job onto the queue."""

    status_code = 503
    code = "enqueue_failed"
