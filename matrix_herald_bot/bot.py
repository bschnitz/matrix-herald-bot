import asyncio
import os
from nio import AsyncClient, RoomMessageText, RoomCreateEvent
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

HOMESERVER = os.getenv("HOMESERVER")
ACCESS_TOKEN = os.getenv("USER_ACCESS_TOKEN")
ANNOUNCEMENT_ROOM = os.getenv("ANNOUNCEMENT_ROOM")
USER = os.getenv("BOT_USER")
ROOT_SPACE = os.getenv("ROOT_SPACE")

async def main():
    client = AsyncClient(HOMESERVER, USER)
    client.access_token = ACCESS_TOKEN

    # --- Callbacks ---
    async def on_room_create(room, event):
        print("On Room Create")
        print("📦 New room created!")
        # room.room_id existiert, wenn der Raum bekannt ist
        print(f"Room ID: {getattr(room, 'room_id', 'Unknown')}")
        print(f"Sender: {event.sender}")
        print(f"Room Type: {event.room_type}")
        print(f"Federate: {event.federate}")
        print(f"Room Version: {event.room_version}")
        print(f"Raw content: {event.source.get('content', {})}")
        print()

    async def on_message(room, event: RoomMessageText):
        print("On Room Message Text")
        print(event)
        print()
        #print(f"💬 Message in {room.display_name if room else event.room_id}: {event.body}")

    # Register callbacks
    client.add_event_callback(on_room_create, RoomCreateEvent)
    client.add_event_callback(on_message, RoomMessageText)

    # --- Initial Sync ---
    await client.sync(timeout=30000, full_state=True)

    # --- Start listening ---
    await client.sync_forever(timeout=30000)

if __name__ == "__main__":
    asyncio.run(main())
