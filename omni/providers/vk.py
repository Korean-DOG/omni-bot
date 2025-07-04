"""Provides a concrete implementation of the BaseProvider for VK chat bots. 
Handles platform-specific interactions including:
- Event processing from VK Callback API
- Message delivery via VK methods
- Trigger mapping for VK event types
"""

import os
import json
from collections import defaultdict

import requests

from omni import send, trigger

from omni.providers.base import BaseProvider


class VK(BaseProvider):
    """Provider for VK chat bot.

    Attributes:
        TYPE (str): Type of bot.
        ACCESS_TOKEN (str): The group's access key.
        VK_API_URL (str): Api url.
        API_VERSION (str): Api version.
        VK_TYPE_TO_TRIGGER (dict): Platform-specific types of triggers.
        SELF_REPLY_MESSAGE (str): The template message sent by the bot when responding to its own actions.
    """
    TYPE = "vk"
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')  # Ключ доступа группы
    VK_API_URL = "https://api.vk.com/method/messages.send"
    API_VERSION = "5.199"
    #CONFIRMATION_TOKEN = os.getenv('CONFIRMATION_TOKEN')

    def __init__(self):
        """Class constructor."""
        super().__init__()

        self.actions = defaultdict(
            list)  # key = trigger or tuple(trigger, filter_func=None)

    async def send(self, who, type, text, buttons=None):
        """Send different types of messages.

        Args:
            who (dict): Dictionary with message destinations.
            type (str): Type of message.
            text (str): Message text.
            buttons (set, optional): Menu buttons. Defaults to None.

        Raises:
            Exception: If type is not in send.py.

        Returns:
            requests.Response: Response of chat bot server.
        """
        print(who, type, text)
        if type == send.MESSAGE:
            return self.message(who, text)
        elif type == send.MENU:
            return self.message(who, text, buttons)
        else:
            raise Exception(f"Unknown type {type}")

    def message(self, destination, text, buttons=None):
        """Send text message with optional menu buttons.

        Args:
            destination (telegram.Message): The message included in the update.
            text (str): Message to sent.
            buttons (set(str)): Menu buttons. Defaults to None.

        Returns:
            requests.Response: Response of chat bot server.
        """
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
        """Generates a VK API-compatible keyboard layout for interactive message replies. 

        Args:
            buttons (set(str)): Menu buttons.

        Returns:
            dict: Dictionary with menu config and buttons.
        """
        lines = []
        for start_index in range(0, len(buttons), self.keyboard_lines - 1):
            lines.append(buttons[start_index:start_index + self.keyboard_lines - 1])

        return {"one_time": False, "inline": False, "buttons": lines}

    VK_TYPE_TO_TRIGGER = {'confirmation': trigger.TRIGGER_ON_CONFIRMATION,
                          'message_new': trigger.ON_MESSAGE}

    SELF_REPLY_MESSAGE = 'message_reply'

    def get_reply_type(self, update, context):
        """Defines the type of trigger.

        Args:
            update (dict): Request info
            context: Chat context.

        Returns:
            (str | None): Type of trigger or None when bot replies to itself.
        """
        reply_vk_type = json.loads(update['body'])['type']
        if reply_vk_type == self.SELF_REPLY_MESSAGE:
            return None

        reply_text = self.get_who_what(update, context)[1]
        if reply_text in self.menu_buttons:
            return trigger.ON_MENU

        return self.VK_TYPE_TO_TRIGGER[reply_vk_type]

    @staticmethod
    def get_who_what(update, context):
        """Get user ID and message text.

        Args:
            update (dict): Request info.
            context: Chat context.

        Returns:
            (int, str): User ID and message text.
        """
        data = json.loads(update['body'])

        print(data)

        message = data['object']['message']
        channel = message['from_id']
        reply_text = message['text']

        print(f"Пользователь '{channel}' написал '{reply_text}'")

        return channel, reply_text

    def get_destination(self, update, context):
        """Get user ID.

        Args:
            update (dict): Request info.
            context: Chat context.

        Returns:
            int: User ID.
        """
        return self.get_who_what(update, context)[0]

    def response(self, actions_results):
        """Finalizes request processing by logging results and returning an HTTP status.

        Args:
            actions_results (Any): Results of response.

        Returns:
            dict: Status code of response.
        """
        print(f"Results: '{actions_results}'")
        return {'statusCode': 200}

    def add(self, on, action, trigger_filter=None):
        """Add action on specific trigger.

        Args:
            on (str): Trigger type.
            action (Callable): Action.
            trigger_filter (Callable): Function-filter for trigger. Defaults to None.
        """
        self.actions[(on, trigger_filter)].append(action)

    async def act(self, update, context):
        """Performs actions added by the add method.

        Args:
            update (dict): Request info.
            context: Chat context.

        Returns:
            dict: Status code.
        """
        reply_type = self.get_reply_type(update, context)

        if not reply_type:
            return self.response([f"We don't reply on such messages "
                                  f"'{reply_type}'. "
                                  f"skip work update'{update}'"])

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
