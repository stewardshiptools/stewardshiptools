# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0010_auto_20160129_0503'),
    ]

    operations = [
        migrations.AddField(
            model_name='leafletmap',
            name='layer_control_collapsed',
            field=models.BooleanField(default=False),
        ),
    ]
