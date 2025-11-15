from dataclasses import dataclass
from matrix_herald_bot.model.tree import MatrixTree

@dataclass
class TreeStructureUpdated:
    tree: MatrixTree
