# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0013_remove_species_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='species',
            name='photo',
            field=models.ImageField(upload_to='', default=1),
            preserve_default=False,
        ),
    ]
