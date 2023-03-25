"""
A module for handling Fernet-encrypted tokens
© Copyright 2023, Chris Halstead
"""
from cryptography.fernet import Fernet
from modules.log import Log


class EncryptedToken:
    """
    A class to manage tokens encrypted with Fernet

    Parameters
    ----------
    fenet_key: str
        The Fernet key used to encrypt the token
    encrypted_toked: str
        The valid Fernet-encrypted token that this instance will decrypt
    """

    log = None

    def __init__(self, fernet_key: str, encrypted_token: str) -> None:
        """
        The initializer
        """
        global log
        log = Log()
        self._T = encrypted_token
        try:
            self._F = Fernet(fernet_key)
        except:
            log.crit(f"The supplied fernet key was invalid: {fernet_key=}")
            raise Exception()

    def decrypt(self) -> str:
        """
        Decrypt the Fernet-encrypted token.
        """
        try:
            return self._F.decrypt(self._T).decode("utf-8")
        except:
            log.crit(f"The encrypted token was invalid: {self._T=}")
            raise Exception()