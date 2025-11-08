import asyncio
import os
from nio import AsyncClient
from nio.events.room_events import RoomSpaceChildEvent
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
    
    # Cache für Space-Hierarchie
    space_hierarchy_cache = set()
    
    async def fetch_space_hierarchy(space_id, visited=None):
        """Rekursiv alle Räume in der Space-Hierarchie sammeln"""
        if visited is None:
            visited = set()
        
        if space_id in visited:
            return set()
        
        visited.add(space_id)
        rooms = {space_id}
        
        try:
            # Hole alle State Events des Space
            state_response = await client.room_get_state(space_id)
            
            # events ist eine Liste von Dicts
            if hasattr(state_response, 'events') and state_response.events:
                for event in state_response.events:
                    # event ist ein Dict
                    event_type = event.get('type')
                    
                    if event_type == 'm.space.child':
                        # Der state_key enthält die Child-Room-ID
                        child_id = event.get('state_key')
                        
                        if child_id and child_id not in visited:
                            rooms.add(child_id)
                            # Rekursiv Kinder durchsuchen
                            child_rooms = await fetch_space_hierarchy(child_id, visited)
                            rooms.update(child_rooms)
        except Exception as e:
            print(f"⚠️ Fehler beim Abrufen der Hierarchie für {space_id}: {e}")
        
        return rooms
    
    async def update_space_hierarchy():
        """Aktualisiere den Cache der Space-Hierarchie"""
        nonlocal space_hierarchy_cache
        if ROOT_SPACE:
            space_hierarchy_cache = await fetch_space_hierarchy(ROOT_SPACE)
        else:
            print("⚠️ ROOT_SPACE nicht gesetzt")
    
    async def is_room_in_hierarchy(room_id):
        """Prüfe, ob ein Raum in der ROOT_SPACE Hierarchie liegt"""
        return room_id in space_hierarchy_cache
    
    # --- Callbacks ---
    async def on_space_child(room, event: RoomSpaceChildEvent):
        """Wird aufgerufen wenn ein Raum zu einem Space hinzugefügt wird"""
        parent_room_id = room.room_id
        child_room_id = event.state_key
        
        # Aktualisiere Hierarchie
        await update_space_hierarchy()
        
        # Prüfe ob der Parent in unserer ROOT_SPACE Hierarchie ist
        if await is_room_in_hierarchy(parent_room_id):
            print(f"📦 Neuer Raum zur ROOT_SPACE Hierarchie hinzugefügt!")
            print(f"Child Room ID: {child_room_id}")
            print(f"Parent Space ID: {parent_room_id}")
            print(f"Sender: {event.sender}")
            print(f"Suggested: {getattr(event, 'suggested', 'N/A')}")
            # Via ist oft im source content
            via = event.source.get('content', {}).get('via', []) if hasattr(event, 'source') else []
            print(f"Via: {via}")
            print()
        else:
            print(f"🔕 Raum {child_room_id} zu Space {parent_room_id} hinzugefügt (außerhalb ROOT_SPACE)")
    
    try:
        # Register callbacks
        client.add_event_callback(on_space_child, RoomSpaceChildEvent)
        
        # --- Initial Sync & Hierarchie laden ---
        print("🔄 Starte initialen Sync...")
        await client.sync(timeout=30000, full_state=True)
        
        # Lade initiale Space-Hierarchie
        print(f"🔄 Lade Space-Hierarchie für {ROOT_SPACE}...")
        await update_space_hierarchy()
        print(f"✅ {len(space_hierarchy_cache)} Räume in der Hierarchie gefunden")
        
        # --- Start listening ---
        print("👂 Höre auf Space-Child Events...")
        await client.sync_forever(timeout=30000)
    
    except KeyboardInterrupt:
        print("\n🛑 Bot wird beendet...")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🧹 Schließe Client-Verbindung...")
        await client.close()
        print("✅ Client geschlossen")

if __name__ == "__main__":
    asyncio.run(main())
