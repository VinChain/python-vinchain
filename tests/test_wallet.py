import unittest
import mock
from pprint import pprint
from vinchainio import VinChain
from vinchainio.account import Account
from vinchainio.amount import Amount
from vinchainio.asset import Asset
from vinchainio.instance import set_shared_vinchain_instance
from vinchainiobase.operationids import getOperationNameForId

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = VinChain(
            nobroadcast=True,
            # We want to bundle many operations into a single transaction
            bundle=True,
            # Overwrite wallet to use this list of wifs only
            wif=[wif]
        )
        self.bts.set_default_account("init0")
        set_shared_vinchain_instance(self.bts)
