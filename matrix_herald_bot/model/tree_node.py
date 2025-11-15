from dataclasses import dataclass, field
from nio import RoomGetStateError
from matrix_herald_bot.model.enums import MatrixNodeType

@dataclass
class MatrixWidget:
    widget_id: str
    room_id: str

@dataclass
class MatrixTreeNode:
    id: str
    name: str | None
    canonical_alias: str | None
    type_: MatrixNodeType
    childs: list["MatrixTreeNode"] = field(default_factory=list)
    access: bool = True
    error: RoomGetStateError | None = None
    public: bool = False
    herald_widget: str | None = None

    def get_childs_sorted_by_type(self) -> list["MatrixTreeNode"]:
        type_order = {
            MatrixNodeType.ROOM: 0,
            MatrixNodeType.SPACE: 1,
            MatrixNodeType.UNKNOWN: 2
        }
        return sorted(self.childs, key=lambda child: type_order.get(child.type_, 99))

    def convert_to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "canonical_alias": self.canonical_alias,
            "type": self.type_.name,
            "public": self.public,
            "access": self.access,
            "error": str(self.error) if self.error else None,
            "childs": [child.convert_to_dict() for child in self.childs]
        }
