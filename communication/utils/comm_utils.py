import datetime
import email.header
import logging
import os
import re
import six

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Q

import communication  # I was running into circular import problems.
from cedar_settings.models import GeneralSetting

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_settings():
    return {
        'strip_unallowed_mimetypes': getattr(
            settings,
            'DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES',
            False
        ),
        'allowed_mimetypes': getattr(
            settings,
            'DJANGO_MAILBOX_ALLOWED_MIMETYPES',
            [
                'text/plain',
                'text/html'
            ]
        ),
        'text_stored_mimetypes': getattr(
            settings,
            'DJANGO_MAILBOX_TEXT_STORED_MIMETYPES',
            [
                'text/plain',
                'text/html'
            ]
        ),
        'altered_message_header': getattr(
            settings,
            'DJANGO_MAILBOX_ALTERED_MESSAGE_HEADER',
            'X-Django-Mailbox-Altered-Message'
        ),
        'attachment_interpolation_header': getattr(
            settings,
            'DJANGO_MAILBOX_ATTACHMENT_INTERPOLATION_HEADER',
            'X-Django-Mailbox-Interpolate-Attachment'
        ),
        'attachment_upload_to': getattr(
            settings,
            'DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO',
            'mailbox_attachments/%Y/%m/%d/'
        ),
        'store_original_message': getattr(
            settings,
            'DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE',
            False
        ),
        'default_charset': getattr(
            settings,
            'DJANGO_MAILBOX_default_charset',
            'iso8859-1',
        )
    }


def convert_header_to_unicode(header):
    default_charset = get_settings()['default_charset']

    if six.PY2 and isinstance(header, six.text_type):
        return header

    def _decode(value, encoding):
        if isinstance(value, six.text_type):
            return value
        if not encoding or encoding == 'unknown-8bit':
            encoding = default_charset
        return value.decode(encoding, 'replace')

    try:
        return ''.join(
            [
                (
                    _decode(bytestr, encoding)
                ) for bytestr, encoding in email.header.decode_header(header)
                ]
        )
    except UnicodeDecodeError:
        logger.exception(
            'Errors encountered decoding header %s into encoding %s.',
            header,
            default_charset,
        )
        return unicode(header, default_charset, 'replace')


def get_body_from_message(message, maintype, subtype):
    """
    Fetchs the body message matching main/sub content type.
    """
    body = six.text_type('')
    for part in message.walk():
        if part.get_content_maintype() == maintype and \
                        part.get_content_subtype() == subtype:
            charset = part.get_content_charset()
            this_part = part.get_payload(decode=True)
            if charset:
                try:
                    this_part = this_part.decode(charset, 'replace')
                except LookupError:
                    this_part = this_part.decode('ascii', 'replace')
                    logger.warning(
                        'Unknown encoding %s encountered while decoding '
                        'text payload.  Interpreting as ASCII with '
                        'replacement, but some data may not be '
                        'represented as the sender intended.',
                        charset
                    )
                except ValueError:
                    this_part = this_part.decode('ascii', 'replace')
                    logger.warning(
                        'Error encountered while decoding text '
                        'payload from an incorrectly-constructed '
                        'e-mail; payload was converted to ASCII with '
                        'replacement, but some data may not be '
                        'represented as the sender intended.'
                    )
            else:
                this_part = this_part.decode('ascii', 'replace')

            body += this_part

    return body


def get_attachment_save_path(instance, filename):
    settings = get_settings()

    path = settings['attachment_upload_to']
    if '%' in path:
        path = datetime.datetime.utcnow().strftime(path)

    return os.path.join(
        path,
        filename,
    )


def harvest_codes_to_regex_pattern(harvest_prefix_list):
    pattern_template = '{prefix}[0-9]+'
    return '|'.join(
        pattern_template.format(prefix=pre) for pre in harvest_prefix_list
    )


def harvest_mailboxes(mailbox_qs):
    '''
    Called by MailAccount, Mailbox, in Admin pages, and in the communication manage.py command.
    Calls harvest_mailbox on each supplied mailbox in the queryset.
    :param mailbox_qs: queryset of mailboxes that should be harvested.
    :return:
    '''
    for mailbox in mailbox_qs:
        logger.info('Pulling mail for account:{account}, id:{account_id}, mailbox:{mailbox}, id:{mailbox_id}'.format(
            account=mailbox.mail_account,
            account_id=mailbox.mail_account.id,
            mailbox=mailbox.folder,
            mailbox_id=mailbox.id
        ))

        messages = harvest_mailbox(mailbox)
        for message in messages:
            logger.info('Received message-id:{}. From {}'.format(message.message_id, message.from_address))


def harvest_mail_account_status(mail_account):
    """ Helper function to report whether a mail account is currently being harvested, has never been harvested, or
    the last date it was harvested.

    :param mail_account: A MailAccount model instance.
    :return: 0 for never harvested, 1 for in progress, or a datetime object referring the the last harvest time.
    """
    status = 0
    mailboxes = mail_account.mailbox_set.filter(active=True)

    found_date = False
    for mailbox in mailboxes:
        result = harvest_mailbox_status(mailbox)

        # If we even find one mailbox currently being harvested, that counts as the account being harvested.
        if not found_date and result == 1:
            return 1

        if isinstance(result, datetime.datetime):
            found_date = True

            # If status isn't 0 then it should be a datetime object, so this is okay, yes?
            if status == 0 or result > status:
                status = result

    return status


def harvest_mailbox_status(mailbox):
    """
    Helper function to report whether a mailbox is currently being harvested, has never been harvested, or the last
    date it was harvested.

    :param mailbox: A MailBox model instance
    :return: 0 for never harvested, 1 for in progress, or a datetime object referring the the last harvest time.
    """
    if cache.get('mailbox_is_harvesting_%d' % mailbox.id, False):
        return 1

    # If we've made it this far either the mailbox has never been harvested (default 0) or we can return whatever date
    # this is assuming it's the last harvest date.
    return cache.get("date_mailbox_harvested_%d" % mailbox.id, 0)


def harvest_mailbox(mailbox):
    """
    Connect to the mailbox and fetch new messages. This probably needs to be moved into the model as a class method.
    :param mailbox:
    :return: list of new Message instances.
    """
    new_mail = []

    # Get the lookback date that will used in mail server queries:
    lookback_date = timezone.now() - datetime.timedelta(hours=GeneralSetting.objects.get('communication__mailharvest_lookback_hours'))

    # Make pre-search message queryset -- prevents downloading of duplicated messsages.
    # Use double the lookback date to filter the messages and reduce the number db and server hits in .get_message()
    double_lookback_date = timezone.now() - datetime.timedelta(hours=2 * GeneralSetting.objects.get('communication__mailharvest_lookback_hours'))
    existing_messages_qs = mailbox.messages.filter(Q(communication__date__gte=double_lookback_date)|Q(communication__isnull=True))

    logger.info("message for pre-filtering email download count: {}, lookback date: {}".format(existing_messages_qs.count(), double_lookback_date))

    # get set of all active harvest code prefixes (used to do only those associated with current mailbox):
    search_string_list = communication.models.HarvestCodePrefix.objects.all().values_list('prefix', flat=True)

    # check that prefixes have been assigned to this mailbox:
    if search_string_list.count() == 0:
        logger.warn("No active prefixes were returned. Discontinuing mail pull.")
        return new_mail

    connection = mailbox.get_connection()
    if not connection:
        return new_mail

    for message in connection.get_message(
            existing_messages_qs=existing_messages_qs,
            search_list=search_string_list,
            lookback_date=double_lookback_date):

        msg = mailbox._process_message(message)
        new_mail.append(msg)

    communication.models.HarvestHistory.objects.create(
        mailbox=mailbox
    )

    return new_mail


def parse_message_for_harvest_codes(harvest_prefixes, message):
    '''
    Deprecated: parse message and create HarvestRelation instances.
    Instead use parse_message_for_entity_relations() which will determine
    what should be related and return a list of dicts that can be used to
    create the relations.
    :param harvest_prefixes:
    :param message:
    :return:
    '''
    # make the string regex pattern for the qs of harvest prefixes:
    harvest_prefix_regex_pattern = harvest_codes_to_regex_pattern(harvest_prefixes.values_list('prefix', flat=True))

    found_harvest_codes = []

    # Search message body:
    found_harvest_codes.extend(re.findall(harvest_prefix_regex_pattern, str(message.text)))

    # Search message subject:
    found_harvest_codes.extend(re.findall(harvest_prefix_regex_pattern, str(message.subject)))

    # Eliminate dupes:
    found_harvest_codes = set(found_harvest_codes)

    created = 0

    if found_harvest_codes:
        for h_prefix in harvest_prefixes:
            matched_codes = [code for code in found_harvest_codes if h_prefix.prefix in code]
            for code in matched_codes:
                try:
                    logger.info(msg="Linking harvest code {} for email: {}".format(code, message.message_id))

                    object_id = int(code.replace(h_prefix.prefix, ''))
                    related_obj = h_prefix.content_type.get_object_for_this_type(id=object_id)

                    communication.models.HarvestMessageRelation.objects.create(
                        related_object=related_obj,
                        message=message,
                        harvest_code_prefix=h_prefix,
                        harvest_code_full=code
                    )
                    created += 1

                except ValueError as e:
                    # We actually will never get here because the regex should always filter these out.
                    logger.error(msg='Value error when parsing discovered '
                                     'harvest mail code:{}. Prefix:{}'.format(code, h_prefix.prefix))
                except ObjectDoesNotExist:
                    logger.error(msg='ObjectDoesNotExist error for the related object when '
                                     'parsing discovered harvest mail code:{}. Prefix:{}'.format(code, h_prefix.prefix))

                    # if created > 0:
                    #     logger.debug(
                    #         msg="{} harvest code relations created for message id:{} in mailbox folder: {}"
                    #         .format(created, message.message_id, message.mailbox.folder_name)
                    #     )
    return created


def parse_message_for_entity_relations(harvest_prefixes, message):
    # make the string regex pattern for the qs of harvest prefixes:
    harvest_prefix_regex_pattern = harvest_codes_to_regex_pattern(harvest_prefixes.values_list('prefix', flat=True))

    found_harvest_codes = []

    # Search message body:
    found_harvest_codes.extend(re.findall(harvest_prefix_regex_pattern, str(message.text)))

    # Search message subject:
    found_harvest_codes.extend(re.findall(harvest_prefix_regex_pattern, str(message.subject)))

    # Eliminate dupes:
    found_harvest_codes = set(found_harvest_codes)

    relations = []

    if found_harvest_codes:
        for h_prefix in harvest_prefixes:
            matched_codes = [code for code in found_harvest_codes if h_prefix.prefix in code]
            for code in matched_codes:
                try:
                    logger.info(msg="Discovering harvest code {} for email: {}".format(code, message.message_id))

                    object_id = int(code.replace(h_prefix.prefix, ''))
                    related_obj = h_prefix.content_type.get_object_for_this_type(id=object_id)

                    relations.append({
                        'related_object': related_obj,
                        'message': message,
                        'harvest_code_prefix': h_prefix,
                        'harvest_code_full': code
                    })

                except ValueError as e:
                    # We actually will never get here because the regex should always filter these out.
                    logger.error(msg='Value error when parsing discovered '
                                     'harvest mail code:{}. Prefix:{}'.format(code, h_prefix.prefix))
                except ObjectDoesNotExist:
                    logger.error(msg='ObjectDoesNotExist error for the related object when '
                                     'parsing discovered harvest mail code:{}. Prefix:{}. Message-id:{}'
                                 .format(code, h_prefix.prefix, message.message_id))

    return relations


def communications_stats():
    '''
    Makes a dict of statistics for use in the communications dashboard
    :return: dict of stats
    '''
    stats = {}
    stats['message_count'] = communication.models.Message.objects.all().count()
    stats['messages_linked_to_projects_count'] = communication.models.HarvestMessageRelation.objects.all().count()
    stats['active_mailbox_count'] = communication.models.Mailbox.objects.all().count()
    stats['mail_account_count'] = communication.models.MailAccount.objects.all().count()
    stats['activate_prefix_count'] = communication.models.HarvestCodePrefix.objects.all().count()
    stats['phonecall_count'] = communication.models.PhoneCall.objects.all().count()
    stats['fax_count'] = communication.models.Fax.objects.all().count()

    return stats


def get_google_oauth2_private_redirect_url(request=None):
    '''
    Helper for doing gmail account stuff on a local (ie non-public ip) machine.
    :param request:
    :return:
    '''
    if settings.GOOGLE_OAUTH2_PRIVATE_REDIRECT_URL_OVERRIDE is None:
        return request.build_absolute_uri(reverse("communication:authorize_gmail"))
    else:
        return settings.GOOGLE_OAUTH2_PRIVATE_REDIRECT_URL_OVERRIDE