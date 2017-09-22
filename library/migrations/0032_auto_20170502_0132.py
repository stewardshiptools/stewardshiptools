# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0031_review_places_mentioned'),
    ]

    operations = [
        migrations.AddField(
            model_name='casebrief',
            name='uuid',
            field=models.UUIDField(editable=False, default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='item',
            name='uuid',
            field=models.UUIDField(editable=False, default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='synthesis',
            name='uuid',
            field=models.UUIDField(editable=False, default=uuid.uuid4),
        ),
    ]
