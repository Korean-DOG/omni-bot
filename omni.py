import logging
import send
import trigger


class OMNI:
    logger = logging.getLogger('omni.%s' % __name__)
    def __init__(self, provider):
        self.provider = provider
        self.logger.info("Bot created")

    def set_default_action(self, func):
        self.provider.set_default_action(func)

    def set_error_action(self, func):
        self.provider.set_error_action(func)

    def get_who_what(self, update, context):
        return self.provider.get_who_what(update, context)

    async def send_message(self, message, update, context):
        destination = self.provider.get_destination(update, context)
        return await self.provider.send(destination, send.MESSAGE, message)

    async def send_menu(self, message, buttons, update, context):
        destination = self.provider.get_destination(update, context)
        return await self.provider.send(destination, send.MENU,
                                        message, buttons)

    def register_menu_buttons(self, buttons):
        self.provider.register_menu_buttons(buttons)

    def add(self, on, action, trigger_filter=None):
        if on == trigger.ON_MENU and not self.provider.menu_buttons:
            raise Exception(f"Trigger '{on}' is not allowed without "
                            f"registration of menu buttons. Call "
                            f"register_menu_buttons before")
        self.provider.add(on, action, trigger_filter)
        print(f"Trigger '{on}(filter={trigger_filter})' "
                         f"added with action '{action}'")

    def act(self, update, context):
        return self.provider.act(update, context)
