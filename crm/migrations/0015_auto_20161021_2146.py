# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cedar.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0014_auto_20160824_1512'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alternatename',
            options={'ordering': ('id',)},
        ),
        migrations.AlterField(
            model_name='person',
            name='indigenous_name',
            field=cedar.fields.StrippedCharField(blank=True, max_length=100, null=True, verbose_name='Indigenous name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='mentor_name',
            field=cedar.fields.StrippedCharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='name_first',
            field=cedar.fields.StrippedCharField(max_length=100, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='name_last',
            field=cedar.fields.StrippedCharField(max_length=100, verbose_name='Last Name'),
        ),
    ]
