#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models declaration for application ``django_mailbox``.
"""

from email.encoders import encode_base64
from email.message import Message as EmailMessage
from email.utils import formatdate, parseaddr, parsedate_tz, parsedate_to_datetime
from quopri import encode as encode_quopri
import base64
import email
import logging
import mimetypes
import os.path
import sys
import uuid

import six
from urllib import parse

import django
from django.conf import settings as django_settings
from django.core.files.base import ContentFile
from django.core.mail.message import make_msgid
from django.core.urlresolvers import reverse
from django.utils import timezone

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from model_utils.managers import InheritanceManager

from communication.utils import comm_utils
from communication.transports.harvest_transports import HarvestImapTransport, HarvestPop3Transport, HarvestGmailTransport, \
    HarvestImapExchangeTransport
from communication.transports import transport_exceptions

from cryptographic_fields.fields import EncryptedCharField
from phonenumber_field.modelfields import PhoneNumberField

from oauth2client.contrib.django_util.models import CredentialsField

import assets
import crm
from crm.models import Person
from cedar_settings.models import GeneralSetting

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# For DRF Serializing See:
# http://www.django-rest-framework.org/api-guide/relations/#rest-framework-generic-relations

class ActiveObjectManager(models.Manager):
    """
    Filters all objects that are not active.
    Requires a boolean field called 'active'
    """

    def get_queryset(self):
        return super(ActiveObjectManager, self).get_queryset().filter(active=True)


class Communication(models.Model):
    """
    Sort-of parent object for Communication Type (Phone, Fax, Message, etc.) objects.
    Note: a post_delete signal is attached that will delete the comm_type instance when
    a Communication instance is deleted. Since CommunicationRelation objects will cascade
    we don't have to worry about those.
    """
    subject = models.TextField(max_length=1000)
    date = models.DateTimeField(verbose_name='Date & time of communication.')

    from_contacts = models.ManyToManyField(crm.models.Person, related_name='from_contact')
    to_contacts = models.ManyToManyField(crm.models.Person, related_name='to_contact')

    # Generic foreign keys to communication types (Fax, PhoneCall, Message, etc.)
    comm_type_ct = models.ForeignKey(ContentType)
    comm_type_oid = models.PositiveIntegerField()
    comm_type = GenericForeignKey('comm_type_ct', 'comm_type_oid')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return '{}: {}'.format(self.date, self.subject)

    @classmethod
    def create_communication(cls, subject, date, from_contacts, to_contacts, comm_type_obj):
        """
        Takes a communication type object, creates a communication instance and creates a relation between the two.
        :param subject:
        :param date:
        :param from_contacts:
        :param to_contacts:
        :param comm_type_obj: PhoneCall, Message, Fax, etc.
        :return:
        """
        comm = Communication(
            subject=subject,
            date=date,
        )
        comm.comm_type = comm_type_obj
        comm.save()

        if from_contacts:
            comm.from_contacts = from_contacts
        if to_contacts:
            comm.to_contacts = to_contacts

        comm.save()

        return comm

    @classmethod
    def create_related_communication(cls, subject, date, from_contacts, to_contacts, comm_type_obj, related_obj):
        """
        Takes a communication type object, creates a communication instance and creates a relation between the two.
        :param subject:
        :param date:
        :param from_contacts:
        :param to_contacts:
        :param comm_type_obj: PhoneCall, Message, Fax, etc.
        :param related_obj: eg HER Prj, DEV Prj, etc.
        :return:
        """
        comm = Communication(
            subject=subject,
            date=date,
            # comm_type=comm_type_obj
        )
        comm.comm_type = comm_type_obj

        if from_contacts:
            comm.from_contacts = from_contacts
        if to_contacts:
            comm.to_contacts = to_contacts

        comm.save()

        CommunicationRelation(
            comm=comm,
            related_object=related_obj
        ).save()

        return comm

    @classmethod
    def get_communications_related_to(cls, related_object):
        """
        Takes some object (eg development project instance) and returns communication objects
        related to it.
        :param related_object:
        :return: communication queryset
        """
        return Communication.objects.filter(
            related_communication__related_object_oid=related_object.id,
            related_communication__related_object_ct=ContentType.objects.get_for_model(related_object)
        )

    def get_absolute_url(self):
        """
        :return:the url to the comm_type object not the parent communication object itself.
        """
        return self.comm_type.get_absolute_url()


class CommunicationRelation(models.Model):
    """
    Relates a communication instance to some other model in the database. The expectation
    for now is that the related_object will be a development project or heritage project.
    """
    comm = models.ForeignKey(Communication, related_name='related_communication')

    related_object_ct = models.ForeignKey(ContentType)
    related_object_oid = models.PositiveIntegerField()
    related_object = GenericForeignKey('related_object_ct', 'related_object_oid')

    def __str__(self):
        return "{}: {}: {}".format(self.comm.date, self.comm.comm_type_ct, self.related_object)


class CommunicationAsset(assets.models.SecureAsset):
    """
    This is a deprecated model - created prior to generic link assets.
    """

    @property
    def storage_string(self):
        return "communication_assets"

    objects = InheritanceManager()


class CommunicationFileRelation(models.Model):
    """
    Provides a method for communication type instances to have a x-many
    relationship with any (asset) model instance(s). The presumption here is that
    the "asset" points to an implementation of the assets.SecureAsset class.
    """
    asset_ct = models.ForeignKey(ContentType, related_name='communicationfilerelation_ct')
    asset_oid = models.PositiveIntegerField()
    asset = GenericForeignKey('asset_ct', 'asset_oid')

    # Generic foreign keys to communication types (Fax, PhoneCall, Message, etc.)
    comm_type_ct = models.ForeignKey(ContentType)
    comm_type_oid = models.PositiveIntegerField()
    comm_type = GenericForeignKey('comm_type_ct', 'comm_type_oid')


class CommunicationTypeAbstract(models.Model):
    communication = GenericRelation(Communication, content_type_field='comm_type_ct', object_id_field='comm_type_oid')

    class Meta:
        abstract = True


class MailAccount(models.Model):
    protocol_choices = (
        ('pop3', 'pop3'),
        ('imap', 'imap'),
        ('imap-exchange', 'imap-exchange'),
        ('gmail', 'imap-gmail')
    )
    email_address = models.EmailField(help_text="Email address for this account. May differ from username.")
    username = models.CharField(
        max_length=100,
        help_text="Username required for login to the mail server.")
    password = EncryptedCharField(max_length=50, blank=True, null=True)
    server_address = models.CharField(
        max_length=300,
        verbose_name="Address of the server",
        help_text="Address of the mail server. Eg: www.example.com, 192.168.5.1, etc.")
    protocol = models.CharField(
        max_length=20,
        choices=protocol_choices,
        default='imap',
        help_text="If you use gmail SSL must be enabled."
    )

    ssl = models.BooleanField(default=False)

    def get_folders(self):
        """
        Queries server via a temp mailbox for folder names
        :return: list of foldernames on the server.
        """
        # use a temporary mailbox for it's connection:
        m = Mailbox(mail_account=self)
        return m.get_mail_folders()

    def update_folders(self):
        """
        Creates mailboxes for each folder returned from the server.
        :return: list of names of created folders
        """
        new = []
        for folder in self.get_folders():
            mbx, created = Mailbox.objects.get_or_create(folder_name=folder, mail_account=self)
            if created:
                new.append(mbx)
        return new

    def harvest_mail(self):
        comm_utils.harvest_mailboxes(self.mailbox_set.filter(active=True))

    def __str__(self):
        return '{} - {}'.format(self.username, self.server_address)

    class Meta:
        permissions = (
            ("harvest_mail_account", "Can run mailharvest on mail account"),
        )


class Mailbox(models.Model):
    folder_name = models.CharField(max_length=300,
                                   default='INBOX',
                                   help_text='This is the un-url-quoted folder name')

    active = models.BooleanField(
        _(u'Active'),
        help_text=(_(
            "Check this e-mail inbox for new e-mail messages during polling "
            "cycles.  This checkbox does not have an effect upon whether "
            "mail is collected here when this mailbox receives mail from a "
            "pipe, and does not affect whether e-mail messages can be "
            "dispatched from this mailbox. "
        )),
        blank=True,
        default=False,
    )

    mail_account = models.ForeignKey(MailAccount)

    incoming = models.BooleanField(
        default=True,
        verbose_name="Is Incoming",
        help_text="False if this is an outgoing mailbox (e.g. 'Sent Mail'), True if otherwise.")

    # hierarchy_delimiter = models.CharField(
    #     max_length=1,
    #     blank=True,
    #     null=True,
    #     verbose_name='IMAP folder hierarchy delimiter. Set automatically by the mailaccount when folders (mailboxes) are created.')

    objects = models.Manager()

    @property
    def uri_template(self):
        return '{protocol}://{user}:{password}@{server_address}?folder={folder}'

    @property
    def uri(self):
        """
        Most important property of mailbox. Everything derives from this.
        :return:
        """
        if self.mail_account.ssl:
            protocol = self.mail_account.protocol + "+ssl"
        else:
            protocol = self.mail_account.protocol

        password = None
        if self.mail_account.password:
            password = parse.quote(self.mail_account.password)

        return self.uri_template.format(
            protocol=protocol,
            user=parse.quote(self.mail_account.username),
            password=password,
            server_address=self.mail_account.server_address,
            folder=parse.quote(self.folder_name)
        )

    @property
    def uri_sani_pretty(self):
        """
        Same as uri property but with user/pass excluded and things unquoted.
        :return:
        """
        return self.uri_template.format(
            protocol=self.mail_account.protocol,
            user="username",
            password="password",
            server_address=self.mail_account.server_address,
            folder=self.folder_name
        )

    @property
    def _protocol_info(self):
        return parse.urlparse(self.uri)

    @property
    def _query_string(self):
        return parse.parse_qs(self._protocol_info.query)

    @property
    def _domain(self):
        return self._protocol_info.hostname

    @property
    def folder(self):
        """Returns the folder to fetch mail from."""
        # return parse.quote(self.folder_name)
        folder = self._query_string.get('folder', None)[0]
        # see BUG: https://bugs.python.org/issue13940
        # if there are special characters we should quote them ourselves:
        # folder = '"{}"'.format(folder)
        return folder

    @property
    def folder_pretty(self):
        # Todo: implement field to store imap folder hierachy delimiter. For now, assume it's a "."
        f = self.folder
        return f.split('.')[-1]

    @property
    def name(self):
        return '{}__{}'.format(self.mail_account.username, self.folder)

    @property
    def port(self):
        """Returns the port to use for fetching messages."""
        return self._protocol_info.port

    @property
    def username(self):
        """Returns the username to use for fetching messages."""
        return parse.unquote(self._protocol_info.username)

    @property
    def password(self):
        """Returns the password to use for fetching messages."""
        return parse.unquote(self._protocol_info.password)

    @property
    def from_email(self):
        return self.mail_account.email_address

    @property
    def location(self):
        """Returns the location (domain and path) of messages."""
        return self._domain if self._domain else '' + self._protocol_info.path

    @property
    def type(self):
        """Returns the 'transport' name for this mailbox."""
        scheme = self._protocol_info.scheme.lower()
        if '+' in scheme:
            return scheme.split('+')[0]
        return scheme

    @property
    def use_ssl(self):
        """Returns whether or not this mailbox's connection uses SSL."""
        return '+ssl' in self._protocol_info.scheme.lower()

    @property
    def use_tls(self):
        """Returns whether or not this mailbox's connection uses STARTTLS."""
        return '+tls' in self._protocol_info.scheme.lower()

    @property
    def archive(self):
        """Returns (if specified) the folder to archive messages to."""
        archive_folder = self._query_string.get('archive', None)
        if not archive_folder:
            return None
        return archive_folder[0]

    def get_connection(self):
        """
        Decides on the transport required and initiates the connection.
        :return:
        """

        # Define method-level variable that connect_to_transport() can reference outside of its own scope.
        # I have doubts that this will work when connect_to_transport() is executed in its own process.
        transport = None

        if not self.uri:
            transport = None
        elif self.type == 'imap':
            transport = HarvestImapTransport(
                self.location,
                port=self.port if self.port else None,
                ssl=self.use_ssl,
                tls=self.use_tls,
                archive=self.archive,
                folder=self.folder
            )
        elif self.type == 'imap-exchange':
            transport = HarvestImapExchangeTransport(
                self.location,
                port=self.port if self.port else None,
                ssl=self.use_ssl,
                tls=self.use_tls,
                archive=self.archive,
                folder=self.folder
            )
        elif self.type == 'gmail':
            mail_account = self.mail_account
            credentials = mail_account.gmailcredential.credential

            transport = HarvestGmailTransport(
                self.location,
                port=self.port if self.port else None,
                ssl=True,
                archive=self.archive,
                credentials=credentials,
                folder=self.folder
            )
        elif self.type == 'pop3':
            transport = HarvestPop3Transport(
                self.location,
                port=self.port if self.port else None,
                ssl=self.use_ssl
            )
        else:
            logger.error("Error choosing mail transport class for mailbox:", str(self))
            transport = None

        if transport is None:
            logger.error("A valid transport class could not be determined for this mailbox:", str(self))
        else:
            try:
                default_timeout = GeneralSetting.objects.get('communication__mailharvest_get_connection_timeout')
                transport.connect(self.username, self.password, default_timeout)
            except (transport_exceptions.ConnectionError,
                    transport_exceptions.LoginError,
                    transport_exceptions.TimeoutError) as e:
                # The transport will have already logged the error. We should give some user feed back here.
                # TODO: present to user some error message about failing to connect to the mail server.
                return None

            return transport

    def get_mail_folders(self):
        """
        Connect to this transport and fetch imap folders
        :param:
        :return:
        """
        folders = []
        connection = self.get_connection()
        if not connection:
            return folders
        else:
            folders = connection.list_folders()
        return folders

    def get_message_ids(self):
        """
        Connect to this transport and fetch message Ids
        :return:
        """
        connection = self.get_connection()
        message_ids = []

        if not connection:
            return message_ids
        for thing in connection.list_message_ids():
            message_ids.append(thing)
            print("message id:", thing)
        return message_ids

    def get_message_uids(self):
        """
        Connect to this transport and fetch message UIds
        :return:
        """
        connection = self.get_connection()
        message_uids = []
        if not connection:
            return message_uids
        for thing in connection.list_message_uids():
            message_uids.append(thing)
        return message_uids

    def harvest_mail(self):
        """Connect to this transport and fetch new messages."""
        new_mail = comm_utils.harvest_mailbox(self)
        return new_mail

    def _get_dehydrated_message(self, msg, record):
        """
        Gets the various message pieces of msg (EmailMessage) and stores as Attachments related to record (Message).
        Called by Mailbox._process_message()
        Calls itself resursively if the message is MULTIPART.

        :param msg: EmailMessage object instance
        :param record: communications.Message model instance
        :return: EmailMessage object (NOT communication.Message model)
        """
        settings = comm_utils.get_settings()

        new = EmailMessage()
        if msg.is_multipart():
            for header, value in msg.items():
                new[header] = value
            for part in msg.get_payload():
                new.attach(
                    self._get_dehydrated_message(part, record)
                )

        # cedar8 is not using the strip_unnallowed mimetypes setting, no this code is never executed.
        elif settings['strip_unallowed_mimetypes'] and not msg.get_content_type() in settings['allowed_mimetypes']:
            for header, value in msg.items():
                new[header] = value
            # Delete header, otherwise when attempting to  deserialize the
            # payload, it will be expecting a body for this.
            del new['Content-Transfer-Encoding']
            new[settings['altered_message_header']] = (
                'Stripped; Content type %s not allowed' % (
                    msg.get_content_type()
                )
            )
            new.set_payload('')
        elif (
                    (msg.get_content_type() not in settings['text_stored_mimetypes'])
                or
                    ('attachment' in msg.get('Content-Disposition', ''))
        ):
            filename = None
            raw_filename = msg.get_filename()
            if raw_filename:
                filename = comm_utils.convert_header_to_unicode(raw_filename)
            if not filename:
                extension = mimetypes.guess_extension(msg.get_content_type())
            else:
                _, extension = os.path.splitext(filename)
            if not extension:
                extension = '.bin'

            filename_safe = uuid.uuid4().hex + extension
            if not filename:
                filename = filename_safe

            # create a blank attachment instance and copy in some email stuff:
            attachment = MessageAttachment()
            attachment.message = record
            for key, value in msg.items():
                attachment[key] = value

            content_file = ContentFile(six.BytesIO(msg.get_payload(decode=True)).getvalue())

            # test the attachment before saving. If it's an image, inline, and small, don't save it.
            # If we return "new" without setting the EmailMessage's 'attachment_interpolation_header' then I think we're cool.
            # TODO Implement Message Attachment Blacklist HERE.
            try:
                if attachment['Content-Disposition'].startswith('inline') and attachment['Content-Type'].startswith('image'):
                    min_img_size_KB = GeneralSetting.objects.get('communication__mailharvest_min_inline_img_size_KB')
                    if content_file.size/1000 < min_img_size_KB:
                        logger.warning("SKIP attachment: inline image size {} KB is smaller than min image size setting of {} KB."
                                       .format(content_file.size/1000, min_img_size_KB))
                        placeholder = EmailMessage()

                        # return placeholder without the interpolation header:
                        return placeholder

            except KeyError:
                # we tried to check a header that wasn't there. that's ok, keep on keepin' on.
                logger.warning("checking for attachment headers - we referenced a header that wasn't there. that's probably ok.")

            # if we've made it here, continue with saving and relating the attachment.
            attachment.save()

            '''
            create temporary CommunicationAssets. "Temporary" because
            the message hasn't yet been parsed for harvest codes.
            these will be transferred into related asset classes at that point (if there
            are found to be related instances, other will remain CommunicationAssets).
            '''

            comm_asset = CommunicationAsset()
            comm_asset.name = filename
            comm_asset.save()
            comm_asset.file.save(filename_safe, content_file)
            attachment.create_file_relation(comm_asset)

            placeholder = EmailMessage()
            placeholder[
                settings['attachment_interpolation_header']
            ] = str(attachment.pk)
            new = placeholder
        else:
            content_charset = msg.get_content_charset()
            if not content_charset:
                content_charset = 'ascii'
            try:
                # Make sure that the payload can be properly decoded in the
                # defined charset, if it can't, let's mash some things
                # inside the payload :-\
                msg.get_payload(decode=True).decode(content_charset)
            except LookupError:
                logger.warning(
                    "Unknown encoding %s; interpreting as ASCII!",
                    content_charset
                )
                msg.set_payload(
                    msg.get_payload(decode=True).decode(
                        'ascii',
                        'ignore'
                    )
                )
            except ValueError:
                logger.warning(
                    "Decoding error encountered; interpreting %s as ASCII!",
                    content_charset
                )
                msg.set_payload(
                    msg.get_payload(decode=True).decode(
                        'ascii',
                        'ignore'
                    )
                )
            new = msg
        return new

    def _process_message(self, message):
        """
        This is the guy that does the magic.
        :param message:
        :return: msg (Message)
        """

        msg = Message()
        settings = comm_utils.get_settings()

        # Get message-id - this is a critical piece, it shouldn't be conditional.
        # if 'message-id' in message:
        msg.message_id = message['message-id'].strip()
        if not msg.message_id:
            raise AttributeError("Harvest acquired a message without a message id. Message: {}".format(message))
        if Message.objects.filter(mailbox=self, message_id=msg.message_id).exists():
            logger.error("Problem. A message was about to be processed that already exists in C8. Message id: {}".format(msg.message_id))
            return

        # Set owning mailbox:
        msg.mailbox = self

        # Get message date:
        date = parsedate_to_datetime(message.get('date'))

        if settings['store_original_message']:
            msg.eml.save(
                '%s.eml' % uuid.uuid4(),
                ContentFile(message.as_string()),
                save=False
            )

        # Get message subject:
        if 'subject' in message:
            msg.subject = comm_utils.convert_header_to_unicode(message['subject'])[0:255]
        else:
            msg.subject = '[No subject]'

        # Get senders:
        if 'from' in message:
            msg.from_header = comm_utils.convert_header_to_unicode(message['from'])
            from_contacts = crm.models.Person.objects.filter(email__in=msg.from_address)
        else:
            from_contacts = Person.objects.none()

        # Get receivers
        if 'to' in message:
            msg.to_header = comm_utils.convert_header_to_unicode(message['to'])
            to_contacts = crm.models.Person.objects.filter(email__in=msg.to_addresses)
        elif 'Delivered-To' in message:
            msg.to_header = comm_utils.convert_header_to_unicode(message['Delivered-To'])
            to_contacts = crm.models.Person.objects.filter(email__in=msg.to_addresses)
        else:
            to_contacts = Person.objects.none()

        msg.save()
        message = self._get_dehydrated_message(message, msg)
        msg.set_body(message.as_string())

        if message['in-reply-to']:
            try:
                msg.in_reply_to = Message.objects.filter(
                    message_id=message['in-reply-to'].strip()
                )[0]
            except IndexError:
                pass

        msg.save()

        # Process Message for harvest codes:
        relations = comm_utils.parse_message_for_entity_relations(
            harvest_prefixes=HarvestCodePrefix.objects.all(),
            message=msg
        )

        '''
            Use the message/object relations we made in the previous step to set up
            the Communication, CommunicationRelation, HarvestPrefixRelations. Also,
            if the message is related to something and it has attachments, then those
            attachments need to be converted from CommunicationAssets in to whatever
            asset class the related object suggests (eg. get_asset_class()
        '''

        if relations:

            # Create the communication object (one message, one comm, but possibly many relations):
            comm = Communication.create_communication(
                subject=msg.subject,
                date=date,
                from_contacts=from_contacts,
                to_contacts=to_contacts,
                comm_type_obj=msg
            )

            for relation in relations:
                # This HMR step should be dropped in favour of the CR below - but I like it, so don't drop it.
                HarvestMessageRelation.objects.create(
                    related_object=relation['related_object'],
                    message=relation['message'],  # This should be the same as "msg" in this method scope.
                    harvest_code_prefix=relation['harvest_code_prefix'],
                    harvest_code_full=relation['harvest_code_full']
                )

                CommunicationRelation(
                    comm=comm,
                    related_object=relation['related_object']
                ).save()

                # determine what do to with message attachments' CFRs:
                if msg.attachments.count() > 0:
                    for attachment in msg.attachments.all():
                        # save a pointer to the original Communication File Relation
                        attachment_file_relation = attachment.file_relations.first()

                        try:
                            new_asset_instance = relation['related_object'].get_asset_class()
                        except Exception as err:
                            msg = "Could not get asset class for {} when processing message {}. Error: {}" \
                                .format(relation['related_object'], relation['message'].id, str(err))
                            logger.warning(msg=msg)
                            continue

                        # transfer attributes to new asset instance:
                        new_asset_instance.name = attachment_file_relation.asset.name
                        new_asset_instance.comment = "Harvested from email on {}. Related message id: {}" \
                            .format(timezone.now(), msg.id)
                        new_asset_instance.save()

                        content_file = ContentFile(attachment_file_relation.asset.file.read())
                        attachment_file_relation.asset.file.close()

                        new_asset_instance.file.save(attachment_file_relation.asset.file.name, content_file)
                        attachment.create_file_relation(new_asset_instance)

                        log_msg = "Created asset from email attachment for: {}, message id: {}, filename: {}" \
                            .format(relation['related_object'], relation['message'].id, new_asset_instance.name)
                        logger.info(msg=log_msg)

                        # Close the asset file
                        attachment_file_relation.asset.file.close()

                        # When the asset linking is done (ie after this loop) we need to clean up generic communications assets as they
                        # are existing on their own, not linked to projects.

        else:
            '''
            If no relations were discovered then wipe the message.
            This should only happen for Exchange server messages due to
            the face that server-side searches are disabled.
            '''
            logger.warning("Wipe disabled for message id: {} in mailbox: {}".format(msg.message_id, msg.mailbox))
            # msg.wipe()

        '''
        CLEAN up lingering CommunicationAssets
        by this point all linkages between messageattachment assets and related project should be done.
        loop over message attachments again and squanch any that are generic CommunicationAssets
        '''
        for attachment in msg.attachments.all():
            for cfr in attachment.file_relations.all():
                if isinstance(cfr.asset, CommunicationAsset):
                    cfr.asset.delete()
                    cfr.delete()


        return msg

    def __str__(self):
        return self.folder

    class Meta:
        verbose_name_plural = "Mailboxes"
        permissions = (
            ("harvest_mailbox", "Can run mailharvest on mailbox"),
        )


class Message(CommunicationTypeAbstract):
    mailbox = models.ForeignKey(
        Mailbox,
        related_name='messages',
        verbose_name=_(u'Mailbox'),
    )

    # Kept subject in Message model to make parsing for Harvest Codes slightly easier.
    # could be dropped if the parse method were refactored.
    subject = models.TextField(
        _(u'Subject'),
        max_length=1000
    )

    message_id = models.TextField(
        _(u'Message ID')
    )

    in_reply_to = models.ForeignKey(
        'communication.Message',
        related_name='replies',
        blank=True,
        null=True,
        verbose_name=_(u'In reply to'),
    )

    from_header = models.CharField(
        _('From header'),
        max_length=255,
    )

    to_header = models.TextField(
        _(u'To header'),
    )

    body = models.TextField(
        _(u'Body'),
    )

    encoded = models.BooleanField(
        _(u'Encoded'),
        default=False,
        help_text=_('True if the e-mail body is Base64 encoded'),
    )

    processed = models.DateTimeField(
        _('Processed'),
        auto_now_add=True
    )

    eml = models.FileField(
        _(u'Raw message contents'),
        blank=True,
        null=True,
        upload_to="messages",
        help_text=_(u'Original full content of message')
    )

    harvest_code_prefixes = models.ManyToManyField('HarvestCodePrefix', through='HarvestMessageRelation', related_name='harvest_code_prefixes')

    objects = models.Manager()

    @property
    def from_address(self):
        """Returns the address (as a list) from which this message was received

        .. note::

           This was once (and probably should be) a string rather than a list,
           but in a pull request received long, long ago it was changed;
           presumably to make the interface identical to that of
           `to_addresses`.

        """
        if self.from_header:
            return [parseaddr(self.from_header)[1].lower()]
        else:
            return []

    @property
    def to_addresses(self):
        """Returns a list of addresses to which this message was sent."""
        addresses = []
        for address in self.to_header.split(','):
            if address:
                addresses.append(
                    parseaddr(
                        address
                    )[1].lower()
                )
        return addresses

    # def reply(self, message):
    #     """Sends a message as a reply to this message instance.
    #
    #     Although Django's e-mail processing will set both Message-ID
    #     and Date upon generating the e-mail message, we will not be able
    #     to retrieve that information through normal channels, so we must
    #     pre-set it.
    #
    #     """
    #     if not message.from_email:
    #         if self.mailbox.from_email:
    #             message.from_email = self.mailbox.from_email
    #         else:
    #             message.from_email = django_settings.DEFAULT_FROM_EMAIL
    #     message.extra_headers['Message-ID'] = make_msgid()
    #     message.extra_headers['Date'] = formatdate()
    #     message.extra_headers['In-Reply-To'] = self.message_id.strip()
    #     message.send()
    #     return self.mailbox.record_outgoing_message(
    #         email.message_from_string(
    #             message.message().as_string()
    #         )
    #     )

    @property
    def text(self):
        """
        Returns the message body matching content type 'text/plain'.
        """
        return comm_utils.get_body_from_message(
            self.get_email_object(), 'text', 'plain'
        ).replace('=\n', '').strip()

    @property
    def html(self):
        """
        Returns the message body matching content type 'text/html'.
        """
        return comm_utils.get_body_from_message(
            self.get_email_object(), 'text', 'html'
        ).replace('\n', '').strip()

    def _rehydrate(self, msg):
        new = EmailMessage()
        settings = comm_utils.get_settings()

        if msg.is_multipart():
            for header, value in msg.items():
                new[header] = value
            for part in msg.get_payload():
                new.attach(
                    self._rehydrate(part)
                )
        elif settings['attachment_interpolation_header'] in msg.keys():
            try:
                attachment = MessageAttachment.objects.get(
                    pk=msg[settings['attachment_interpolation_header']]
                )
                for header, value in attachment.items():
                    new[header] = value
                encoding = new['Content-Transfer-Encoding']
                if encoding and encoding.lower() == 'quoted-printable':
                    # Cannot use `email.encoders.encode_quopri due to
                    # bug 14360: http://bugs.python.org/issue14360
                    output = six.BytesIO()

                    # att_file = attachment.file
                    # file_contents = att_file.read()
                    # att_file.close()

                    # I don't want it to do this very often, and who needs the attachments here anyways?
                    file_contents = ContentFile("File contents not read for optimization").read()

                    encode_quopri(
                        six.BytesIO(file_contents),
                        output,
                        quotetabs=True,
                        header=False,
                    )
                    new.set_payload(
                        output.getvalue().decode().replace(' ', '=20')
                    )
                    del new['Content-Transfer-Encoding']
                    new['Content-Transfer-Encoding'] = 'quoted-printable'
                else:
                    # att_file = attachment.file  # put in a var so the .file property doesn't loop so much.
                    # file_contents = att_file.read()
                    # att_file.close()

                    file_contents = ContentFile("File contents not read due for optimization").read()

                    new.set_payload(file_contents)
                    del new['Content-Transfer-Encoding']
                    encode_base64(new)
            except MessageAttachment.DoesNotExist:
                new[settings['altered_message_header']] = (
                    'Missing; Attachment %s not found' % (
                        msg[settings['attachment_interpolation_header']]
                    )
                )
                new.set_payload('')
        else:
            for header, value in msg.items():
                new[header] = value
            new.set_payload(
                msg.get_payload()
            )
        return new

    def get_body(self):
        """Returns the `body` field of this record.

        This will automatically base64-decode the message contents
        if they are encoded as such.

        """
        if self.encoded:
            return base64.b64decode(self.body.encode('ascii'))
        return self.body.encode('utf-8')

    def set_body(self, body):
        """Set the `body` field of this record.

        This will automatically base64-encode the message contents to
        circumvent a limitation in earlier versions of Django in which
        no fields existed for storing arbitrary bytes.

        """
        if six.PY3:
            body = body.encode('utf-8')
        self.encoded = True
        self.body = base64.b64encode(body).decode('ascii')

    def get_email_object(self):
        """Returns an `email.message.Message` instance representing the
        contents of this message and all attachments.

        See [email.Message.Message]_ for more information as to what methods
        and properties are available on `email.message.Message` instances.

        .. note::

           Depending upon the storage methods in use (specifically --
           whether ``DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE`` is set
           to ``True``, this may either create a "rehydrated" message
           using stored attachments, or read the message contents stored
           on-disk.

        .. [email.Message.Message]: Python's `email.message.Message` docs
           (https://docs.python.org/2/library/email.message.html)

        """
        if self.eml:
            self.eml.open()
            body = self.eml.file.read()
        else:
            body = self.get_body()
        if six.PY3:
            flat = email.message_from_bytes(body)
        else:
            flat = email.message_from_string(body)
        return self._rehydrate(flat)

    def wipe(self):
        """
        Deletes all fields and attachments associated with this message. Leaves message_id intact
        Allows us to keep a record of message-ids that have been downloaded without tracking every
        email that has ever been sent.
        :return:
        """
        for attachment in self.attachments.all():
            # This attachment is attached only to this message.
            attachment.delete()
        wiped_text = 'wiped'
        self.subject = wiped_text
        self.in_reply_to = None
        self.from_header = wiped_text
        self.to_header = wiped_text
        self.body = wiped_text
        self.eml.delete()

        # for field in self._meta.get_fields():
        self.save()

    def delete(self, *args, **kwargs):
        """Delete this message and all stored attachments."""
        for attachment in self.attachments.all():
            # This attachment is attached only to this message.
            attachment.delete()
        return super(Message, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('communication:message-detail', args=[str(self.id)])

    def __str__(self):
        return self.subject


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message,
        related_name='attachments',
        null=True,
        blank=True,
        verbose_name=_('Message'),
    )

    headers = models.TextField(
        _(u'Headers'),
        null=True,
        blank=True,
    )

    # files = models.Many(CommunicationFileRelation)
    file_relations = GenericRelation(CommunicationFileRelation, content_type_field='comm_type_ct', object_id_field='comm_type_oid')

    def _get_rehydrated_headers(self):
        headers = self.headers
        if headers is None:
            return EmailMessage()
        if sys.version_info < (3, 0):
            try:
                headers = headers.encode('utf-8')
            except UnicodeDecodeError as e:
                # headers = unicode(headers, 'utf-8').encode('utf-8')
                logger.error("Unicode error at MessageAttachment._get_rehydrated_headers: {}".format(str(e)))
        return email.message_from_string(headers)

    def _set_dehydrated_headers(self, email_object):
        self.headers = email_object.as_string()

    def __delitem__(self, name):
        rehydrated = self._get_rehydrated_headers()
        del rehydrated[name]
        self._set_dehydrated_headers(rehydrated)

    def __setitem__(self, name, value):
        rehydrated = self._get_rehydrated_headers()
        rehydrated[name] = value
        self._set_dehydrated_headers(rehydrated)

    def get_filename(self):
        """
        :return: original filename of this attachment.
        """
        file_name = self._get_rehydrated_headers().get_filename()
        if isinstance(file_name, six.string_types):
            result = comm_utils.convert_header_to_unicode(file_name)
            if result is None:
                return file_name
            return result
        else:
            return None

    def items(self):
        return self._get_rehydrated_headers().items()

    def __getitem__(self, name):
        value = self._get_rehydrated_headers()[name]
        if value is None:
            raise KeyError('Header %s does not exist' % name)
        return value

    def create_file_relation(self, asset):
        """
        Takes an instantiated asset class, creates a file relation instance for it, and
        saves a pointer to the file relation.
        :param asset: an instantiated asset class
        :return: communication file relation instance
        """
        cfr = CommunicationFileRelation(asset=asset, comm_type=self)
        cfr.save()
        return cfr

    def create_file_relations(self, assets):
        """
        Takes a list of  instantiated asset classes, creates file relation instances for them, and
        saves a pointer to the file relations set.
        :param assets: an instantiated asset class
        :return: communication file relation queryset
        """
        cfr_ids = []
        for asset in assets:
            cfr = self.create_file_relation(asset)
            cfr_ids.append(cfr.id)
        return CommunicationFileRelation.objects.filter(comm_type=self.message)

    @property
    def file(self):
        """
        Provides a short-cut for other mailbox code accessing the related asset's file contents (message hydration)
        This should only be used by other mailbox code that handles reading file CONTENTS. Do not use this for writing!
        Note if an asset is deleted, say on a Dev't project, then a CFR instance may not point to anything.
        :return: file contents
        """
        if self.asset is None:
            return ContentFile("File {} not found.".format(self.get_filename()))
        else:
            return self.asset.file
            # except Exception as err:
            #     msg = "Failed while trying to return file contents for message attachment id: {}: {}".format(self.id, str(err))
            #     logger.warning(msg=msg)

    @property
    def asset(self):
        """
        Return the FIRST related ASSET that doesn't throw an exception.
        :return: asset instance
        """
        # for cfr in CommunicationFileRelation.objects.filter(comm_type=self.message):
        for cfr in self.file_relations.all():
            try:
                # test if there is actually a file attached:
                cfr.asset.file.name
                return cfr.asset
            except Exception as err:
                msg = "Failed while trying to return the asset instance for message attachment id: {}: {}".format(self.id, str(err))
                logger.warning(msg=msg)

        # If we've gotten here it because we've tried to get an asset attached to this MessageAttachment but
        # there are none.
        return None
        # raise MessageAttachment.DoesNotExist

    def delete(self, using=None):
        """
        Clean up file relation before deleting.
        :param using:
        :return:
        """
        try:
            for cfr in self.file_relations.all():
                # Delete the asset:
                try:
                    cfr.asset.delete()
                except AttributeError as e:
                    msg = "MessageAttachment - self delete - tried to delete an asset in a CFR that was None." \
                          " Most likely the file was already deleted manually by a user."
                    logger.warning(msg)

                # Delete the communication File Relation record:
                cfr.delete()

        except django.db.utils.ProgrammingError as err:
            logger.error("Error in MessageAttachment.delete() method for id: {}. Error: \'{}\"".format(self.id, str(err)))
        super(MessageAttachment, self).delete(using=using)

    def __str__(self):
        return str(self.get_filename())


class HarvestCodePrefix(models.Model):
    prefix = models.CharField(
        max_length=30,
        verbose_name="Harvest Code Prefix")

    active = models.BooleanField(default=True)

    # Removed - too much to manage for now but could be useful in the future.
    # mailboxes = models.ManyToManyField(Mailbox, verbose_name="Mailboxes that will be checked for this prefix.")

    content_type = models.ForeignKey(ContentType, verbose_name="Model type that the prefix belongs to.")

    objects = ActiveObjectManager()
    admin_objects = models.Manager()

    class Meta:
        verbose_name_plural = 'Harvest code prefixes'

    def __str__(self):
        return self.prefix


class HarvestMessageRelation(models.Model):
    """
    Mailbox._process_message() calls the comm_utils.parse method which creates these relations,
    but it will be more efficient if only Comm. objects are created directly without te HMRs in the middle.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')

    message = models.ForeignKey(Message, related_name='related_message')

    harvest_code_prefix = models.ForeignKey(HarvestCodePrefix)
    harvest_code_full = models.CharField(max_length=100)

    def __str__(self):
        return "{}:{}".format(self.harvest_code_full, self.content_type)


class HarvestHistory(models.Model):
    mailbox = models.ForeignKey(Mailbox)
    last_harvest = models.DateTimeField(default=timezone.now)
    message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-last_harvest']
        verbose_name_plural = 'harvest histories'


class PhoneCall(CommunicationTypeAbstract):
    from_number = PhoneNumberField(blank=True, null=True)
    to_number = PhoneNumberField(blank=True, null=True)

    duration = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Duration of phone call in minutes.',
        help_text='The duration of the phone call in decimal minutes. 1 minute, 30 seconds should be entered as "1.5"')

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Try to get the from/to numbers first. Failing those, get numbers from contacts.
        :return:
        """
        from_num = self.from_number or ""
        to_num = self.to_number or ""
        if self.from_number is None:
            if self.communication.first() is not None:
                for contact in self.communication.first().from_contacts.all():
                    if contact.phone:
                        from_num = contact.phone
                        break
        if self.to_number is None:
            if self.communication.first() is not None:
                for contact in self.communication.first().to_contacts.all():
                    if contact.phone:
                        to_num = contact.phone
                        break
        return "from: {}, to: {}".format(from_num, to_num)

    def get_absolute_url(self):
        return reverse('communication:phonecall-detail', kwargs={'pk': self.id})


class Fax(CommunicationTypeAbstract):
    from_number = PhoneNumberField(blank=True, null=True)
    to_number = PhoneNumberField(blank=True, null=True)

    # document = models.ForeignKey(CommunicationAsset, blank=True, null=True)
    document = models.ForeignKey(CommunicationFileRelation, blank=True, null=True)
    # document = models.OneToOneField('CommunicationFileRelation', through='CommunicationFileRelation', related_name='asset')
    # harvest_code_prefixes = models.ManyToManyField('HarvestCodePrefix', through='HarvestMessageRelation', related_name='harvest_code_prefixes')

    # document_ct = models.ForeignKey(ContentType)
    # document_oid = models.PositiveIntegerField()
    # document = GenericForeignKey('document_ct', 'document_oid')

    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'faxes'

    def __str__(self):
        """
        Try to get the from/to numbers first. Failing those, get numbers from contacts.
        :return:
        """
        from_num = self.from_number or ""
        to_num = self.to_number or ""
        if self.from_number is None:
            if self.communication.first() is not None:
                for contact in self.communication.first().from_contacts.all():
                    if contact.phone:
                        from_num = contact.phone
                        break
        if self.to_number is None:
            if self.communication.first() is not None:
                for contact in self.communication.first().to_contacts.all():
                    if contact.phone:
                        to_num = contact.phone
                        break
        return "from: {}, to: {}".format(from_num, to_num)

    def get_absolute_url(self):
        return reverse('communication:fax-detail', args=[str(self.id)])


class Letter(CommunicationTypeAbstract):
    document = models.ForeignKey(CommunicationFileRelation, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return "letter. {}".format(self.document.asset.file.name)

    def get_absolute_url(self):
        return reverse('communication:letter-detail', args=[str(self.id)])


# Google GMail OAuth2 helper models
class GmailCredential(models.Model):
    mail_account = models.OneToOneField(MailAccount)
    credential = CredentialsField()

    def __str__(self):
        return "credential for {}".format(self.mail_account)
