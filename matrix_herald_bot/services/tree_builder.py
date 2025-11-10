from injector import inject, singleton
from nio import RoomGetStateError
from matrix_herald_bot.connection.connection import Connection
from matrix_herald_bot.model.tree_node import MatrixTreeNode
from matrix_herald_bot.model.enums import MatrixNodeType

@singleton
class MatrixTreeBuilder:
    @inject
    def __init__(self, connection: Connection):
        self.connection = connection

    async def fetch_tree(self, room_id: str) -> MatrixTreeNode:
        client = self.connection.get_client_or_raise()

        state_events = await client.room_get_state(room_id)

        name = None
        canonical_alias = None
        is_space = False
        childs = []
        access = True
        error = None
        public = False

        if isinstance(state_events, RoomGetStateError):
            access = False
            error = state_events
        else:
            for ev in state_events.events:
                t = ev["type"]
                if t == "m.room.name":
                    name = ev.get("content", {}).get("name")
                elif t == "m.room.canonical_alias":
                    canonical_alias = ev.get("content", {}).get("canonical_alias")
                elif t == "m.room.create":
                    if ev.get("content", {}).get("type") == "m.space":
                        is_space = True
                elif t == "m.space.child":
                    child_id = ev["state_key"]
                    child_node = await self.fetch_tree(child_id)
                    childs.append(child_node)
                elif t == "m.room.join_rules":
                    join_rule = ev.get("content", {}).get("join_rule")
                    public = join_rule == "public"

        type_ = MatrixNodeType.SPACE if is_space else MatrixNodeType.ROOM

        return MatrixTreeNode(
            room_id,
            name,
            canonical_alias,
            type_,
            childs,
            access,
            error,
            public
        )
