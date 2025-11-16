#!/usr/bin/env python
"""Matrix Herald Bot - Main Entry Point"""

import asyncio
from injector import Injector
from matrix_herald_bot.core.event.listeners import InternalListenerCollectionModule
from matrix_herald_bot.di.app_module import AppModule
from matrix_herald_bot.services.listeners import MatrixListenerCollectionModule
from matrix_herald_bot.services.commands import (
    HeraldBotEventLoop,
    PrintAllUnreadNotifications,
    PrintMatrixTreesOfWatchedSpaceCmd,
    PrintUnreadNotifications,
    PrintUsersInAnnouncementRoom,
    PromoteToServerAdmin,
    PromoteUsersInAnnouncementRoom,
    SendTreeToWidget
)


async def async_main():
    """Async main function that runs the bot."""
    injector = Injector([
        AppModule,
        MatrixListenerCollectionModule,
        InternalListenerCollectionModule
    ])

    # Verschiedene Commands für Testing/Debugging (auskommentiert)
    # cmd = injector.get(PrintMatrixTreesOfWatchedSpaceCmd)
    # await cmd.print_tree()

    # cmd = injector.get(PromoteToServerAdmin)
    # resp = await cmd.promote_to_server_admin("@herald:curiosity-summit.org")
    # print(resp)

    # cmd = injector.get(PrintUsersInAnnouncementRoom)
    # await cmd.print_users_in_announcement_room()

    # cmd = injector.get(PromoteUsersInAnnouncementRoom)
    # await cmd.promote_users_in_announcement_room()

    # cmd = injector.get(SendTreeToWidget)
    # await cmd.send_tree_to_widget("!tdnBzXyr5vKuCEW7tm:curiosity-summit.org")

    # cmd = injector.get(PrintUnreadNotifications)
    # await cmd.print_all_unread_notifications()

    # cmd = injector.get(PrintAllUnreadNotifications)
    # await cmd.print_all_unread_notifications()

    # Starte den Bot Event Loop
    cmd = injector.get(HeraldBotEventLoop)
    await cmd.start()


def main():
    """Main entry point for the installed package."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
