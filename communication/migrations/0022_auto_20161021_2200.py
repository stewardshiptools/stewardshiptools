# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0021_auto_20161021_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fax',
            name='document',
            field=models.ForeignKey(to='communication.CommunicationFileRelation', blank=True, null=True),
        ),
    ]
