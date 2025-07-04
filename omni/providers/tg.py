"""Provides a concrete implementation of the BaseProvider for Telegram chat bots. 
Handles platform-specific interactions including:
- Bot initialization
- Webhook configuration
- Message routing via Telegram's API
"""

import os
import json
from collections import defaultdict

from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.constants import ParseMode

from omni import send, trigger

from omni.providers.base import BaseProvider


class TG(BaseProvider):
    """Provider for Telegram chat bot.

    Attributes:
        TYPE (str): Type of bot.
        TOKEN (str): The group's access key.
        app (telegram.ext.Application): Application.
        actions_to_handlers (dict): Actions for each trigger.
    """
    TYPE = "TG"
    TOKEN = os.environ["TOKEN"]  # Ключ доступа группы

    def __init__(self):
        """Class constructor"""
        super().__init__()
        self.app = ApplicationBuilder().token(os.environ["TOKEN"]).build()
        self.actions_to_handlers = defaultdict(list)

    async def send(self, who, type, text, buttons=None):
        """Send different types of messages.

        Args:
            who (dict): Dictionary with message destinations.
            type (str): Type of message.
            text (str): Message text.
            buttons (set(str), optional): Menu buttons. Defaults to None.

        Raises:
            Exception: If type is not in send.py.

        Returns:
            telegram.Message: Message, chat and user info.
        """
        print(who, type, text)
        if type == send.MESSAGE:
            return await self.message(who[send.MESSAGE], text)
        elif type == send.MENU:
            return await self.menu(who[send.MENU], text, buttons)
        else:
            raise Exception(f"Unknown type {type}")

    async def message(self, destination, text):
        """Send text message.

        Args:
            destination (int): Chat ID.
            text (str): Message.

        Returns:
            telegram.Message: Message, chat and user info.
        """
        text = text.encode('utf16',
                           errors='surrogatepass').decode('utf16')

        print(f"send message to {destination}: {text}")

        return await self.app.bot.send_message(
            chat_id=destination,
            text=text,
            parse_mode=ParseMode.HTML)

    async def menu(self, who, text, buttons):
        """Send message with menu buttons.

        Args:
            who (telegram.Message): The message included in the update.
            text (str): Message to sent.
            buttons (set(str)): Menu buttons.

        Returns:
            telegram.Message: Message, chat and user info.
        """
        print(f"send menu: {who, text, buttons}")
        return await who.reply_text(text,
                                    reply_markup=self.get_keyboard(buttons),
                                    parse_mode=ParseMode.MARKDOWN)

    def get_keyboard(self, buttons):
        """Create button markup.

        Args:
            buttons (set(str)): Button names.

        Returns:
            telegram.InlineKeyboardMarkup: Button markup.
        """
        keyboard = []

        for start_index in range(0, len(buttons), self.keyboard_lines - 1):
            keyboard_line = []
            for key in buttons[start_index:start_index + self.keyboard_lines-1]:
                button = InlineKeyboardButton(key, callback_data=key)
                keyboard_line.append(button)
            keyboard.append(keyboard_line)
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_who_what(update, context):
        """Get username and message text.

        Args:
            update (telegram.Update): Request info.
            context (telegram.ext.ContextTypes.DEFAULT_TYPE): Chat context.

        Returns:
            (str, str): Username and message text.
        """
        username = (update.message or update.effective_message).chat.username

        if update.callback_query:
            return username, update.callback_query.data

        message = (update.message or update.effective_message).text
        return username, message

    def get_destination(self, update, context):
        """Get destinations for each message type.

        Args:
            update (telegram.Update): Request info.
            context (telegram.ext.ContextTypes.DEFAULT_TYPE): Chat context.

        Returns:
            dict: Dictionary where keys - message types, values - destinations.
        """
        return {send.MESSAGE: update.effective_chat.id,
                send.MENU: (update.message or update.effective_message)}

    async def act(self, update, context):
        """Performs actions added by the add method.

        Args:
            update (telegram.Update): Request info.
            context (telegram.ext.ContextTypes.DEFAULT_TYPE): Chat context.

        Returns:
            dict: Status code.
        """
        print(f"update {update}\ncontext {context}")

        if not self.app._initialized:
            self._really_add()
            await self.app.initialize()
        else:
            self.app.shutdown()
            self._really_add()
            await self.app.initialize()

        try:
            ret = await self.app.process_update(Update.de_json(json.loads(update['body']),
                                                    self.app.bot))
            return self.response(ret)
        except Exception as e:
            print(e)
            return self.response(e)

    def response(self, actions_results):
        """Finalizes request processing by logging results and returning an HTTP status.

        Args:
            actions_results (Any): Results of response.

        Returns:
            dict: Status code of response.
        """
        print(f"Results: '{actions_results}'")
        return {'statusCode': 200}
    

    def _really_add(self):
        print(f"really add: %s" % ({k:[i.__qualname__.split('.')[-1] for i in v]
                                    for k, v in
                                    self.actions_to_handlers.items()},))

        handlers_to_add = {}
        for t, actions in self.actions_to_handlers.items():
            if t == trigger.ON_MESSAGE:
                message_actions = actions[:]
                async def message_func(update, context):
                    print(f"Trigger '{t}' leads to "
                          f"{[a.__qualname__.split('.')[-1] for a in message_actions]}")
                    return [await a(update, context) for a in message_actions]

                handlers_to_add[-1] = [MessageHandler(filters.CHAT,
                                                      message_func)]
            elif t == trigger.ON_MENU:
                menu_actions = actions[:]
                async def menu_func(update, context):
                    print(f"Trigger '{t}' leads to "
                          f"{[a.__qualname__.split('.')[-1] for a in menu_actions]}")
                    return [await a(update, context) for a in menu_actions]

                def filter_menu(data):
                    print(f"We got '{data}' from {self.menu_buttons}")
                    return data in self.menu_buttons

                handlers_to_add[1] = [CallbackQueryHandler(menu_func,
                                                           pattern=filter_menu)]
            else:
                raise Exception(f"Trigger is not expected: '{t}'")

        self.app.add_handlers(handlers_to_add)

    def add(self, on, action, trigger_filter=None):
        """Add action on specific trigger.

        Args:
            on (str): Trigger type.
            action (Callable): Action.
            trigger_filter (Callable): Function-filter for trigger. Defaults to None. Not used.
        """
        self.actions_to_handlers[on].append(action)
