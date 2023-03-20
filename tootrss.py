#!/usr/bin/env python3
"""
The TootRSS client - reads an RSS feed and toots new feed items to a Mastodon account
"""
import argparse
import settings as S
from mastodon import Mastodon
from modules.encrypted_token import EncryptedToken
from modules.feed_cache import FeedCache
from modules.log import Log
from modules.rss_feed import Feed

# Global variables used later
C = F = M = log = None
CACHE_ONLY = QUIET = VERBOSE = False
CACHED_ITEMS = POSTED_ITEMS = PROCESSED_ITEMS = 0


def get_args() -> None:
    # Get arguments passed into the program
    global CACHE_ONLY, QUIET, VERBOSE
    argParser = argparse.ArgumentParser(
        prog="tootrss", description="s utility to toot rss posts to Mastodon"
    )
    argParser.add_argument(
        "-c",
        "--cache", action="store_true", help="build the feed cache - do not toot"
    )
    argParser.add_argument(
        "-q",
        "--quiet", action="store_true", help="suppress all progress messages"
    )
    argParser.add_argument(
        "-v",
        "--verbose", action="store_true", help="provide additional progress messaging",
    )
    argParser.add_argument(
        "-k",
        "--fernet_key", default=None, help="the Fernet key used to ecrypt tokens"
    )
    args = argParser.parse_args()
    S.FERNET_KEY = args.fernet_key
    CACHE_ONLY = args.cache
    QUIET = args.quiet
    VERBOSE = args.verbose


def init() -> None:
    # Initialize the globals
    global C, F, M
    try:
        aws_access_key = EncryptedToken(S.FERNET_KEY, S.AWS_ACCESS_KEY).decrypt()
        aws_access_key_id = EncryptedToken(S.FERNET_KEY, S.AWS_ACCESS_KEY_ID).decrypt()
        mastodon_access_token = EncryptedToken(S.FERNET_KEY, S.MASTODON_ACCESS_TOKEN).decrypt()
        F = Feed(S.FEED_URL)
        C = FeedCache(
            access_key_id=aws_access_key_id,
            access_key=aws_access_key,
            region=S.AWS_REGION,
            table_name=S.DYNAMO_DB_TABLE,
            p_key_name=S.DYNAMO_DB_P_KEY_NAME,
            s_key_name=S.DYNAMO_DB_S_KEY_NAME,
        )
        M = Mastodon(
            access_token=mastodon_access_token,
            api_base_url=S.MASTODON_BASE_URL,
        )
    except:
        log.crit("Initialization of global variables failed.")


def cache_item(feed: Feed, item_key: str) -> None:
    # Put an item into the FeedCache
    global CACHED_ITEMS
    try:
        C.put_item(
            p_key=feed.title,
            s_key=item_key,
            link=feed.items[item_key]["link"],
            title=feed.items[item_key]["title"],
            tooted=True,
        )
        CACHED_ITEMS += 1
        log.inform(f'Cached item "{item_key}" in the feed cache.')
    except:
        log.crit(f"Caching the item {item_key} into the feed cache failed.")
        raise Exception()


def post_item(feed: Feed, item_key: str) -> None:
    # Post a status for this feed item
    global POSTED_ITEMS
    try:
        M.status_post(
            (
                f"I just published a new post on {feed.title}. Check it out!\n\n"
                f"\"{feed.items[item_key]['title']}\"\n"
                f"{feed.items[item_key]['link']}"
            ),
            visibility=S.MASTODON_STATUS_VISIBILITY,
        )
        POSTED_ITEMS += 1
        log.inform(f"Posted item \"{feed.items[item_key]['title']}\" to Mastodon.")
    except:
        log.crit(f"Posting the item {item_key} to Mastondon failed.")
        raise Exception()

def process_feed() -> None:
    # Get the list of post items in the feed, sorted oldest-to-newest
    global PROCESSED_ITEMS
    for item_key in sorted(F.items):
        log.debug(f"Processing item {item_key}")
        try:
            # Try to get a cache record for this item
            cache_record = C.get_item(F.title, item_key)
            # If the item has not been cached and/or tooted already, we need to decide what to do with it
            if not cache_record or not cache_record["tooted"]:
                # Toot the item unless we're just caching
                CACHE_ONLY or post_item(F, item_key)
                # Cache the item
                cache_item(F, item_key)
            else:
                log.debug(f"The item was already in the cache: {item_key}")
            PROCESSED_ITEMS += 1
        except:
            log.crit("Processing of feed items encountered a critical error")
            raise Exception()


if __name__ == "__main__":
    get_args()
    log = Log(quiet=QUIET, verbose=VERBOSE)
    try:
        init()
        process_feed()
        log.inform(
            f"Processed {PROCESSED_ITEMS} items\n"
            f"Posted {POSTED_ITEMS} items to Mastodon\n"
            f"Cached {CACHED_ITEMS} items in the feed cache"
        )
    except:
        log.crit("TootRSS encountered a fatal exception - exiting")
