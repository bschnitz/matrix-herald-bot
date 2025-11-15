from matrix_herald_bot.model.tree_node import MatrixTreeNode, MatrixWidget
from matrix_herald_bot.util.tree_iterator import MatrixTreeIterator

class MatrixTree:
    def __init__(self, root: MatrixTreeNode) -> None:
        self._root: MatrixTreeNode = root
        self._cache_build = False
        self._child_id_cache: list[str] = []
        self._herald_widget_cache: list[MatrixWidget] = []
        self.childs_which_need_user_promotion = []

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

    def convert_to_dict(self):
        return self.root.convert_to_dict()

    def add_node_to_tree(self, parent_room_id: str, node: MatrixTreeNode):
        for tree_node in MatrixTreeIterator(self._root):
            if tree_node.id == parent_room_id:
                tree_node.childs.append(node)
                self._cache_build = False
                return

        raise ValueError(f"Parent room '{parent_room_id}' not found in tree.")
