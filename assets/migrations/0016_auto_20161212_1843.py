# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import assets.asset_helpers
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0015_auto_20161105_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='secureasset',
            name='file',
            field=models.FileField(upload_to=assets.asset_helpers.generate_asset_file_name, storage=django.core.files.storage.FileSystemStorage(base_url='/media-secure', location='/data/django/django-cedar/media-secure')),
        ),
        migrations.AlterField(
            model_name='secureasset',
            name='name',
            field=models.CharField(max_length=250),
        ),
    ]
