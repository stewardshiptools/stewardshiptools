from mailbox import MH
from communication.transports.generic import GenericFileMailbox


class MHTransport(GenericFileMailbox):
    _variant = MH
