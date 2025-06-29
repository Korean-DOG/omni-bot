import logging
import traceback


class BaseProvider:
    logger = logging.getLogger('omni.%s' % __name__)
    def __init__(self):
        print(f"Initialized '{self.__module__}' Provider")
        self.error_action = None
        self.default_action = None

    def _error(self, update, context):
        self.logger.error("Error triggered. Exception: {}".
                              format(traceback.format_exc()))

        if self.error_action is not None:
            self.error_action(update, context)

    def _default(self, update, context):
        self.logger.warning("Default action triggered.")
        if self.default_action is not None:
            self.default_action(update, context)

    def set_default_action(self, func):
        self.default_action = func

    def set_error_action(self, func):
        self.error_action = func




