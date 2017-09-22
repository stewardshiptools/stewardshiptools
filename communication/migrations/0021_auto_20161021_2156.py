# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0020_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fax',
            name='document',
            field=models.ForeignKey(null=True, blank=True, to='communication.CommunicationAsset'),
        ),
    ]
