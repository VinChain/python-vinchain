from vinchainio.instance import shared_vinchain_instance
import random
from vinchainiobase import memo as BtsMemo
from vinchainiobase.account import PrivateKey, PublicKey
from .account import Account
from .exceptions import MissingKeyError, KeyNotFound


class Memo(object):
    """ Deals with Memos that are attached to a transfer

        :param vinchainio.account.Account from_account: Account that has sent the memo
        :param vinchainio.account.Account to_account: Account that has received the memo
        :param vinchainio.vinchain.VinChain vinchain_instance: VinChain instance

        A memo is encrypted with a shared secret derived from a private key of
        the sender and a public key of the receiver. Due to the underlying
        mathematics, the same shared secret can be derived by the private key
        of the receiver and the public key of the sender. The encrypted message
        is perturbed by a nonce that is part of the transmitted message.

        .. code-block:: python

            from vinchainio.memo import Memo
            m = Memo("vinchainio", "wallet.xeroc")
            m.vinchainio.wallet.unlock("secret")
            enc = (m.encrypt("foobar"))
            print(enc)
            >> {'nonce': '17329630356955254641', 'message': '8563e2bb2976e0217806d642901a2855'}
            print(m.decrypt(enc))
            >> foobar

        To decrypt a memo, simply use

        .. code-block:: python

            from vinchainio.memo import Memo
            m = Memo()
            m.vinchainio.wallet.unlock("secret")
            print(memo.decrypt(op_data["memo"]))

        if ``op_data`` being the payload of a transfer operation.

    """
    def __init__(
        self,
        from_account=None,
        to_account=None,
        vinchain_instance=None
    ):

        self.vinchain = vinchain_instance or shared_vinchain_instance()

        if to_account:
            self.to_account = Account(to_account, vinchain_instance=self.vinchain)
        if from_account:
            self.from_account = Account(from_account, vinchain_instance=self.vinchain)

    def unlock_wallet(self, *args, **kwargs):
        """ Unlock the library internal wallet
        """
        self.vinchain.wallet.unlock(*args, **kwargs)
        return self

    def encrypt(self, memo):
        """ Encrypt a memo

            :param str memo: clear text memo message
            :returns: encrypted memo
            :rtype: str
        """
        if not memo:
            return None

        nonce = str(random.getrandbits(64))
        memo_wif = self.vinchain.wallet.getPrivateKeyForPublicKey(
            self.from_account["options"]["memo_key"]
        )
        if not memo_wif:
            raise MissingKeyError("Memo key for %s missing!" % self.from_account["name"])

        enc = BtsMemo.encode_memo(
            PrivateKey(memo_wif),
            PublicKey(
                self.to_account["options"]["memo_key"],
                prefix=self.vinchain.prefix
            ),
            nonce,
            memo
        )

        return {
            "message": enc,
            "nonce": nonce,
            "from": self.from_account["options"]["memo_key"],
            "to": self.to_account["options"]["memo_key"]
        }

    def decrypt(self, memo):
        """ Decrypt a memo

            :param str memo: encrypted memo message
            :returns: encrypted memo
            :rtype: str
        """
        if not memo:
            return None

        # We first try to decode assuming we received the memo
        try:
            memo_wif = self.vinchain.wallet.getPrivateKeyForPublicKey(
                memo["to"]
            )
            pubkey = memo["from"]
        except KeyNotFound:
            try:
                # if that failed, we assume that we have sent the memo
                memo_wif = self.vinchain.wallet.getPrivateKeyForPublicKey(
                    memo["from"]
                )
                pubkey = memo["to"]
            except KeyNotFound:
                # if all fails, raise exception
                raise MissingKeyError(
                    "Non of the required memo keys are installed!"
                    "Need any of {}".format(
                    [memo["to"], memo["from"]]))

        return BtsMemo.decode_memo(
            PrivateKey(memo_wif),
            PublicKey(pubkey, prefix=self.vinchain.prefix),
            memo.get("nonce"),
            memo.get("message")
        )
