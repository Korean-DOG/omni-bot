"""Provides a unified interface for text-based bot operations across multiple messaging platforms by abstracting provider-specific implementations."""

import logging
import send
import trigger


class OMNI:
    """Text bot with different providers.
   
    Attributes:
        logger (Logger): Logger object.
        provider (BaseProvider): Provider for bot actions.
    """
    logger = logging.getLogger('omni.%s' % __name__)
    def __init__(self, provider):
        """Class constructor.
        
        Args:
            provider (BaseProvider): Provider for bot actions.
        """
        self.provider = provider
        self.logger.info("Bot created")

    def set_default_action(self, func):
        """Setter for default provider action.

        Args:
            func (Callable): Action.
        """
        self.provider.set_default_action(func)

    def set_error_action(self, func):
        """Setter for error provider action.

        Args:
            func (Callable): Action.
        """
        self.provider.set_error_action(func)

    def get_who_what(self, update, context):
        """Get username and request content.

        Args:
            update (telegram.Update | dict): Request info.
            context (telegram.ext.ContextTypes.DEFAULT_TYPE): Chat context.

        Returns:
            (str | int, str): Username and message text.
        """
        return self.provider.get_who_what(update, context)

    async def send_message(self, message, update, context):
        """Send text message.

        Args:
            message (str): Text message.
            update (telegram.Update | dict): Request info.
            context (telegram.ext.ContextTypes.DEFAULT_TYPE): Chat context.

        Returns:
            (telegram.Message | requests.Response): Message object with sended message info.
        """
        destination = self.provider.get_destination(update, context)
        return await self.provider.send(destination, send.MESSAGE, message)

    async def send_menu(self, message, buttons, update, context):
        """Send menu with buttons

        Args:
            message (str): Text message.
            buttons (set): Menu buttons.
            update (telegram.Update | dict): Request info.
            context (telegram.ext.ContextTypes.DEFAULT_TYPE): Chat context.

        Returns:
            Message object with sended message info.
        """
        destination = self.provider.get_destination(update, context)
        return await self.provider.send(destination, send.MENU,
                                        message, buttons)

    def register_menu_buttons(self, buttons):
        """Method for registration inline buttons for menu.

        Args:
            buttons (set): Menu buttons.
        """
        self.provider.register_menu_buttons(buttons)

    def add(self, on, action, trigger_filter=None):
        """Add action on specific trigger with optional filter.

        Args:
            on (str): Trigger type.
            action (Callable): Action.
            trigger_filter (Callable): Function-filter for trigger. Defaults to None.

        Raises:
            Exception: If add menu trigger without registered menu buttons.
        """
        if on == trigger.ON_MENU and not self.provider.menu_buttons:
            raise Exception(f"Trigger '{on}' is not allowed without "
                            f"registration of menu buttons. Call "
                            f"register_menu_buttons before")
        self.provider.add(on, action, trigger_filter)
        print(f"Trigger '{on}(filter={trigger_filter})' "
                         f"added with action '{action}'")

    def act(self, update, context):
        """Performs actions added by the add method.

        Args:
            update (telegram.Update | dict): Request info.
            context (telegram.ext.ContextTypes.DEFAULT_TYPE): Chat context.

        Returns:
            dict: Status code.
        """
        return self.provider.act(update, context)
