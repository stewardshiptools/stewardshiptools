# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0044_auto_20170510_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='synthesisitem',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.SynthesisCategory'),
        ),
    ]
