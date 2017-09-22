# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0015_leafletoverlaygeoinfolayer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leafletmap',
            name='overlay_layers',
        ),
    ]
