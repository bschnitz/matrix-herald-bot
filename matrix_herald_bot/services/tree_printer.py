from injector import singleton, inject
from matrix_herald_bot.model.tree_node import MatrixTreeNode
from matrix_herald_bot.model.enums import MatrixNodeType

@singleton
class MatrixTreePrinter:
    @inject
    def __init__(self):
        pass

    def print_matrix_tree(self, node: MatrixTreeNode, indent: int = 0):
        prefix = " " * indent
        type_symbol = {
            MatrixNodeType.SPACE: "[SPACE]",
            MatrixNodeType.ROOM: "[ROOM]",
            MatrixNodeType.UNKNOWN: "[UNKNOWN]",
        }.get(node.type_, "[?]")

        name = node.name or ""
        alias = node.canonical_alias or ""

        print(f"{prefix}{type_symbol} {name}")
        print(f"{prefix}  id: {node.id}")
        if alias:
            print(f"{prefix}  alias: {alias}")
        if node.error:
            print(f"{prefix}  error: {node.error}")
        print(f"{prefix}  access: {'True' if node.access else 'False'}")

        if node.childs:
            print(f"{prefix}  childs:")
            for child in node.get_childs_sorted_by_type():
                self.print_matrix_tree(child, indent + 4)
