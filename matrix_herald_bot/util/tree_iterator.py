from matrix_herald_bot.model.tree_node import MatrixTreeNode

class MatrixTreeIterator:
    def __init__(self, root: MatrixTreeNode) -> None:
        self._stack = [root]

    def __iter__(self):
        return self

    def __next__(self) -> MatrixTreeNode:
        if not self._stack:
            raise StopIteration
        node = self._stack.pop()
        # put childs reversed on stack for them to get popped in their correct order
        self._stack.extend(reversed(node.childs))
        return node

class MatrixTreeLeafIterator:
    def __init__(self, root: MatrixTreeNode) -> None:
        self._stack = [root]

    def __iter__(self):
        return self

    def __next__(self) -> MatrixTreeNode:
        while self._stack:
            node = self._stack.pop()
            if node.childs:
                self._stack.extend(reversed(node.childs))
                continue
            return node

        raise StopIteration
