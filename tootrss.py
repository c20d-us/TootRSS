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
C = None
F = None
M = None

def get_args() -> None:
    # Get arguments passed into the program
    argParser = argparse.ArgumentParser(
        prog="tootrss",
        description="A utility to toot rss posts to Mastodon"
    )
    argParser.add_argument("--fernet_key",type=str)
    args = argParser.parse_args()
    if args.fernet_key:
        S.FERNET_KEY = args.fernet_key

def init() -> None:
    # Initialize the globals
    global C, F, M
    try:
        C = FeedCache(
            access_key_id=EncryptedToken(S.FERNET_KEY, S.AWS_ACCESS_KEY_ID).decrypt(),
            access_key=EncryptedToken(S.FERNET_KEY, S.AWS_ACCESS_KEY).decrypt(),
            region=S.AWS_REGION,
            table_name=S.DYNAMO_DB_TABLE,
            p_key_name=S.DYNAMO_DB_P_KEY_NAME,
            s_key_name=S.DYNAMO_DB_S_KEY_NAME
        )
        F = Feed(S.FEED_URL)
        M = Mastodon(
            access_token = EncryptedToken(S.FERNET_KEY, S.MASTODON_ACCESS_TOKEN).decrypt(),
            api_base_url=S.MASTODON_BASE_URL
        )
    except Exception as ex:
        print(ex)

def status_post(feed_title: str, item_title: str, link: str) -> None:
    # Post a status for this feed item to Mastodon
    post_message = (
        f"I just published a new post on {feed_title}. Check it out!\n\n"
        f"\"{item_title}\"\n"
        f"{link}"
    )
    M.status_post(
        post_message,
        visibility=S.MASTODON_STATUS_VISIBILITY
    )

def post_and_put(feed: Feed, item_key: str) -> None:
    # Post a status for this feed item, then put it in the feed cache
    status_post(feed.title, feed.items[item_key]['title'], feed.items[item_key]['link'])
    C.put_item(
        p_key=feed.title,
        s_key=item_key,
        link=feed.items[item_key]['link'],
        title=feed.items[item_key]['title'],
        tooted=True
    )

def process_feed() -> None:
    # Get the list of post items in the feed, sorted oldest-to-newest
    for item_key in sorted(F.items):
        # See if there is already a cache record for this item
        cache_record = C.get_item(F.title, item_key)
        if not cache_record:
            # If there's no cache item, post the toot about it and put it in the cache
            post_and_put(F, item_key)
        if cache_record and not cache_record['tooted']:
            # If there is a cache item, but it hasn't been tooted yet, post and cache
            post_and_put(F, item_key)

if __name__ == "__main__":
    get_args()
    init()
    process_feed()