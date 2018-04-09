import logging
from events import Events
from vinchainioapi.websocket import VinChainWebsocket
from vinchainio.instance import shared_vinchain_instance
from vinchainio.market import Market
from vinchainio.price import Order, FilledOrder, UpdateCallOrder
from vinchainio.account import AccountUpdate
log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)


class Notify(Events):
    """ Notifications on Blockchain events.

        :param list accounts: Account names/ids to be notified about when changing
        :param list markets: Instances of :class:`vinchainio.market.Market` that identify markets to be monitored
        :param list objects: Object ids to be notified about when changed
        :param fnt on_tx: Callback that will be called for each transaction received
        :param fnt on_block: Callback that will be called for each block received
        :param fnt on_account: Callback that will be called for changes of the listed accounts
        :param fnt on_market: Callback that will be called for changes of the listed markets
        :param vinchainio.vinchain.VinChain vinchain_instance: VinChain instance

        **Example**

        .. code-block:: python

            from pprint import pprint
            from vinchainio.notify import Notify
            from vinchainio.market import Market

            notify = Notify(
                markets=["TEST:GOLD"],
                accounts=["xeroc"],
                on_market=print,
                on_account=print,
                on_block=print,
                on_tx=print
            )
            notify.listen()


    """

    __events__ = [
        'on_tx',
        'on_object',
        'on_block',
        'on_account',
        'on_market',
    ]

    def __init__(
        self,
        accounts=[],
        markets=[],
        objects=[],
        on_tx=None,
        on_object=None,
        on_block=None,
        on_account=None,
        on_market=None,
        vinchain_instance=None,
    ):
        # Events
        super(Notify, self).__init__()
        self.events = Events()

        # VinChain instance
        self.vinchain = vinchain_instance or shared_vinchain_instance()

        # Markets
        market_ids = []
        for market_name in markets:
            market = Market(
                market_name,
                vinchain_instance=self.vinchain
            )
            market_ids.append([
                market["base"]["id"],
                market["quote"]["id"],
            ])

        # Callbacks
        if on_tx:
            self.on_tx += on_tx
        if on_object:
            self.on_object += on_object
        if on_block:
            self.on_block += on_block
        if on_account:
            self.on_account += on_account
        if on_market:
            self.on_market += on_market

        # Open the websocket
        self.websocket = VinChainWebsocket(
            urls=self.vinchain.rpc.urls,
            user=self.vinchain.rpc.user,
            password=self.vinchain.rpc.password,
            accounts=accounts,
            markets=market_ids,
            objects=objects,
            on_tx=on_tx,
            on_object=on_object,
            on_block=on_block,
            on_account=self.process_account,
            on_market=self.process_market,
        )

    def process_market(self, data):
        """ This method is used for post processing of market
            notifications. It will return instances of either

            * :class:`vinchainio.price.Order` or
            * :class:`vinchainio.price.FilledOrder` or
            * :class:`vinchainio.price.UpdateCallOrder`

            Also possible are limit order updates (margin calls)

        """
        for d in data:
            if not d:
                continue
            if isinstance(d, str):
                # Single order has been placed
                log.debug("Calling on_market with Order()")
                self.on_market(Order(
                    d,
                    vinchain_instance=self.vinchain
                ))
                continue
            elif isinstance(d, dict):
                d = [d]

            # Orders have been matched
            for p in d:
                if not isinstance(p, list):
                    p = [p]
                for i in p:
                    if isinstance(i, dict):
                        if "pays" in i and "receives" in i:
                            self.on_market(FilledOrder(
                                i,
                                vinchain_instance=self.vinchain
                            ))
                        elif "for_sale" in i and "sell_price" in i:
                            self.on_market(Order(
                                i,
                                vinchain_instance=self.vinchain
                            ))
                        elif "collateral" in i and "call_price" in i:
                            self.on_market(UpdateCallOrder(
                                i,
                                vinchain_instance=self.vinchain
                            ))
                        else:
                            if i:
                                log.error(
                                    "Unknown market update type: %s" % i
                                )

    def process_account(self, message):
        """ This is used for processing of account Updates. It will
            return instances of :class:vinchainio.account.AccountUpdate`
        """
        self.on_account(AccountUpdate(
            message,
            vinchain_instance=self.vinchain
        ))

    def listen(self):
        """ This call initiates the listening/notification process. It
            behaves similar to ``run_forever()``.
        """
        self.websocket.run_forever()
