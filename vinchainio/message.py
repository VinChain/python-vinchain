import re
import logging
from binascii import hexlify, unhexlify
from graphenebase.ecdsa import verify_message, sign_message
from vinchainiobase.account import PublicKey
from vinchainio.instance import shared_vinchain_instance
from vinchainio.account import Account
from .exceptions import InvalidMessageSignature
from .storage import configStorage as config

log = logging.getLogger(__name__)

MESSAGE_SPLIT = (
    "-----BEGIN VINCHAIN SIGNED MESSAGE-----",
    "-----BEGIN META-----",
    "-----BEGIN SIGNATURE-----",
    "-----END VINCHAIN SIGNED MESSAGE-----"
)

SIGNED_MESSAGE_META = """{message}
account={meta[account]}
memokey={meta[memokey]}
block={meta[block]}
timestamp={meta[timestamp]}"""

SIGNED_MESSAGE_ENCAPSULATED = """
{MESSAGE_SPLIT[0]}
{message}
{MESSAGE_SPLIT[1]}
account={meta[account]}
memokey={meta[memokey]}
block={meta[block]}
timestamp={meta[timestamp]}
{MESSAGE_SPLIT[2]}
{signature}
{MESSAGE_SPLIT[3]}
"""


class Message():

    def __init__(self, message, vinchain_instance=None):
        self.vinchain = vinchain_instance or shared_vinchain_instance()
        self.message = message
        self.meta = {}

    def sign(self, account=None, **kwargs):
        """ Sign a message with an account's memo key

            :param str account: (optional) the account that owns the bet
                (defaults to ``default_account``)

            :returns: the signed message encapsulated in a known format
        """
        if not account:
            if "default_account" in config:
                account = config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        # Data for message
        account = Account(account, vinchain_instance=self.vinchain)
        info = self.vinchain.info()
        self.meta = dict(
            timestamp=info["time"],
            block=info["head_block_number"],
            memokey=account["options"]["memo_key"],
            account=account["name"])

        # wif key
        wif = self.vinchain.wallet.getPrivateKeyForPublicKey(
            account["options"]["memo_key"]
        )

        # signature
        message = self.message.strip()
        signature = hexlify(sign_message(
            SIGNED_MESSAGE_META.format(
                meta=self.meta, **locals()
            ),
            wif
        )).decode("ascii")

        message = self.message
        return SIGNED_MESSAGE_ENCAPSULATED.format(
            MESSAGE_SPLIT=MESSAGE_SPLIT,
            meta=self.meta,
            **locals()
        )

    def verify(self, **kwargs):
        """ Verify a message with an account's memo key

            :param str account: (optional) the account that owns the bet
                (defaults to ``default_account``)

            :returns: True if the message is verified successfully
            :raises InvalidMessageSignature if the signature is not ok
        """
        # Split message into its parts
        parts = re.split("|".join(MESSAGE_SPLIT), self.message)
        parts = [x for x in parts if x.strip()]

        assert len(parts) > 2, "Incorrect number of message parts"

        message = parts[0].strip()
        signature = parts[2].strip()
        # Parse the meta data
        self.meta = dict(re.findall(r'(\S+)=(.*)', parts[1]))

        # Ensure we have all the data in meta
        assert "account" in self.meta
        assert "memokey" in self.meta
        assert "block" in self.meta
        assert "timestamp" in self.meta

        self.meta['message'] = message

        # Load account from blockchain
        account = Account(
            self.meta.get("account"),
            vinchain_instance=self.vinchain
        )

        # Test if memo key is the same as on the blockchain
        if not account["options"]["memo_key"] == self.meta["memokey"]:
            log.error(
                "Memo Key of account {} on the Blockchain".format(
                    account["name"]) +
                "differs from memo key in the message: {} != {}".format(
                    account["options"]["memo_key"], self.meta["memokey"]
                )
            )

            raise InvalidMessageSignature

        # Reformat message
        message = SIGNED_MESSAGE_META.format(meta=self.meta, **locals())

        # Verify Signature
        pubkey = verify_message(message, unhexlify(signature))

        # Verify pubky
        pk = PublicKey(hexlify(pubkey).decode("ascii"))
        if format(pk, self.vinchain.prefix) != self.meta["memokey"]:
            raise InvalidMessageSignature

        return True
