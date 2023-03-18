#!/usr/bin/env python3
"""
The Toot RSS client - reads an RSS feed and toots out new feed items to a Mastodon account
"""
import argparse
import settings as S
from mastodon import Mastodon
from modules.encrypted_token import EncryptedToken
from modules.feed_cache import FeedCache
from modules.rss_feed import Feed

# Global objects used later
CACHE_ONLY = False
PROCESSED_ITEMS = 0
POSTED_ITEMS = 0
QUIET = False
C = F = M = None


def inform(msg: str = None) -> None:
    if not QUIET:
        print(msg)


def init() -> None:
    # Initialize the globals
    global C, F, M
    C = FeedCache(
        access_key_id=EncryptedToken(S.FERNET_KEY, S.AWS_ACCESS_KEY_ID).decrypt(),
        access_key=EncryptedToken(S.FERNET_KEY, S.AWS_ACCESS_KEY).decrypt(),
        region=S.AWS_REGION,
        table_name=S.DYNAMO_DB_TABLE,
        p_key_name=S.DYNAMO_DB_P_KEY_NAME,
        s_key_name=S.DYNAMO_DB_S_KEY_NAME,
    )
    F = Feed(S.FEED_URL)
    M = Mastodon(
        access_token=EncryptedToken(S.FERNET_KEY, S.MASTODON_ACCESS_TOKEN).decrypt(),
        api_base_url=S.MASTODON_BASE_URL,
    )


def get_args() -> None:
    # Get arguments passed into the program
    global CACHE_ONLY, QUIET
    argParser = argparse.ArgumentParser(
        prog="tootrss", description="A utility to toot rss posts to Mastodon"
    )
    argParser.add_argument(
        "-c", "--cache", action="store_true", help="build the feed cache - do not toot"
    )
    argParser.add_argument(
        "-k", "--fernet_key", default=None, help="the Fernet key used to ecrypt tokens"
    )
    argParser.add_argument(
        "-q", "--quiet", action="store_true", help="suppress progress messages"
    )
    args = argParser.parse_args()
    S.FERNET_KEY = args.fernet_key
    CACHE_ONLY = args.cache
    QUIET = args.quiet


def cache_item(feed: Feed, item_key: str) -> None:
    C.put_item(
        p_key=feed.title,
        s_key=item_key,
        link=feed.items[item_key]["link"],
        title=feed.items[item_key]["title"],
        tooted=True,
    )
    inform(f'Cached item "{item_key}" in the feed cache.')


def post_item(feed: Feed, item_key: str) -> None:
    global POSTED_ITEMS
    # Post a status for this feed item
    try:
        M.status_post(
            (
                f"I just published a new post on {feed.title}. Check it out!\n\n"
                f"\"{feed.items[item_key]['title']}\"\n"
                f"{feed.items[item_key]['link']}"
            ),
            visibility=S.MASTODON_STATUS_VISIBILITY,
        )
    except:
        print("Error!")
    finally:
        POSTED_ITEMS += 1
        inform(f"Posted item \"{feed.items[item_key]['title']}\" to Mastodon.")


def process_feed() -> None:
    global POSTED_ITEMS, PROCESSED_ITEMS
    # Get the list of post items in the feed, sorted oldest-to-newest
    for item_key in sorted(F.items):
        PROCESSED_ITEMS += 1
        # See if there is already a cache record for this item
        cache_record = C.get_item(F.title, item_key)
        if not cache_record:
            # If the item isn't in the cache, we need to cache it, or post it and cache it
            if CACHE_ONLY:
                cache_item(F, item_key)
            else:
                post_item(F, item_key)
                cache_item(F, item_key)
        if cache_record and not cache_record["tooted"]:
            post_item(F, item_key)
            cache_item(F, item_key)


if __name__ == "__main__":
    get_args()
    init()
    process_feed()
    inform(
        f"Processed {PROCESSED_ITEMS} items\nPosted {POSTED_ITEMS} items to Mastodon"
    )
