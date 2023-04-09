"""
A wrapper class for an RSS feed
© Copyright 2023, Chris Halstead
"""
import feedparser
import re
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
        self._id = None
        self._entries = {}
        self._data = feedparser.parse(feed_url)
        self._title = None
        self._type = "unknown"
        if self._data.bozo:
            log.crit(f"Could not parse the feed '{feed_url}'")
            raise Exception()
        else:
            try:
                self._set_type()
                self._set_id()
                self._set_title()
                self._load_entries()
            except:
                log.crit(f"Unable to load the feed '{feed_url}'")
                raise Exception()

    def _set_id(self) -> None:
        if re.match("atom", self._type):
            # if this is an Atom feed, it should have an "id" attribute
            if "id" in self._data.feed:
                self._id = self._data.feed.id
        else:
            # this is not an Atom feed or it didn't have an "id" attribute
            if "href" in self._data:
                self._id = self._data.href
        if not self._id:
            log.crit("Could not set an id for the feed")
            raise Exception()

    def _set_title(self) -> None:
        if "title" in self._data.feed:
            self._title = self._data.feed.title
        if not self._title:
            log.crit("Could not set the title for the feed")
            raise Exception()

    def _set_type(self) -> None:
        if "version" in self._data:
            self._type = re.sub(r'[0-9]+', '', self._data.version)
        if not self._type:
            log.crit("Could not set the type for the feed")
            raise Exception()

    def _load_entries(self) -> None:
        """
        Load all items from the feed into the '_items' class attribute
        """
        if self._data:
            for entry in self._data.entries:
                if self._type == "atom":
                    summary = entry.summary or None
                else:
                    summary = None
                self._entries[entry.id] = {
                    "link": entry.link,
                    "summary": summary,
                    "title": entry.title,
                    "tooted": False,
                }

    @property
    def id(self) -> str:
        # Feed id getter
        return self._id

    @property
    def entries(self) -> dict:
        # Feed items dict getter
        return self._entries

    @property
    def title(self) -> str:
        # Feed title getter
        return self._title