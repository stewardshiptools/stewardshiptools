# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0011_auto_20160107_0104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='type',
            field=models.CharField(max_length=50, choices=[('image', 'Image'), ('video', 'Video'), ('audio', 'Audio'), ('document', 'Document'), ('unknown', 'Unknown')]),
        ),
    ]
