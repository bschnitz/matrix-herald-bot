from dataclasses import dataclass, field
from nio import RoomGetStateError
from matrix_herald_bot.model.enums import MatrixNodeType

@dataclass
class MatrixTreeNode:
    id: str
    name: str | None
    canonical_alias: str | None
    type_: MatrixNodeType
    childs: list["MatrixTreeNode"] = field(default_factory=list)
    access: bool = True
    error: RoomGetStateError | None = None

    def get_childs_sorted_by_type(self) -> list["MatrixTreeNode"]:
        type_order = {
            MatrixNodeType.ROOM: 0,
            MatrixNodeType.SPACE: 1,
            MatrixNodeType.UNKNOWN: 2
        }
        return sorted(self.childs, key=lambda child: type_order.get(child.type_, 99))
