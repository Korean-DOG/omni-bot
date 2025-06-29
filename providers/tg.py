import os
import json

from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram import Message
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

    async def send(self, who, type, text):
        print(who, type, text)
        if type == send.MESSAGE:
            return await self.message(who, text)
        else:
            raise Exception(f"Unknown type {type}")

    async def message(self, destination, text):
        text = text.encode('utf16',
                           errors='surrogatepass').decode('utf16')

        return await self.app.bot.send_message(
            chat_id=destination,
            text=text,
            parse_mode=ParseMode.HTML)


    @staticmethod
    def get_who_what(update, context):
        username = (update.message or update.effective_message).chat.username
        message = (update.message or update.effective_message).text

        return username, message

    def get_destination(self, update, context):
        return update.effective_chat.id

    async def act(self, update, context):
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

    def add(self, on, action, trigger_filter=None):
        self.app.add_handler(
            MessageHandler(
                self.TRIGGER_TO_TG[trigger.ON_MESSAGE], action))
