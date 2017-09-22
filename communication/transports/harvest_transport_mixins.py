from django.conf import settings
from django.utils import timezone
import datetime
import email
import logging
import shlex
import pickle
import socket
import httplib2
from multiprocessing.reduction import ForkingPickler
from io import StringIO


from communication.transports.base import MessageParseError
from communication.transports import transport_exceptions
"""
These mixins are set up to override methods in the django_mailbox transport classes.
Use these to create new Harvest Transports. I hope this will make future code
updates from the django_mailbox slightly easier.
"""

logger = logging.getLogger(__name__)

# TODO: Document process flow for email harvesting.


class HarvestMailTransportBaseMixin(object):
    def list_folders(self):
        return self._get_folders()

    def list_message_ids(self):
        '''
        I think think should be deprecated.
        :return: integers ids of messages in folder.
        '''
        return self._get_all_message_ids()

    def list_message_uids(self):
        '''
        Gets string UIDs of messages in folder
        :return: list of message UID strings.
        '''
        return self._get_all_message_uids()

    @staticmethod
    def pickle_transport(obj):
        '''
        Part of failed attempt to write decoupled timeout function.
        Could not get pickling of sockets to work.
        :param obj:
        :return:
        '''
        buf = StringIO()
        ForkingPickler(buf).dump(obj)
        return buf.getvalue()

    @staticmethod
    def unpickle_transport(obj):
        '''
        Part of failed attempt to write decoupled timeout function.
        Could not get pickling of sockets to work.
        :param obj:
        :return:
        '''
        # trans = pickle.loads(obj.get())
        trans = pickle.loads(obj)
        return trans


class HarvestImapTransportMixin(HarvestMailTransportBaseMixin):
    '''
    Note: if you want tons of imaplib debug output do this:
        self.server.debug=4
    '''
    def escape_specials(self, arg):
        if self._imap_Atom_Specials.search(arg):
            arg = '"' + arg + '"'
        arg = bytes(arg, 'utf-8')
        return arg

    def connect(self, username, password, timeout=20):
        '''
        Connects to imap server and does a read-only select on the mailbox folder.
        The business about setting the socket timeout is a cheap hack - it sets the default
        timeout for ANY new socket connection spawned by python, so this is bad. It needs to be
        set a then unset. What actually needs to be done is an override/extension of the IMAPlib
        module to properly set the timeout of the specific socket that it creates.
        Other option is to multithread this connect method and time it out from the caller, but pickling
        the transport class (specifically the connected socket) proved to be impossible for me.
        :param username:
        :param password:
        :param timeout: defaults to 20 seconds.
        :return:
        '''

        logger.info("connecting to {} on port {} for folder {}".format(self.hostname, self.port, self.folder))

        saved_default_timeout = socket.getdefaulttimeout()

        try:
            socket.setdefaulttimeout(timeout)
            self.server = self.transport(self.hostname, self.port)

        except self.transport.error as e:
            log_msg = "connection failed for server {} on port {} with message {}".format(self.hostname, self.port, str(e))
            logger.critical(log_msg)
            socket.setdefaulttimeout(saved_default_timeout)
            raise transport_exceptions.ConnectionError(log_msg)

        except socket.timeout:
            log_msg = "connection timed out for server {} on port {} after {} seconds.".format(self.hostname, self.port, timeout)
            logger.critical(log_msg)
            raise transport_exceptions.TimeoutError(log_msg)

        if self.tls:
            self.server.starttls()

        logger.info("logging in to {} on port {} for folder {}".format(self.hostname, self.port, self.folder))

        try:
            socket.setdefaulttimeout(timeout)
            typ, msg = self.server.login(username, password)

        except self.transport.error as e:
            log_msg = "login failed for user:{} on server {} on port {} with message {}".format(username, self.hostname, self.port, str(e))
            logger.critical(log_msg)
            socket.setdefaulttimeout(saved_default_timeout)
            raise transport_exceptions.LoginError(log_msg)

        except socket.timeout:
            log_msg = "connection timed out logging to server {} on port {} after {} seconds.".format(self.hostname, self.port, timeout)
            logger.critical(log_msg)
            raise transport_exceptions.TimeoutError(log_msg)

        if self.folder:
            # Point the connection to this folder:
            try:
                typ, msg = self.server.select(mailbox=self.folder, readonly=True)

                if typ == 'NO' or typ == 'BAD':
                    raise self.transport.error(str(msg))

                logger.debug("Folder selected:{}.".format(self.folder))

            except self.transport.error as e:
                logger.error("Error encountered when selecting folder:{}. {}".format(self.folder, str(e)))

        else:
            raise AttributeError("Harvest IMAP Transport required a foldername to establish an initial connection.")

    def get_message(self, existing_messages_qs=None, search_list=[], lookback_date=None):
        '''
        Overrides django_mailbox.get_message to prevent deletion of messages on the server.
        :param existing_messages_qs: queryset of Message instances from the db that are used to prevent
        downloading duplicate messages. If None, all messages will be downloaded.
        :param search_list: list of strings (ie harvest codes) that will be used to perform server-side search prior to download.
        :param lookback_date: python datetime object defines max lookback date when downloading/searching for messages from the server.
        :return:
        '''

        # Execute string search on server if search_list or lookback_date parameters given:
        if search_list or lookback_date:

            search_string = None
            search_date = None

            if search_list:
                search_string = self._make_imap_keyword_search_string(search_list)
            if lookback_date:
                search_date = self._make_imap_date_search_string(lookback_date)

            ids = self._get_all_message_ids(
                search_condition_1=search_string,
                search_condition_2=search_date,
                as_string=True)
            if ids:
                message_uid_tuples = self._get_all_message_uids(message_id_range=ids)
            else:
                logger.info(msg="_get_all_message_ids yielded no results therefore terminate get_message() for folder: {}".format(self.folder))
                return

        else:
            message_uid_tuples = self._get_all_message_uids()

        message_ids_to_download = []

        if existing_messages_qs is None:
            message_ids_to_download = [id for id, uid in message_uid_tuples]
        else:
            # use the existing list from the db and the message_id:message_uid dict from the
            # server to determine what message_ids should be requested.

            for message_id, message_uid in message_uid_tuples:
                if not existing_messages_qs.filter(message_id=message_uid).exists():
                    logger.debug("({}, {}) Allowing message with id: {} and uid: {} to be downloaded".format(self.hostname, self.folder, message_id, message_uid))
                    message_ids_to_download.append(message_id)
                else:
                    logger.debug("({}, {}) Disallowing message with id: {} and uid: {} to be downloaded".format(self.hostname, self.folder, message_id, message_uid))
                    

        if not message_ids_to_download:
            logger.info(msg="No messages to request for {}.".format(self.folder))
            return

        if self.archive:
            typ, folders = self.server.list(pattern=self.archive)
            if folders[0] is None:
                # If the archive folder does not exist, create it
                self.server.create(self.archive)

        for id in message_ids_to_download:
            try:
                typ, msg_contents = self.server.fetch(id, '(RFC822)')
                if not msg_contents:
                    continue
                try:
                    message = self.get_email_from_bytes(msg_contents[0][1])
                except TypeError:
                    # This happens if another thread/process deletes the
                    # message between our generating the ID list and our
                    # processing it here.
                    if settings.DEBUG:
                        logger.error(msg="Type Error encountered while getting email from bytes. "
                                         "server-side message id:{id}. response message:{typ}. "
                                         "response contents:{msg_contents}".format(id=id, typ=typ, msg_contents=msg_contents))
                    continue

                yield message
            except MessageParseError:
                continue

            if self.archive:
                self.server.uid('copy', id, self.archive)

        return

    def _get_all_message_ids(self, search_condition_1='ALL', search_condition_2=None, as_string=False):
        '''
        Gets integer ids for messages in this folder.
        :param: search_condition_1: takes an optional imap-formatted search string (use _make_imap_keyword_search_string() to make it).
        Defaults to 'ALL'. If the value is None it will also default to 'ALL'.
        :param: search_condition_2: takes an optional imap-formatted search string (use _make_imap_date_search_string() to make it).
        Defaults to None.
        :param: as_string: if True returns the list of IDs as a comma-separated string, False returns list of integer IDs.
        :return: as defined by as_string
        '''
        # Fetch the message uids -- the server folder should have already been
        # selected when the Transport was initialized.
        # If I use UID I get a different set of integer IDs -- I think I should probably
        # use those but don't want to switch right now.

        if search_condition_1 is None:
            search_condition_1 = 'ALL'

        try:
            logger.info(msg="Search server folder {} for messages. "
                            "Search condition 1: \"{}\". "
                            "Search condition 2: \"{}\".".format(self.folder, search_condition_1, search_condition_2))
            # typ, data = self.server.uid('search', search_string)
            typ, data = self.server.search(None, search_condition_1, search_condition_2)
            if typ == 'NO':
                logger.warninging(msg="No message IDs returned in _get_all_message_ids() for {}. ".format(self.folder))
                return None
            elif typ == 'BAD':
                raise self.transport.error(str(data))
        except self.transport.error as e:
            logger.error(msg="Error in _get_all_message_ids() for {}:{}. ".format(self.folder, str(e)))
            return None

        # logger.info(msg="Raw message ids:{}".format(','.join(data)))

        message_id_string = data[0].decode().strip()
        if message_id_string == '':
            return None

        # Usually `message_id_string` will be a list of space-separated
        # ids; we must make sure that it isn't an empty string before
        # splitting into individual UIDs.
        if as_string:
            return message_id_string.replace(' ', ',')
        else:
            return [int(x) for x in message_id_string.split(' ')]

    def _get_all_message_uids(self, message_id_range='1:*'):
        '''
        Fetches UIDs of messages in the current folder.
        :param message_id_range: range of message int ids to fetch for this folder. Defaults to 1:* (all)
        :return: list of tuples:( <str>message_id, <str>message_uid )
        '''
        uids = []
        try:
            typ, data = self.server.fetch(message_id_range, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
            if typ == 'NO':
                logger.warning(
                    msg="No messages returned in _get_all_message_uids() for {} with message id range \"{}\". "
                        .format(self.folder, message_id_range)
                )

            elif typ == 'BAD':
                # Note: This can fail if the mailbox is empty.
                raise self.transport.error(str(data))

        except self.transport.error as e:
            logger.error(
                msg="Error in _get_all_message_uids() for {} with message id range \"{}\":\"{}\". "
                    "This may only mean that the folder has no messages in it."
                    .format(self.folder, message_id_range, str(e)))

            return uids

        for entry in data:
            try:
                if type(entry) is not tuple:
                    if entry.decode() == ")":
                        continue
                message_id = entry[0].decode().split(" ")[0]
                msg_str = entry[1].decode()
                message = email.message_from_string(msg_str)
                message_uid = message.get('Message-ID').strip()
                uids.append((message_id, message_uid))
            except IndexError as e:
                if settings.DEBUG:
                    logger.warning(msg="Error decoding message-id tuple. {}. {}".format(entry, str(e)))
                pass
            except AttributeError as e:
                if settings.DEBUG:
                    logger.warning(msg="Error decoding message-id tuple. {}. {}".format(entry, str(e)))
                pass

        return uids

    def _get_folders(self):
        folders = []
        try:
            typ, lst = self.server.list()
            if typ == 'NO' or typ == 'BAD':
                # Note: This can fail if the mailbox is empty.
                raise self.transport.error(str(lst))
        except self.transport.error as e:
            logger.error(msg="Error in _get_folders() for {}:{}".format(self.server, str(e)))
            return []

        for entry in lst:
            try:
                # if there is a weird character in the folder name
                # the entry will be a tuple instead of a space-separated list:
                if type(entry) is tuple:
                    entry = entry[1]
                    folder_str = entry.decode()
                else:
                    # shlex will split on space but preserve quoted string (but quotes are stripped off)
                    folder_str = shlex.split(entry.decode())[-1]

                # TODO: Figure out how to get IMAP foldernames with funny characters to work.
                if self._imap_Atom_Specials.search(folder_str):
                    msg = "Currently Harvest IMAP transport does not know how to handle foldernames with some characters. Folder" \
                          + folder_str + " will be quoted, cross fingers & hope for the best."
                    logger.warning(msg)
                    folder_str = '"{}"'.format(folder_str)

                # Strip off leading and trailing double quotes before appending:
                # folder_str = folder_str.strip('"')

                folders.append(folder_str)

            except IndexError as e:
                if settings.DEBUG:
                    logger.info(msg="IndexError extracting foldername from response. {}. {}".format(entry, str(e)))
            except AttributeError as e:
                if settings.DEBUG:
                    logger.info(msg="Attribute error extracting foldername from response. {}. {}".format(entry, str(e)))
        return folders

    def _make_imap_keyword_search_string(self, string_list=[], search_string=''):
        '''
        Produces a search string that will be used to search imap folders for messsages
        where TEXT (email headers or body) contains one of the strings.
        It builds a crazy nested string of crazy imap ORs. Enjoy debugging.
        Be careful with exchange - it is less forgiving about the format of the query
         than the other imap server I tested with. Don't less extraneous spaces in the query
        :param string_list: python list of search strings (eg harvest prefixes).
        :return: imap-formed string of concatenated search strings on body and subject.
        '''

        # make sure it's a list (not just a ValuesListQuerySet
        string_list = list(string_list)

        template_double_outer = '(OR TEXT "{}" {})'  # must always be wrapped in () after formatting.
        template_double_inner = '(OR TEXT "{}" TEXT "{}")'
        template_single = '(TEXT "{}")'

        if len(string_list) == 1 and search_string == '':
            term_1 = string_list.pop().strip()
            search_string = template_single.format(term_1)

        elif len(string_list) >= 2 and search_string == '':
            term_1 = string_list.pop().strip()
            term_2 = string_list.pop().strip()
            search_string = template_double_inner.format(term_1, term_2)

        elif len(string_list) > 0 and search_string != '':
            term_1 = string_list.pop().strip()
            search_string = template_double_outer.format(term_1, search_string)

        if len(string_list) == 0:
            return search_string
        else:
            return self._make_imap_keyword_search_string(string_list, search_string)

    def _make_imap_date_search_string(self, lookback_date):
        '''
        Produces a search string that will be used to search imap folders for messsages
        where since is less than lookback_date. Truncates the time portion, returns DATE string.
        :param lookback_date: python datetime object representing max lookback date
        :return: imap-formed date string: '%d-%b-%Y' (DATE only, no TIME component).
        '''
        format_string = '%d-%b-%Y'

        # IMAP is dumb and only seems to want to look back whole days. Check and make sure that
        # the lookback date actually goes at least ONE day back, ajdust if not:
        if timezone.now().strftime(format_string) == lookback_date.strftime(format_string):
            lookback_delta = datetime.timedelta(days=1)
            lookback_date = lookback_date - lookback_delta

        template_datesearch = '(SINCE {lookback})'
        return template_datesearch.format(lookback=lookback_date.strftime(format_string))


class HarvestImapExchangeTransportMixin(HarvestImapTransportMixin):

    def get_message(self, existing_messages_qs=None, search_list=[], lookback_date=None):
        '''
        Imap Exchange get_message -- tiny override that sets search_list always to an empty list.
        Exchange server can't properly handle string searches in the body (in replies) - yay - so
        instead we want to always download any messages that aren't in the Cedar system and then parse
        them cedar-server-side.
        :param existing_messages_qs:
        :param search_list:
        :return: email messages
        '''
        return super(HarvestImapExchangeTransportMixin, self).get_message(
            existing_messages_qs=existing_messages_qs,
            search_list=[],
            lookback_date=lookback_date)


class HarvestPop3TransportMixin(HarvestMailTransportBaseMixin):
    def get_message(self, condition=None):
        '''
        Overrides django_mailbox.get_message to prevent deletion of messages on the server.
        NOTE: this hasn't been kept up to date - dev priority given to the imap transport. Use that
        as reference when building out proper pop support.
        :param condition:
        :return:
        '''
        message_count = len(self.server.list()[1])
        for i in range(message_count):
            try:
                msg_contents = self.get_message_body(
                    self.server.retr(i + 1)[1]
                )
                message = self.get_email_from_bytes(msg_contents)

                if condition and not condition(message):
                    continue

                yield message
            except MessageParseError:
                continue

                # don't delete messages on the server. kept here for reference.
                # self.server.dele(i + 1)
        self.server.quit()
        return

    def _get_folders(self):
        raise NotImplementedError("POP3 does not support server folders.")


class HarvestImapGmailTransportMixin(HarvestImapTransportMixin):
    def connect(self, username, password, timeout=20):
        # Try to use oauth2 first.  It's much safer
        try:
            self._connect_oauth(username)
        except (TypeError, ValueError) as e:
            logger.warninging("Couldn't do oauth2 because %s" % e)
            raise transport_exceptions.OAuth2ConnectionError(str(e))

    def _connect_oauth(self, username, timeout=20):
        # username should be an email address that has already been authorized
        # for gmail access
        http = httplib2.Http(timeout=timeout)
        logger.info("getting credentials for user {}".format(username))
        credentials = self.credentials
        logger.info("authorizing credentials for user {}".format(username))
        http = credentials.authorize(http)
        logger.info("refreshing credentials for user {}".format(username))
        credentials.refresh(http)

        logger.info("getting access token for user {}".format(username))
        access_token = credentials.access_token

        auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
        logger.info("attempting to connect for user {} on hostname: {}:{}".format(username, self.hostname, self.port))
        self.server = self.transport(self.hostname, self.port)
        logger.info("authenticating connection for user {} on hostname: {}:{}".format(username, self.hostname, self.port))
        self.server.authenticate('XOAUTH2', lambda x: auth_string)
        logger.info("selecting imap folder \"{}\" for user {} on hostname: {}:{}".format(self.folder, username, self.hostname, self.port))

        if self.folder:
            # Point the connection to this folder:
            try:
                typ, msg = self.server.select(mailbox=self.folder, readonly=True)

                if typ == 'NO' or typ == 'BAD':
                    raise self.transport.error(str(msg))

            except self.transport.error as e:
                logger.error("Error encountered when selecting folder:{}. {}".format(self.folder, str(e)))

        else:
            raise AttributeError("Harvest IMAP-GMAIL Transport required a foldername to establish an initial connection.")
