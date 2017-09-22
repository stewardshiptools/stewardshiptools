#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Model configuration in application ``communication`` for administration
console.
"""

import logging

from django.conf import settings
from django.core import urlresolvers
from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from communication.models import MessageAttachment, Message, Mailbox, MailAccount, HarvestCodePrefix, \
    HarvestMessageRelation, Communication, CommunicationRelation, Fax, PhoneCall, CommunicationAsset, \
    HarvestHistory, GmailCredential, CommunicationFileRelation

from communication.utils.comm_utils import convert_header_to_unicode
from communication.forms import MailAccountAdminForm, MailboxAdminForm

from assets.admin import SecureAssetAdmin, SecureAssetAdminInline

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def harvest_mail(mailbox_admin, request, queryset):
    '''
    calls harvest_mailbox on EITHER a MailAccount or a MailBox.
    :param mailbox_admin:
    :param request:
    :param queryset:
    :return:
    '''
    for mailobject in queryset.all():
        logger.debug('Receiving mail via admin for %s' % mailobject)
        mailobject.harvest_mail()
harvest_mail.short_description = 'Harvest mail'


def update_mailaccount_folders(mailaccount_admin, request, queryset):
    for mailaccount in queryset.all():
        logger.debug('Updating folders for %s' % mailaccount)
        mailaccount.update_folders()
update_mailaccount_folders.short_description = 'Update folders for selected mail accounts'


def set_active(admin_class, request, queryset):
    '''
    Sets "active" field to True.
    Use with any model instance that has a boolean field called "active"
    :param admin_class:
    :param request:
    :param queryset:
    :return:
    '''
    queryset.update(active=True)
set_active.short_description = 'Set selected instances to active'


def set_inactive(admin_class, request, queryset):
    '''
    Sets "active" field to False.
    Use with any model instance that has a boolean field called "active"
    :param admin_class:
    :param request:
    :param queryset:
    :return:
    '''
    queryset.update(active=False)
set_inactive.short_description = 'Set selected instances to inactive'

def wipe_message(message_admin, request, queryset):
    '''
    calls wipe on all selected messages
    :param message_admin:
    :param request:
    :param queryset:
    :return:
    '''
    for message in queryset.all():
        logger.debug('Wiping message {}'.format(message))
        message.wipe()


wipe_message.short_description = 'Wipe selected messages.'


class MailAccountAdmin(admin.ModelAdmin):
    form = MailAccountAdminForm
    actions = [harvest_mail, update_mailaccount_folders]
    list_display = (
        'username',
        'server_address',
        'protocol',
        'ssl',
        'folder_count',
        'message_count'
    )

    def folder_count(self, obj):
        return obj.mailbox_set.all().count()

    def message_count(self, obj):
        return Message.objects.filter(mailbox__in=obj.mailbox_set.all()).count()


class MailboxAdmin(admin.ModelAdmin):
    form = MailboxAdminForm
    list_display = (
        'folder',
        'uri_sani_pretty',
        'active',
        'incoming',
        'message_count'
    )
    list_filter = (
        'mail_account',
    )
    actions = [harvest_mail, set_active, set_inactive]

    def message_count(self, obj):
        return obj.messages.all().count()


class MessageAttachmentAdmin(admin.ModelAdmin):
    pass


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment

    # extra = 0
    # fields = ['name', 'secure_link']

    def has_add_permission(self, request):
        return False


class MessageAdmin(admin.ModelAdmin):
    def attachment_count(self, msg):
        return msg.attachments.count()

    def envelope_headers(self, msg):
        email = msg.get_email_object()
        return '\n'.join(
            [('%s: %s' % (h, v)) for h, v in email.items()]
        )

    def harvest_code_count(self, msg):
        return HarvestMessageRelation.objects.filter(message=msg).count()

    inlines = [
        MessageAttachmentInline,
    ]
    list_display = (
        'from_header',
        'subject',
        'attachment_count',
        'harvest_code_count',
        'mail_account',
        'mailbox_folder',
    )

    ordering = ['-processed']
    list_filter = (
        'mailbox__mail_account',
    )
    exclude = (
        'body',
    )
    # raw_id_fields = (
    #     'in_reply_to',
    # )

    readonly_fields = (
        'envelope_headers',
        'text',
        'html',
    )

    actions = [wipe_message]

    def mailbox_folder(self, obj):
        return obj.mailbox.folder

    def mail_account(self, obj):
        return obj.mailbox.mail_account


class HarvestCodePrefixAdmin(admin.ModelAdmin):
    list_display = (
        'prefix',
        'content_type',
        'active',
        # 'number_of_mailboxes_tracking',
        'number_of_instances'
    )
    ordering = ['prefix']
    list_filter = ('active',)
    actions = [set_active, set_inactive]

    def get_queryset(self, request):
        # Had to completely override the get_queryset in order to get the
        # custom model manager. lamo.
        qs = self.model.admin_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    # def number_of_mailboxes_tracking(self, obj):
    #     return obj.mailboxes.all().count()

    def number_of_instances(self, obj):
        return HarvestMessageRelation.objects.filter(harvest_code_prefix=obj).count()


class HarvestMessageRelationAdmin(admin.ModelAdmin):
    list_display = (
        'harvest_code_prefix',
        'related_object',
        'harvest_code_full',
        'mailbox_folder',
        'message_subject'
    )
    # ordering = ['message__message_id']
    list_filter = (
        'harvest_code_prefix',
        'message__mailbox__mail_account'
    )

    def message_subject(self, obj):
        return format_html(
            "<a href='{}'>{}</a>",
            urlresolvers.reverse('admin:communication_message_change', args=(obj.message.id,)), obj.message.subject)
        message_subject.allow_tags = True

    def mailbox_folder(self, obj):
        return obj.message.mailbox.folder


class CommunicationAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'subject',
        'comm_type_ct'
    )
    # list_filter = (
    #     'rel_object_ct',
    #     'comm_ct'
    # )


class CommunicationFileRelationAdmin(admin.ModelAdmin):
    list_display = ('asset',)


class CommunicationAssetAdmin(SecureAssetAdmin):
    pass


class HarvestHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'mailbox',
        'last_harvest',
        'message'
    )

    list_filter = (
        'mailbox__mail_account',
    )


class GmailCredentialsAdmin(admin.ModelAdmin):
    pass


if getattr(settings, 'DJANGO_MAILBOX_ADMIN_ENABLED', True):
    admin.site.register(Message, MessageAdmin)
    admin.site.register(MessageAttachment, MessageAttachmentAdmin)
    admin.site.register(Mailbox, MailboxAdmin)
    admin.site.register(MailAccount, MailAccountAdmin)
    admin.site.register(HarvestCodePrefix, HarvestCodePrefixAdmin)
    admin.site.register(HarvestMessageRelation, HarvestMessageRelationAdmin)
    admin.site.register(Communication, CommunicationAdmin)
    admin.site.register(CommunicationRelation)
    admin.site.register(PhoneCall)
    admin.site.register(Fax)
    admin.site.register(CommunicationAsset, CommunicationAssetAdmin)
    admin.site.register(CommunicationFileRelation, CommunicationFileRelationAdmin)
    admin.site.register(HarvestHistory, HarvestHistoryAdmin)
    admin.site.register(GmailCredential, GmailCredentialsAdmin)
