import os
import json
from collections import defaultdict

from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram import Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import send
import trigger

from providers.base import BaseProvider


class TG(BaseProvider):
    TYPE = "TG"
    TOKEN = os.environ["TOKEN"]  # Ключ доступа группы

    def __init__(self):
        super().__init__()
        self.app = ApplicationBuilder().token(os.environ["TOKEN"]).build()
        self.actions_to_handlers = defaultdict(list)

    async def send(self, who, type, text, buttons=None):
        print(who, type, text)
        if type == send.MESSAGE:
            return await self.message(who[send.MESSAGE], text)
        elif type == send.MENU:
            return await self.menu(who[send.MENU], text, buttons)
        else:
            raise Exception(f"Unknown type {type}")

    async def message(self, destination, text):
        text = text.encode('utf16',
                           errors='surrogatepass').decode('utf16')

        print(f"send message to {destination}: {text}")

        return await self.app.bot.send_message(
            chat_id=destination,
            text=text,
            parse_mode=ParseMode.HTML)

    async def menu(self, who, text, buttons):
        print(f"send menu: {who, text, buttons}")
        return await who.reply_text(text,
                                    reply_markup=self.get_keyboard(buttons),
                                    parse_mode=ParseMode.MARKDOWN)

    def get_keyboard(self, buttons):
        keyboard = []

        for start_index in range(0, len(buttons), 2):
            keyboard_line = []
            for key in buttons[start_index:start_index + 2]:
                button = InlineKeyboardButton(key, callback_data=key)
                keyboard_line.append(button)
            keyboard.append(keyboard_line)
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_who_what(update, context):
        username = (update.message or update.effective_message).chat.username
        message = (update.message or update.effective_message).text

        return username, message

    def get_destination(self, update, context):
        return {send.MESSAGE: update.effective_chat.id,
                send.MENU: (update.message or update.effective_message)}

    async def act(self, update, context):
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
        print(f"Results: '{actions_results}'")
        return {'statusCode': 200}

    TRIGGER_TO_TG = {trigger.ON_MESSAGE: filters.CHAT}

    def _really_add(self):
        for t, actions in self.actions_to_handlers.items():
            async def single_action(update, context):
                return [await a(update, context) for a in actions[:]]

            self.app.add_handler(
            MessageHandler(self.TRIGGER_TO_TG[t], single_action))

    def add(self, on, action, trigger_filter=None):
        self.actions_to_handlers[on].append(action)
