import asyncio
from injector import Injector
from matrix_herald_bot.di.app_module import AppModule
from matrix_herald_bot.services.listeners import ListenerCollectionModule
from matrix_herald_bot.services.commands import (
    HeraldBotEventLoop,
    PrintAllUnreadNotifications,
    PrintMatrixTreesOfWatchedSpacesCmd,
    PrintUnreadNotifications,
    PrintUsersInAnnouncementRoom,
    PromoteToServerAdmin,
    PromoteUsersInAnnouncementRoom,
    SendTreeToWidget
)


async def main():
    injector = Injector([AppModule, ListenerCollectionModule])

    #cmd = injector.get(PrintMatrixTreesOfWatchedSpacesCmd)
    #await cmd.print_trees()

    #cmd = injector.get(PromoteToServerAdmin)
    #resp = await cmd.promote_to_server_admin("@herald:curiosity-summit.org")
    #print(resp)

    #cmd = injector.get(PrintUsersInAnnouncementRoom)
    #await cmd.print_users_in_announcement_room()

    #cmd = injector.get(PromoteUsersInAnnouncementRoom)
    #await cmd.promote_users_in_announcement_room()

    #cmd = injector.get(SendTreeToWidget)
    #await cmd.send_tree_to_widget("!tdnBzXyr5vKuCEW7tm:curiosity-summit.org")

    #cmd = injector.get(PrintUnreadNotifications)
    #await cmd.print_all_unread_notifications()

    #cmd = injector.get(PrintAllUnreadNotifications)
    #await cmd.print_all_unread_notifications()

    cmd = injector.get(HeraldBotEventLoop)
    await cmd.start()

if __name__ == "__main__":
    asyncio.run(main())
