# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import assets.asset_helpers
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0016_auto_20161212_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='secureasset',
            name='file',
            field=models.FileField(upload_to=assets.asset_helpers.generate_asset_file_name, storage=django.core.files.storage.FileSystemStorage(location='/data/django/django-cedar/media-secure', base_url=None)),
        ),
    ]
