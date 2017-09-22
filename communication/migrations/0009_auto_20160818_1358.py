# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('communication', '0008_auto_20160818_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='communicationrelation',
            name='comm',
            field=models.ForeignKey(default=1, to='communication.Communication', related_name='related_communication'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='communicationrelation',
            name='related_object_ct',
            field=models.ForeignKey(default=1, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='communicationrelation',
            name='related_object_oid',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
