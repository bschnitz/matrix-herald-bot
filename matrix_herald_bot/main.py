import asyncio
from injector import Injector
from di.app_module import AppModule
from matrix_herald_bot.services.commands import PrintMatrixTreesOfWatchedSpacesCmd

async def main():
    injector = Injector([AppModule()])
    cmd = injector.get(PrintMatrixTreesOfWatchedSpacesCmd)
    await cmd.print_trees()

if __name__ == "__main__":
    asyncio.run(main())
