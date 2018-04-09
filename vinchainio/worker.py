from vinchainio.instance import shared_vinchain_instance
from .account import Account
from .exceptions import WorkerDoesNotExistsException
from .utils import formatTimeString
from .blockchainobject import BlockchainObject


class Worker(BlockchainObject):
    """ Read data about a worker in the chain

        :param str id: id of the worker
        :param vinchainio vinchain_instance: VinChain() instance to use when
            accesing a RPC

    """
    type_id = 14

    def refresh(self):
        worker = self.vinchain.rpc.get_object(self.identifier)
        if not worker:
            raise WorkerDoesNotExistsException
        worker["work_end_date"] = formatTimeString(worker["work_end_date"])
        worker["work_begin_date"] = formatTimeString(worker["work_begin_date"])
        super(Worker, self).__init__(worker, vinchain_instance=self.vinchain)
        self.cached = True

    @property
    def account(self):
        return Account(
            self["worker_account"], vinchain_instance=self.vinchain)


class Workers(list):
    """ Obtain a list of workers for an account

        :param str account_name/id: Name/id of the account (optional)
        :param vinchainio vinchain_instance: VinChain() instance to use when
            accesing a RPC
    """
    def __init__(self, account_name=None, vinchain_instance=None):
        self.vinchain = vinchain_instance or shared_vinchain_instance()
        if account_name:
            account = Account(account_name, vinchain_instance=self.vinchain)
            self.workers = self.vinchain.rpc.get_workers_by_account(
                account["id"])
        else:
            self.workers = self.vinchain.rpc.get_all_workers()

        super(Workers, self).__init__(
            [
                Worker(x, lazy=True, vinchain_instance=self.vinchain)
                for x in self.workers
            ]
        )
