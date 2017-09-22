# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('communication', '0007_auto_20160818_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='communication',
            name='comm_type_ct',
            field=models.ForeignKey(to='contenttypes.ContentType', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='communication',
            name='comm_type_oid',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
