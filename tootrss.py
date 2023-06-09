#!/usr/bin/env python3
"""
The TootRSS client - reads an RSS feed and toots new feed items to a Mastodon account
© Copyright 2023, Chris Halstead
"""
import argparse
import pwinput
import settings as S
from mastodon import Mastodon
from modules.encrypted_token import EncryptedToken
from modules.feed_cache import FeedCache
from modules.log import Log
from modules.rss_feed import Feed

# Global variables
CACHE = FEED = MASTODON = log = None
ASK_KEY = CACHE_ONLY = MAKE_TABLE = QUIET = VERBOSE = False
CACHED_ENTRIES = POSTED_ENTRIES = PROCESSED_ENTRIES = 0


def getArgParser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="tootrss",
        description="A utility to toot rss posts to Mastodon"
    )
    ap.add_argument(
        "-a",
        "--ask_key",
        action="store_true",
        help="ask user to input the Fernet key"
    )
    ap.add_argument(
        "-c",
        "--cache",
        action="store_true",
        help="just build the feed cache, do not toot"
    )
    ap.add_argument(
        "-k",
        "--fernet_key",
        default=None,
        help="the Fernet key used to ecrypt tokens"
    )
    ap.add_argument(
        "-m",
        "--make_table",
        action="store_true",
        help="create the feed cache table if it does not exist"
    )
    ap.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress all progress messages"
    )
    ap.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="provide additional progress messages"
    )
    return ap


def get_args() -> None:
    # Get arguments passed into the program
    global ASK_KEY, CACHE_ONLY, MAKE_TABLE, QUIET, VERBOSE
    args = getArgParser().parse_args()
    S.FERNET_KEY = args.fernet_key or S.FERNET_KEY
    ASK_KEY = args.ask_key
    CACHE_ONLY = args.cache
    MAKE_TABLE = args.make_table
    QUIET = args.quiet
    VERBOSE = args.verbose


def get_key() -> None:
    global FERNET_KEY
    if ASK_KEY:
        key = pwinput.pwinput(prompt="Fernet key: ")
        if key:
            S.FERNET_KEY = key


def init() -> None:
    # Initialize the globals
    global CACHE, FEED, MASTODON
    try:
        CACHE = FeedCache(
            settings=S,
            access_key_id=EncryptedToken(S.FERNET_KEY, S.AWS_ACCESS_KEY_ID).decrypt(),
            access_key=EncryptedToken(S.FERNET_KEY, S.AWS_ACCESS_KEY).decrypt(),
            make_table=MAKE_TABLE
        )
        FEED = Feed(S.FEED_URL)
        MASTODON = Mastodon(
            access_token=EncryptedToken(S.FERNET_KEY, S.MASTODON_ACCESS_TOKEN).decrypt(),
            api_base_url=S.MASTODON_BASE_URL
        )
    except:
        log.crit("Initialization of global variables failed.")
        raise Exception()


def cache_entry(feed: Feed, entry_key: str) -> None:
    # Put an entry into the FeedCache
    global CACHED_ENTRIES
    try:
        CACHE.put_item(
            p_key=feed.id,
            s_key=entry_key,
            link=feed.entries[entry_key]["link"],
            tooted=True
        )
        CACHED_ENTRIES += 1
        log.inform(f"Cached entry '{entry_key}' in the feed cache.")
    except:
        log.crit(f"Caching the entry '{entry_key}' into the feed cache failed.")
        raise Exception()


def post_entry(feed: Feed, entry_key: str) -> None:
    # Post a status for this feed item
    global POSTED_ENTRIES
    post_text = f"☕ I just published a new post on {feed.title}. Check it out!\n\n"
    post_text += f"\"{feed.entries[entry_key]['title']}\"\n"
    if feed.entries[entry_key]['summary']:
        post_text += f"{feed.entries[entry_key]['summary']}\n\n"
    post_text += f"{feed.entries[entry_key]['link']}"
    try:
        MASTODON.status_post(
            post_text,
            visibility=S.MASTODON_STATUS_VISIBILITY,
        )
        POSTED_ENTRIES += 1
        log.inform(f"Posted entry '{feed.entries[entry_key]['title']}' to Mastodon.")
    except Exception as ex:
        log.crit(f"The status_post call to Mastodon encountered an exception: '{ex}'")
        log.crit(f"Posting the entry '{entry_key}' to Mastondon failed.")
        raise Exception()


def process_feed() -> None:
    # Get the list of post items in the feed, sorted oldest-to-newest
    global PROCESSED_ENTRIES
    for entry_key in sorted(FEED.entries):
        log.debug(f"Processing item '{entry_key}'")
        try:
            # Try to get a cache record for this item
            cache_record = CACHE.get_item(FEED.id, entry_key)
            # If the item has not been cached and/or tooted already, we need to decide what to do with it
            if not cache_record or not cache_record["tooted"]:
                # Toot the item unless we're just cacheing
                CACHE_ONLY or post_entry(FEED, entry_key)
                # Cache the item
                cache_entry(FEED, entry_key)
            else:
                log.debug(f"The item was already in the cache: '{entry_key}'")
            PROCESSED_ENTRIES += 1
        except:
            log.crit("Processing of feed items encountered a critical error")
            raise Exception()


if __name__ == "__main__":
    get_args()
    get_key()
    log = Log(quiet=QUIET, verbose=VERBOSE)
    try:
        init()
        process_feed()
        log.inform(
            f"Processed {PROCESSED_ENTRIES} items\n"
            f"Posted {POSTED_ENTRIES} items to Mastodon\n"
            f"Cached {CACHED_ENTRIES} items in the feed cache"
        )
    except:
        log.crit("TootRSS encountered a fatal exception - exiting")