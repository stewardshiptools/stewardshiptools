# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0010_auto_20160819_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailbox',
            name='last_checked',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mailaccount',
            name='protocol',
            field=models.CharField(choices=[('pop3', 'pop3'), ('imap', 'imap'), ('imap-exchange', 'imap-exchange'), ('gmail', 'imap-gmail')], max_length=20, help_text='If you use gmail SSL must be enabled.', default='imap'),
        ),
    ]
