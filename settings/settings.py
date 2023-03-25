"""
These settings are used unless overriden by identical variables defined in the local environment
© Copyright 2023, Chris Halstead
"""
# The AWS access key ID for AWS DynamoDB access - Fernet-encrypted
AWS_ACCESS_KEY_ID = "xxxx"
# The AWS secret access key for AWS DynamoDB access - Fernet-encrypted
AWS_ACCESS_KEY = "xxxx"
# The primary region for the DynamoDB cache DB
AWS_REGION = "us-west-2"

# The name of the DynamoDB partition key used by the feed cache
DYNAMO_DB_P_KEY_NAME = "feed"
# The name of the DynamoDB sort key used by the feed cache
DYNAMO_DB_S_KEY_NAME = "item_id"
# The name of the DynamoDB table used for the feed cache
DYNAMO_DB_TABLE_NAME = "blog-feed-cache"

# The URL of the RSS/Atom feed to watch
FEED_URL = "https://your.blog/index.xml"

# The Fernet key used to encrypt the encrypted values in this file
# DO NOT EVER STORE THE ACTUAL KEY HERE - PASS IT BY SETTING THE CORRECT VALUE AS AN ENVIRONMENT VARIABLE
FERNET_KEY = None

# The Mastodon API access token used to post statuses - Fernet-encrypted
MASTODON_ACCESS_TOKEN = "xxxx"
# The base URL of your Mastodon instance
MASTODON_BASE_URL = "https://hachyderm.io"
# The status visibility of your status posts - one of ['direct'|'private'|'unlisted'|'public']
# Use 'direct' while testing to make toots only visible to you
MASTODON_STATUS_VISIBILITY = "public"