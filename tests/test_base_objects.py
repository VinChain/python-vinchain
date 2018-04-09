import unittest
from vinchainio import VinChain, exceptions
from vinchainio.instance import set_shared_vinchain_instance
from vinchainio.account import Account
from vinchainio.committee import Committee


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = VinChain(
            nobroadcast=True,
        )
        set_shared_vinchain_instance(self.bts)

    def test_Committee(self):
        with self.assertRaises(
            exceptions.AccountDoesNotExistsException
        ):
            Committee("FOObarNonExisting")

        c = Committee("init0")
        self.assertEqual(c["id"], "1.5.0")
        self.assertIsInstance(c.account, Account)

        with self.assertRaises(
            exceptions.CommitteeMemberDoesNotExistsException
        ):
            Committee("nathan")
