# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cryptographic_fields.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0012_auto_20160810_1310'),
        ('crm', '0013_role_description'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('rel_object_oid', models.PositiveIntegerField()),
                ('comm_oid', models.PositiveIntegerField()),
                ('comm_ct', models.ForeignKey(to='contenttypes.ContentType', related_name='comm_ct')),
                ('rel_object_ct', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='CommunicationAsset',
            fields=[
                ('secureasset_ptr',
                 models.OneToOneField(auto_created=True, to='assets.SecureAsset', serialize=False, parent_link=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.secureasset',),
        ),
        migrations.CreateModel(
            name='Fax',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('subject', models.CharField(max_length=400)),
                ('date', models.DateTimeField(verbose_name='Date & time of communication.')),
                ('from_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True)),
                ('to_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'faxes',
            },
        ),
        migrations.CreateModel(
            name='HarvestCodePrefix',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('prefix', models.CharField(max_length=30, verbose_name='Harvest Code Prefix')),
                ('active', models.BooleanField(default=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', verbose_name='Model type that the prefix belongs to.')),
            ],
        ),
        migrations.CreateModel(
            name='HarvestMessageRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('harvest_code_full', models.CharField(max_length=100)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('harvest_code_prefix', models.ForeignKey(to='communication.HarvestCodePrefix')),
            ],
        ),
        migrations.CreateModel(
            name='MailAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('email_address', models.EmailField(max_length=254, help_text='Email address for this account. May differ from username.')),
                ('username', models.CharField(max_length=100, help_text='Username required for login to the mail server.')),
                ('password', cryptographic_fields.fields.EncryptedCharField()),
                ('server_address', models.CharField(max_length=300, verbose_name='Address of the server',
                                                    help_text='Address of the mail server. Eg: www.example.com, 192.168.5.1, etc.')),
                ('protocol', models.CharField(max_length=20, help_text='If you use gmail SSL must be enabled.', default='imap',
                                              choices=[('pop3', 'pop3'), ('imap', 'imap'), ('gmail', 'imap-gmail')])),
                ('ssl', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Mailbox',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('folder_name', models.CharField(max_length=300, help_text='This is the un-url-quoted folder name', default='INBOX')),
                ('active', models.BooleanField(
                    help_text='Check this e-mail inbox for new e-mail messages during polling cycles.  This checkbox does not have an effect upon whether mail is collected here when this mailbox receives mail from a pipe, and does not affect whether e-mail messages can be dispatched from this mailbox. ',
                    default=False, verbose_name='Active')),
                ('incoming',
                 models.BooleanField(help_text="False if this is an outgoing mailbox (e.g. 'Sent Mail'), True if otherwise.", default=True,
                                     verbose_name='Is Incoming')),
                ('mail_account', models.ForeignKey(to='communication.MailAccount')),
            ],
            options={
                'verbose_name_plural': 'Mailboxes',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('subject', models.CharField(max_length=400)),
                ('date', models.DateTimeField(verbose_name='Date & time of communication.')),
                ('message_id', models.CharField(max_length=255, verbose_name='Message ID')),
                ('from_header', models.CharField(max_length=255, verbose_name='From header')),
                ('to_header', models.TextField(verbose_name='To header')),
                ('body', models.TextField(verbose_name='Body')),
                ('encoded', models.BooleanField(help_text='True if the e-mail body is Base64 encoded', default=False, verbose_name='Encoded')),
                ('processed', models.DateTimeField(auto_now_add=True, verbose_name='Processed')),
                ('eml', models.FileField(null=True, help_text='Original full content of message', blank=True, upload_to='messages',
                                         verbose_name='Raw message contents')),
                ('from_contact', models.ManyToManyField(to='crm.Person', related_name='communication_message_from_contact',
                                                        related_query_name='%(app_label)s_%(class)s')),
                ('harvest_code_prefixes', models.ManyToManyField(through='communication.HarvestMessageRelation', to='communication.HarvestCodePrefix',
                                                                 related_name='harvest_code_prefixes')),
                ('in_reply_to',
                 models.ForeignKey(to='communication.Message', null=True, blank=True, related_name='replies', verbose_name='In reply to')),
                ('mailbox', models.ForeignKey(to='communication.Mailbox', related_name='messages', verbose_name='Mailbox')),
                ('to_contact', models.ManyToManyField(to='crm.Person', related_name='communication_message_to_contact',
                                                      related_query_name='%(app_label)s_%(class)s')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PhoneCall',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('subject', models.CharField(max_length=400)),
                ('date', models.DateTimeField(verbose_name='Date & time of communication.')),
                ('from_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True)),
                ('to_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True)),
                ('duration', models.FloatField(blank=True, null=True, verbose_name='Duration of phone call in minutes.',
                                               help_text='The duration of the phone call in decimal minutes. 1 minute, 30 seconds should be entered as "1.5"')),
                ('notes', models.TextField(blank=True, null=True)),
                ('from_contact', models.ManyToManyField(to='crm.Person', related_name='communication_phonecall_from_contact',
                                                        related_query_name='%(app_label)s_%(class)s')),
                ('to_contact', models.ManyToManyField(to='crm.Person', related_name='communication_phonecall_to_contact',
                                                      related_query_name='%(app_label)s_%(class)s')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MessageAttachment',
            fields=[
                ('communicationasset_ptr',
                 models.OneToOneField(auto_created=True, to='communication.CommunicationAsset', serialize=False, parent_link=True, primary_key=True)),
                ('headers', models.TextField(blank=True, null=True, verbose_name='Headers')),
                ('message', models.ForeignKey(to='communication.Message', null=True, blank=True, related_name='attachments', verbose_name='Message')),
            ],
            options={
                'abstract': False,
            },
            bases=('communication.communicationasset',),
        ),
        migrations.AddField(
            model_name='harvestmessagerelation',
            name='message',
            field=models.ForeignKey(to='communication.Message', related_name='related_message'),
        ),
        migrations.AddField(
            model_name='harvestcodeprefix',
            name='mailboxes',
            field=models.ManyToManyField(to='communication.Mailbox', verbose_name='Mailboxes that will be checked for this prefix.'),
        ),
        migrations.AddField(
            model_name='fax',
            name='document',
            field=models.ForeignKey(to='communication.CommunicationAsset', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='fax',
            name='from_contact',
            field=models.ManyToManyField(to='crm.Person', related_name='communication_fax_from_contact',
                                         related_query_name='%(app_label)s_%(class)s'),
        ),
        migrations.AddField(
            model_name='fax',
            name='to_contact',
            field=models.ManyToManyField(to='crm.Person', related_name='communication_fax_to_contact', related_query_name='%(app_label)s_%(class)s'),
        ),
    ]
