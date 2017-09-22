# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0006_auto_20160127_0027'),
    ]

    operations = [
        migrations.AddField(
            model_name='leafletbaselayer',
            name='machine_name',
            field=models.CharField(help_text='Must be unique and comprised of letters, numbers, dashes, and underscores', default='', max_length=100, unique=True),
            preserve_default=False,
        ),
    ]
