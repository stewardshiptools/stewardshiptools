# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0008_auto_20160127_0108'),
    ]

    operations = [
        migrations.AddField(
            model_name='leafletmap',
            name='machine_name',
            field=models.CharField(max_length=100, help_text='Must be unique and comprised of letters, numbers, dashes, and underscores', unique=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='leafletmap',
            name='name',
            field=models.CharField(max_length=100, help_text='The name that will be shown to users.'),
        ),
    ]
