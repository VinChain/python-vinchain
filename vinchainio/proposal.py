from .instance import shared_vinchain_instance
from .account import Account
from .exceptions import ProposalDoesNotExistException
from .blockchainobject import BlockchainObject
import logging
log = logging.getLogger(__name__)


class Proposal(BlockchainObject):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param vinchainio vinchain_instance: VinChain() instance to use when accesing a RPC

    """
    type_id = 10

    def refresh(self):
        proposal = self.vinchain.rpc.get_objects([self.identifier])
        if not any(proposal):
            raise ProposalDoesNotExistException
        super(Proposal, self).__init__(proposal[0], vinchain_instance=self.vinchain)

    @property
    def proposed_operations(self):
        yield from self["proposed_transaction"]["operations"]


class Proposals(list):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param vinchainio vinchain_instance: VinChain() instance to use when accesing a RPC
    """
    def __init__(self, account, vinchain_instance=None):
        self.vinchain = vinchain_instance or shared_vinchain_instance()

        account = Account(account, vinchain_instance=self.vinchain)
        proposals = self.vinchain.rpc.get_proposed_transactions(account["id"])

        super(Proposals, self).__init__(
            [
                Proposal(x, vinchain_instance=self.vinchain)
                for x in proposals
            ]
        )
