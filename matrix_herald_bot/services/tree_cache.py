from injector import inject, singleton
from matrix_herald_bot.model.tree import MatrixTree

@singleton
class MatrixTreeCache:
    @inject
    def __init__(self):
        self.trees: dict[str, MatrixTree] = {}

    def __getitem__(self, room_id: str) -> MatrixTree:
        return self.trees[room_id]

    def __setitem__(self, room_id: str, tree: MatrixTree):
        self.trees[room_id] = tree

    def __contains__(self, room_id: str) -> bool:
        return room_id in self.trees

    def __delitem__(self, room_id: str):
        del self.trees[room_id]

    def __iter__(self):
        return iter(self.trees)

    def __len__(self):
        return len(self.trees)

    def get(self, room_id: str, default=None) -> MatrixTree | None:
        return self.trees.get(room_id, default)
