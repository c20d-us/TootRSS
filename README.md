### TootRSS

TootRSS is utility that will read an RSS feed and toot new posts in the feed to a Mastodon account. It uses a DynamoDB-based cache to store information about feed items that have been tooted, so that only newly published posts trigger a Mastodon status update.

## Usage
```
usage: tootrss [-h] [-c] [-m] [-q] [-v] [-k FERNET_KEY]

s utility to toot rss posts to Mastodon

optional arguments:
  -h, --help            show this help message and exit
  -c, --cache           build the feed cache - do not toot
  -m, --make_table      create the feed cache table if it does not exist
  -q, --quiet           suppress all progress messages
  -v, --verbose         provide additional progress messaging
  -k FERNET_KEY, --fernet_key FERNET_KEY
                        the Fernet key used to ecrypt tokens
```

## Examples

Read the feed and toot anything new, passing the Fernet key as an argument:
```
mymac:~ jdoe$ ./tootrss -k xxxx
```
Read the feed and just populate the feed cache (no toots), passing the Fernet key as an argument. Useful when bootstrapping for an existing feed to avoid a deluge of toots:
```
mymac:~ jdoe$ ./tootrss -c --fernet_key xxxx
```
Read the feed, populate the feed cache (no toots), and create the feed cache DynamoDB table if it doesn't already exist:
```
mymac:~ jdoe$ ./tootrss -c -m --fernet_key xxxx
```
Read the feed and toot anything new, passing the Fernet key as an environment variable (grouped to prevent environment leakage of the Fernet key after execution):
```
mymac:~ jdoe$ ( export FERNET_KEY="xxxx"; ./tootrss )
```
Where `"xxxx"` in the above examples is the Fernet key used to encrypt your access tokens.

## Requirements
* TootRSS was built to run on Python 3.9+. Module requirements are listed in `./requirements/reqs.txt`.
* The `./mkvenv.sh` script will create a Python virtual environment that fulfills the module needs of the utility.
* You must have an RSS feed to query for published items
* You will need active and valid AWS access credentials for an account that can contain a DynamoDB Table. You can find instructions on how to set up an appropriate IAM user in the AWS documentation.
* TootRSS requires read and write access to a properly structured DynamoDB table.
  * If the DynamoDB table does not exist, it will be created if the `-m` or `--make_table` flag has been specified on the command line.
* You will need an active Mastodon account, and you must generate an access token that will allow the TootRSS utility to post on your behalf. A good tutorial that includes the steps to do this is [here.](https://medium.com/@martin.heinz/getting-started-with-mastodon-api-in-python-9f105309ed43)
## Configuration Settings

All configuration settings required for the utility are stored in the file `./settings/_settings.py`. All variables defined in the settings file can be overriden by defining an identical variable with an alternate value in the local environment. Variables defined in the environment take precendence.

The required configuration settings are:

```
# The AWS access key ID for AWS DynamoDB access - Fernet-encrypted
AWS_ACCESS_KEY_ID = "xxxx" <---- replace with your Fernet-encrypted access key ID

# The AWS secret access key for AWS DynamoDB access - Fernet-encrypted
AWS_ACCESS_KEY = "xxxx" <---- replace with your Fernet-encrypted access key

# The primary region for the DynamoDB cache DB
AWS_REGION = "us-west-2" <---- replace with your primary region

# The name of the DynamoDB partition key used by the feed cache
DYNAMO_DB_P_KEY_NAME = "feed" <---- no need to change this

# The name of the DynamoDB sort key used by the feed cache
DYNAMO_DB_S_KEY_NAME = "item_id" <---- no need to change this

# The name of the DynamoDB table used for the feed cache
DYNAMO_DB_TABLE = "blog-feed-cache" <---- no need to change this

# The URL of the RSS/Atom feed to watch
FEED_URL = "https://your.blog/index.xml" <---- replace with your feed URL

# The Fernet key used to encrypt the encrypted values in this file
# DO NOT EVER STORE THE ACTUAL KEY HERE
FERNET_KEY = None <---- Pass as an argument or define this in the environment

# The Mastodon API access token used to post statuses - Fernet-encrypted
MASTODON_ACCESS_TOKEN = "xxxx" <---- replace with your Fernet-encrypted Mastodon access token

# The base URL of your Mastodon instance
MASTODON_BASE_URL = "https://hachyderm.io"  <---- replace with your Mastodon instance URL

# The status visibility of your status posts - one of ['direct'|'private'|'unlisted'|'public']
# Use 'direct' while testing to make toots only visible to you
MASTODON_STATUS_VISIBILITY = "public"  <---- can leave as-is unless testing
```

**Note:** This utility has not been tested with Atom feeds, though it should be trivial to modify to accomodate them.

**Note:** Critical access and API keys must be encrypted with Fernet and the resulting encrypted tokens stored in the settings file (or provided as environment variables). You can generate a Fernet key and create encrypted tokens using that key with the online Fernet utility located [here](https://8gwifi.org/fernet.jsp).
 
**Note:** _**DO NOT**_ store your Fernet key in the settings file. You should supply the Fernet key either by passing it as an argument to the utility, or by setting the environment variable `FERNET_KEY` with the appropriate Fernet key value. With either of these methods, it's good practice to purge your shell history of the commands so that your Fernet key does not remain behind in plain text on your system.
