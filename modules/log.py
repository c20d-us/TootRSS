"""
A logging wrapper class
"""

class Log:
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

    def warn(self, msg: str) -> None:
        """
        Print a warning message
        """
        self._V and self.inform(f"WARN: {msg}")