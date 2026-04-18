from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


def send_shift_to_user(user_id, payload):
    print("see the payload that i want to send", payload)
    channel_layer = get_channel_layer()
    try:
        json.dumps(payload)
    except Exception as e:
        print("❌ Serialization error:", e)
        raise
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "notify",   # 👈 MUST match method name
            "data": {
                "event": "shift_created",   # 👈 your custom event
                "payload": payload
            }
        }
    )
