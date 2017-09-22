# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0012_remove_mailbox_last_checked'),
    ]

    operations = [
        migrations.CreateModel(
            name='HarvestHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('last_harvest', models.DateTimeField()),
                ('message', models.TextField(null=True, blank=True)),
                ('mailbox', models.ForeignKey(to='communication.Mailbox')),
            ],
        ),
    ]
