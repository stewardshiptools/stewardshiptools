# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0039_auto_20170504_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='synthesisitem',
            name='uuid',
            field=models.UUIDField(editable=False, default=uuid.uuid4),
        ),
    ]
