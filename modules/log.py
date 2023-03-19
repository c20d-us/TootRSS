"""
A simple logging wrapper class
"""


# Make this a Singleton class - will only initialize once
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Log(metaclass=Singleton):
    """
    Log class
    """

    def __init__(self, quiet: bool = False, verbose: bool = False) -> None:
        """
        The initializer
        """
        self._Q = quiet
        self._V = verbose

    def inform(self, msg: str) -> None:
        """
        Print an informational message
        """
        self._Q or print(msg)

    def crit(self, msg: str) -> None:
        """
        Print a critical message
        """
        self.inform(f"CRIT: {msg}")

    def debug(self, msg: str) -> None:
        """
        Print a debug message
        """
        self._V and self.inform(f"DEBUG: {msg}")
