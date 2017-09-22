# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0007_leafletbaselayer_machine_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leafletbaselayer',
            name='name',
            field=models.CharField(max_length=100, help_text='The name that will be shown to the user in layers switches, etc.'),
        ),
    ]
