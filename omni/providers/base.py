"""This module defines the base class BaseProvider, serving as the foundation for all bot platform providers. 
It establishes the core interface and shared functionality for:
- Message handling
- Error management
- Action routing
- Menu system integration
"""

import traceback


class BaseProvider:
    """Base class for all providers.
    
    Attributes:
        logger (Logger): Logger object.
        error_action (Callable): Action for errors.
        default_action (Callable): Default bot action.
        menu_buttons (Set[str]): Inline menu buttons.
    """
    DEFAULT_KEYBOARD_LINES = 3

    def __init__(self):
        """Class constructor."""
        print(f"Initialized '{self.__module__}' Provider")
        self.error_action = None
        self.default_action = None
        self.menu_buttons = set()  # strings
        self.keyboard_lines = None

    def register_menu_buttons(self, buttons, lines=None):
        """Method for registration inline buttons for menu.

        Args:
            buttons (set(str)): menu buttons.
        """
        self.menu_buttons.update(buttons)
        self.keyboard_lines = lines or self.DEFAULT_KEYBOARD_LINES

    def _error(self, update, context):
        print("Error triggered. Exception: {}".
                              format(traceback.format_exc()))

        if self.error_action is not None:
            self.error_action(update, context)

    def _default(self, update, context):
        print("Default action triggered.")
        if self.default_action is not None:
            self.default_action(update, context)

    def set_default_action(self, func):
        """Setter for default provider action.

        Args:
            func (Callable): Action.
        """
        self.default_action = func

    def set_error_action(self, func):
        """Setter for error provider action.

        Args:
            func (Callable): Action.
        """
        self.error_action = func
