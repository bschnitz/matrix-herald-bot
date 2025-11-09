from injector import inject, singleton
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.connection.connection import Connection
from matrix_herald_bot.services.tree_builder import MatrixTreeBuilder
from matrix_herald_bot.services.tree_printer import MatrixTreePrinter

@singleton
class PrintMatrixTreesOfWatchedSpacesCmd:
    @inject
    def __init__(self, config: Configuration, connection: Connection,
                 tree_builder: MatrixTreeBuilder, tree_printer: MatrixTreePrinter):
        self.config = config
        self.connection = connection
        self.tree_builder = tree_builder
        self.tree_printer = tree_printer

    async def print_trees(self):
        await self.connection.connect()
        for space_id in self.config.watched_spaces:
            root_node = await self.tree_builder.fetch_tree(space_id)
            self.tree_printer.print_matrix_tree(root_node)
            print("\n" + "=" * 40 + "\n")
        await self.connection.close()
