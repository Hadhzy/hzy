
__all__ = ['Base', 'HzyDeletedProxy', 'HzyProxyTooOld', 'HzyNullException']


class Base(Exception):
    pass


class HzyDeletedProxy(Base):
    pass


class HzyProxyTooOld(Base):
    pass


class HzyNullException(Base):
    pass
