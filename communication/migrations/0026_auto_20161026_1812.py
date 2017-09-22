# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('communication', '0025_auto_20161026_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messageattachment',
            name='file',
        ),
        migrations.AddField(
            model_name='communicationfilerelation',
            name='comm_type_ct',
            field=models.ForeignKey(to='contenttypes.ContentType', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='communicationfilerelation',
            name='comm_type_oid',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='communicationfilerelation',
            name='asset_ct',
            field=models.ForeignKey(related_name='communicationfilerelation_ct', to='contenttypes.ContentType'),
        ),
    ]
