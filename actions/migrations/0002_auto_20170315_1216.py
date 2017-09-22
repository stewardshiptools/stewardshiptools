# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import actions.models


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionmaster',
            name='date',
            field=models.DateTimeField(default=actions.models.get_default_date_time),
        ),
    ]
