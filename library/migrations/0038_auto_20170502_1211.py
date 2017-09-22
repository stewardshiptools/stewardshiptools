# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0037_dublincore_external_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='firstnationspersonmentionedtaggeditem',
            name='note',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='personmentionedtaggeditem',
            name='note',
            field=models.TextField(null=True, blank=True),
        ),
    ]
