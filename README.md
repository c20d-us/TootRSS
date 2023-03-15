### TootRSS

 A utility that will read an RSS feed and toot new posts from the RSS feed to a Mastodon account.

 This utility has not been tested with Atom feeds, though it should be trivial to modify to accomodate Atom.

 Critical access and API keys should be encrypted with Fernet and the resulting encrypted tokens stored in `./settings/_settings.py`. You can generate a Fernet key and created encrypted tokens with the online Fernet utility located [here](https://8gwifi.org/fernet.jsp).
 
**Note:** DO NOT store your actual Fernet key in the settings file. You should supply the Fernet key by setting the environment variable `FERNET_KEY` with the appropriate Fernet key value.
