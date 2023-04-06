"""
A wrapper class for an RSS feed
© Copyright 2023, Chris Halstead
"""
import feedparser
from modules.log import Log


class Feed:
    """
    Feed class

    Parameters
    ----------
    feed_url: str
        The URL of the feed to retrieve and parse
    """

    log = None

    def __init__(self, feed_url: str = None) -> None:
        """
        The initializer
        """
        global log
        log = Log()
        self._items = {}
        self._title = None
        self._data = feedparser.parse(feed_url)
        if self._data.bozo:
            log.crit(f"Could not parse the feed '{feed_url}'")
            raise Exception()
        else:
            self._title = self._data.feed.title
            self._load_items()

    def _load_items(self) -> bool:
        """
        Load all items from the feed into the '_items' class attribute
        """
        if self._data:
            for entry in self._data.entries:
                self._items[entry.id] = {
                    "link": entry.link,
                    "tooted": False,
                }

    @property
    def title(self) -> str:
        # Feed title getter
        return self._title

    @property
    def items(self) -> dict:
        # Feed items dict getter
        return self._items