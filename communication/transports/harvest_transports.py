from communication.transports.imap import ImapTransport
from communication.transports.pop3 import Pop3Transport
from communication.transports.gmail import GmailImapTransport
from communication.transports.harvest_transport_mixins import HarvestImapTransportMixin, HarvestPop3TransportMixin,\
    HarvestImapExchangeTransportMixin, HarvestImapGmailTransportMixin

import re

'''
Use these harvest transports instead of the django_mailbox transports. If we
build with mixins we can limit possible conflicts when it comes time to upgrade the
django_mailbox transports. Mixins should sit on top of the existing transports, editing
the base transports directly should be avoided.
'''

specials = re.compile(r'[\(\)\{ \%\*\"\\\]]')


class HarvestImapTransport(HarvestImapTransportMixin, ImapTransport):
    _imap_Atom_Specials = specials

    def __init__(self, hostname, port=None, ssl=False, tls=False, archive='', folder=None):
        super(HarvestImapTransport, self).__init__(hostname, port, ssl, tls, archive, folder)


class HarvestPop3Transport(HarvestPop3TransportMixin, Pop3Transport):
    _imap_Atom_Specials = specials


class HarvestImapExchangeTransport(HarvestImapExchangeTransportMixin, ImapTransport):
    _imap_Atom_Specials = specials


class HarvestGmailTransport(HarvestImapGmailTransportMixin, GmailImapTransport):
    _imap_Atom_Specials = specials