# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0020_auto_20170621_1313'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stylecircle',
            old_name='leaflet_layer_type',
            new_name='layer_type',
        ),
    ]
