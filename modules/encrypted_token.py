"""
A module for handling Fernet-encrypted tokens
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
        self._F = None
        self._token = encrypted_token
        try:
            self._F = Fernet(fernet_key)
        except:
            log.crit(f"The supplied fernet key was invalid: {fernet_key=}")
            raise Exception()

    def decrypt(self) -> str:
        """
        Decrypt the Fernet-encrypted token.
        """
        decrypted_token = None
        try:
            decrypted_token = self._F.decrypt(self._token).decode("utf-8")
        except:
            log.crit(f"The encrypted token was invalid: {self._token=}")
            raise Exception()
        return decrypted_token
