from vinchainio.instance import shared_vinchain_instance
from .account import Account
from .exceptions import WitnessDoesNotExistsException
from .blockchainobject import BlockchainObject


class Witness(BlockchainObject):
    """ Read data about a witness in the chain

        :param str account_name: Name of the witness
        :param vinchainio vinchain_instance: VinChain() instance to use when
               accesing a RPC

    """
    type_ids = [6, 2]

    def refresh(self):
        if self.test_valid_objectid(self.identifier):
            _, i, _ = self.identifier.split(".")
            if int(i) == 6:
                witness = self.vinchain.rpc.get_object(self.identifier)
            else:
                witness = self.vinchain.rpc.get_witness_by_account(
                    self.identifier)
        else:
            account = Account(
                self.identifier, vinchain_instance=self.vinchain)
            witness = self.vinchain.rpc.get_witness_by_account(account["id"])
        if not witness:
            raise WitnessDoesNotExistsException
        super(Witness, self).__init__(witness, vinchain_instance=self.vinchain)

    @property
    def account(self):
        return Account(self["witness_account"], vinchain_instance=self.vinchain)


class Witnesses(list):
    """ Obtain a list of **active** witnesses and the current schedule

        :param vinchainio vinchain_instance: VinChain() instance to use when
            accesing a RPC
    """
    def __init__(self, vinchain_instance=None):
        self.vinchain = vinchain_instance or shared_vinchain_instance()
        self.schedule = self.vinchain.rpc.get_object(
            "2.12.0").get("current_shuffled_witnesses", [])

        super(Witnesses, self).__init__(
            [
                Witness(x, lazy=True, vinchain_instance=self.vinchain)
                for x in self.schedule
            ]
        )
