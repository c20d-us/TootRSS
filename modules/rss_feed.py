"""
A wrapper class for an RSS feed
"""
import feedparser
from modules.log import Log


class Feed:
    """
    Feed class

        Parameters
    ----------
    feed_uri: str
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
        if not self._data.bozo:
            self._title = self._data.feed.title
            self._load_items()
        else:
            log.crit(f"Could not parse the feed '{feed_url}'")
            raise Exception()

    def _make_datestamp(self, date_tuple: tuple = None) -> str:
        """
        Make a 14-digit datestamp from the pubDate date tuple (ex. 20230101000000)
        """
        d = "0" * 14
        if date_tuple:
            d = f"{date_tuple[0]:04}"
            for i in range(1, 6):
                d = "".join([d, f"{date_tuple[i]:02}"])
        return d

    def _load_items(self) -> bool:
        """
        Load all items from the feed into the '_items' class attribute
        """
        if self._data:
            for entry in self._data.entries:
                item_key = "-".join(
                    [self._make_datestamp(entry.published_parsed), entry.id]
                )
                self._items[item_key] = {
                    "title": entry.title,
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
