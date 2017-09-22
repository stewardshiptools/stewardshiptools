# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0066_layergroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='heritagegislayer',
            name='group',
            field=models.ForeignKey(default='', to='heritage.LayerGroup'),
            preserve_default=False,
        ),
    ]
