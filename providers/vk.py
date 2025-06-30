import os
import json
from collections import defaultdict

import requests

import send
import trigger

from providers.base import BaseProvider


class VK(BaseProvider):
    TYPE = "vk"
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')  # Ключ доступа группы
    VK_API_URL = "https://api.vk.com/method/messages.send"
    API_VERSION = "5.199"
    #CONFIRMATION_TOKEN = os.getenv('CONFIRMATION_TOKEN')

    def __init__(self):
        super().__init__()

        self.actions = defaultdict(
            list)  # key = trigger or tuple(trigger, filter_func=None)

    async def send(self, who, type, text, buttons=None):
        print(who, type, text)
        if type == send.MESSAGE:
            return self.message(who, text)
        elif type == send.MENU:
            return self.message(who, text, buttons)
        else:
            raise Exception(f"Unknown type {type}")

    def message(self, destination, text, buttons=None):
        params = {
            'user_id': destination,
            'message': text,
            'random_id': 0,
            'access_token': self.ACCESS_TOKEN,
            'v': self.API_VERSION,
            'dont_parse_links': 1,
        }

        if buttons:
            params['keyboard'] = json.dumps(self.get_keyboard(buttons))

        print(f"send message: {params}")

        return requests.post(self.VK_API_URL, params=params)

    def _get_button(self, text):
        return {"action": {"type": "text", "label": text}, "color": "primary"}

    def get_keyboard(self, buttons):
        return {"one_time": False, "inline": False,
                "buttons": [[self._get_button(text) for text in buttons]]}

    VK_TYPE_TO_TRIGGER = {'confirmation': trigger.TRIGGER_ON_CONFIRMATION,
                          'message_new': trigger.ON_MESSAGE}

    SELF_REPLY_MESSAGE = 'message_reply'

    def get_reply_type(self, update, context):
        reply_vk_type = json.loads(update['body'])['type']
        if reply_vk_type == self.SELF_REPLY_MESSAGE:
            return None

        reply_text = self.get_who_what(update, context)[1]
        if reply_text in self.menu_buttons:
            return trigger.ON_MENU

        return self.VK_TYPE_TO_TRIGGER[reply_vk_type]

    @staticmethod
    def get_who_what(update, context):
        data = json.loads(update['body'])

        print(data)

        message = data['object']['message']
        channel = message['from_id']
        reply_text = message['text']

        print(f"Пользователь '{channel}' написал '{reply_text}'")

        return channel, reply_text

    def get_destination(self, update, context):
        return self.get_who_what(update, context)[0]

    def response(self, actions_results):
        print(f"Results: '{actions_results}'")
        return {'statusCode': 200}

    def add(self, on, action, trigger_filter=None):
        self.actions[(on, trigger_filter)].append(action)

    async def act(self, update, context):
        reply_type = self.get_reply_type(update, context)

        if not reply_type:
            return self.response([f"We don't reply on'{reply_type}'"])

        reply_text = self.get_who_what(update, context)[1]
        ret = []
        try:
            acted = False
            for (on, trigger_filter), actions in self.actions.items():
                if (on == reply_type and (trigger_filter is None or
                        trigger_filter(reply_type, reply_text))):
                    for action in actions:
                        ret.append(await action(update, context))
                        acted = True
            if not acted:
                self.logger.warning(f"No action triggered for '{reply_type}'")
                ret.append(self._default(update, context))
        except Exception as e:
            ret.append(self._error(update, context))

        return self.response(ret)
