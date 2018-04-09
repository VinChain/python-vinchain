import warnings


class GrapheneWebsocketProtocol():
    """ This class is **deprecated**. The old implementation can by
        found in python-bitshares (still deprecated, but functional)
    """

    def __init__(self, *args, **kwargs):
        raise DeprecationWarning(
            "[DeprecationWarning] The GrapheneWebsocket is deprecated\n"
            "or VinChain specific. The old implementation can be\b"
            "found in\n\n"
            "    from vinchainioapi.websocketprotocol import BitSharesWebsocketProtocol"
        )
        super(GrapheneWebsocketProtocol, self).__init__(*args, **kwargs)
