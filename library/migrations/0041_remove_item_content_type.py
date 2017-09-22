# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0040_synthesisitem_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='content_type',
        ),
    ]
