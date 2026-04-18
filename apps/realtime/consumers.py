# shifts/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

# shifts/consumers.py


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("lets connect")
        print("see the self", self)
        user = self.scope["user"]
        print("see the user", user)

        if user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print("lets disconnect")
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # # IMPORTANT: name must match "type"
    # async def shift_created(self, event):
    #     await self.send(text_data=json.dumps({
    #         "type": "shift_created",
    #         "data": event["data"]
    #     }))
    async def notify(self, event):
        await self.send(text_data=json.dumps({
            "type": event["type"],
            "data": event["data"]
        }))
