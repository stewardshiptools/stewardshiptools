# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        ('heritage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='species',
            name='photo',
            field=filer.fields.image.FilerImageField(null=True, to='filer.Image', blank=True, related_name='species_photo'),
        ),
    ]
