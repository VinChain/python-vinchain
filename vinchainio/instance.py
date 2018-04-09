import vinchainio as vin


class SharedInstance:
    instance = None


def shared_vinchain_instance():
    """ This method will initialize ``SharedInstance.instance`` and return it.
        The purpose of this method is to have offer single default
        vinchainio instance that can be reused by multiple classes.
    """
    if not SharedInstance.instance:
        clear_cache()
        SharedInstance.instance = vin.VinChain()
    return SharedInstance.instance


def set_shared_vinchain_instance(vinchain_instance):
    """ This method allows us to override default vinchainio instance for all users of
        ``SharedInstance.instance``.

        :param vinchainio.vinchain.VinChain vinchain_instance: VinChain instance
    """
    clear_cache()
    SharedInstance.instance = vinchain_instance


def clear_cache():
    """ Clear Caches
    """
    from .blockchainobject import BlockchainObject
    BlockchainObject.clear_cache()
