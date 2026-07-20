from njinet_agent.events.publisher import channel_for, encode_event
from njinet_agent.events.types import AgentEvent
import json

def test_channel_for_room():
    assert channel_for("abc") == "room:abc"


def test_encode_event_is_json():
    event = AgentEvent(type="token", data={"text": "hi"})

    parsed = json.loads(encode_event(event))
    
    assert parsed == {"type": "token", "data": {"text": "hi"}}