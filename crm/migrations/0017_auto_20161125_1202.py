# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cedar.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0016_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='clan_family',
            field=cedar.fields.StrippedCharField(verbose_name='Clan/Family', max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='initials',
            field=cedar.fields.StrippedCharField(verbose_name='Initials', null=True, blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='person',
            name='mentor_relationship',
            field=cedar.fields.StrippedCharField(null=True, blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='person',
            name='name_suffix',
            field=cedar.fields.StrippedCharField(verbose_name='Suffix', null=True, blank=True, max_length=10),
        ),
    ]
