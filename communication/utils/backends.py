import smtplib
import logging
import httplib2
import base64
import binascii
import threading
from django.core.mail.utils import DNS_NAME
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

from communication.models import MailAccount, Mailbox


logger = logging.getLogger(__name__)


class GmailBackend(EmailBackend):
    '''
    This is a non-functional add.
    I there is a problem with the syntax of the AUTH command. See google response.
    Track work here https://trello.com/c/PxWFiNpO/109-email-backend-try-to-user-gmail-account

    This is being committed to the repo despite being non-functional due to some handy
    refactoring done to the comms utils modules to accomodate the new (faulty) backend.

    https://github.com/google/gmail-oauth2-tools/blob/master/python/oauth2.py
    https://developers.google.com/gmail/xoauth2_protocol
    '''

    def __init__(self, *args, **kwargs):
        self.fail_silently = kwargs.pop('fail_silently', True)

        # print ('kwargs:', kwargs)
        self.connection = None
        self.mail_account = self.get_mail_account()
        self.mailbox = Mailbox(mail_account=self.mail_account)

        self.username = self.mail_account.username

        self._lock = threading.RLock()

    def open(self):

        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        try:
            self.connection = self.get_connection()
            # if self.username and self.password:
            #     self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise

    def get_mail_account(self):
        username = settings.EMAIL_BACKEND_GMAIL_ADDRESS
        return MailAccount.objects.get(username=username)

    def get_connection(self, timeout=20):
        '''


        http://stackoverflow.com/questions/18391741/send-mail-via-smtp-ideally-using-oauth-2-0-in-a-google-marketplace-app
        :param timeout:
        :return:
        '''

        http = httplib2.Http(timeout=timeout)
        logger.info("getting credentials for user {}".format(self.mailbox.username))
        credentials = self.mail_account.gmailcredential.credential
        logger.info("authorizing credentials for user {}".format(self.mailbox.username))
        http = credentials.authorize(http)
        logger.info("refreshing credentials for user {}".format(self.mailbox.username))
        credentials.refresh(http)

        logger.info("getting access token for user {}".format(self.mailbox.username))
        access_token = credentials.access_token

        # conn = smtplib.SMTP('smtp.googlemail.com', 587)
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.set_debuglevel(True)
        conn.ehlo('test')
        conn.starttls()
        # conn.ehlo('test2')
        # auth_string = 'user=%s\1auth=Bearer %s\1\1' % (self.mail_account.username, credentials.access_token)
        auth_string = generateOAuth2String(self.mail_account.username, credentials.access_token, False)
        auth_string = auth_string.encode('utf-8')
        conn.docmd('AUTH XOAUTH2', auth_string)
        return conn


'''
from django.core.mail import send_mail
send_mail('subject', 'message', 'adam@cedarbox.ca', ['djang@bitspatial.com'])

from communication.utils.backends import GmailBackend
GmailBackend().open()


# For testing oauth2 connection stuff:
from communication.utils.backends import GmailBackend
ge = GmailBackend()
ge.get_connection()

import base64
base64.b64decode('dXNlcj14b2F1dGhAZ21haWwuY29tAWF1dGg9QmVhcmVyIHlhMjkuQUhFUzZaUktlVVF3SDJ4aGlya3NTVURTeWpnOW9QdVJNTWFsMDVUeTBjZkZJVF91UmZFU0h3AQE=')
b'user=xoauth@gmail.com\x01auth=Bearer ya29.AHES6ZRKeUQwH2xhirksSUDSyjg9oPuRMMal05Ty0cfFIT_uRfESHw\x01\x01'


'''


def generateOAuth2String(username, access_token, base64_encode=False):
    """Generates an SMTP OAuth2 authentication string.
    See https://developers.google.com/google-apps/gmail/oauth2_overview
    Args:
      username: the username (email address) of the account to authenticate
      access_token: An OAuth2 access token.
      base64_encode: Whether to base64-encode the output. (no for imaplib, yes for smtplib)
    Returns:
      The SASL argument for the OAuth2 mechanism.
    """
    auth_string = 'user={}\1auth=Bearer {}\1\1'.format(username, access_token)
    if base64_encode:
        auth_string = base64.b64encode(auth_string)
    return auth_string
