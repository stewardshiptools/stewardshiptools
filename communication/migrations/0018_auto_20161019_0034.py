# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oauth2client.contrib.django_util.models
import cryptographic_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0017_auto_20161013_1759'),
    ]

    operations = [
        migrations.CreateModel(
            name='GmailCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('credential', oauth2client.contrib.django_util.models.CredentialsField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='mailaccount',
            name='password',
            field=cryptographic_fields.fields.EncryptedCharField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gmailcredential',
            name='mail_account',
            field=models.OneToOneField(to='communication.MailAccount'),
        ),
    ]
