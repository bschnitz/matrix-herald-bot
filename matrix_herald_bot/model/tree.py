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

class MatrixTree:
    def __init__(self, root: MatrixTreeNode) -> None:
        self._root: MatrixTreeNode = root
        self._cache_build = False
        self._child_id_cache: list[str] = []
        self._herald_widget_cache: list[MatrixWidget] = []

    @property
    def root(self) -> MatrixTreeNode:
        return self._root

    @root.setter
    def root(self, value: MatrixTreeNode):
        self._root = value
        self._cache_build = False

    @property
    def child_ids(self) -> list[str]:
        if not self._cache_build:
            self._build_cache()
        return self._child_id_cache

    @property
    def herald_widgets(self) -> list[MatrixWidget]:
        if not self._cache_build:
            self._build_cache()
        return self._herald_widget_cache

    def _build_cache(self):
        stack = [self._root]
        self._child_id_cache = []
        self._herald_widget_cache = []
        while stack:
            node = stack.pop()
            self._child_id_cache.append(node.id)
            if node.herald_widget is not None:
                widget = MatrixWidget(node.herald_widget, node.id)
                self._herald_widget_cache.append(widget)
            stack.extend(node.childs)

    def _collect_child_ids(self) -> list[str]:
        stack = [self._root]
        child_ids = []
        while stack:
            node = stack.pop()
            child_ids.append(node.id)
            stack.extend(node.childs)
        return child_ids

    def convert_to_dict(self):
        return self.root.convert_to_dict()
