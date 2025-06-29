import logging
import traceback
from collections import defaultdict


class OMNI:
    logger = logging.getLogger('omni.%s' % __name__)
    def __init__(self, provider):
        self.provider = provider
        self.default_action = None
        self.error_action = None
        self.logger.info("Bot created")

    def set_default_action(self, func):
        self.provider.set_default_action(func)

    def set_error_action(self, func):
        self.provider.set_error_action(func)

    def add(self, on, action, trigger_filter=None):
        self.provider.add(on, action, trigger_filter)
        self.logger.info(f"Trigger '{on}(filter={trigger_filter})' "
                         f"added with action '{action}'")

    def act(self, update, context):
        return self.provider.act(update, context)
