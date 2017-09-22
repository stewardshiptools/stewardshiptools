# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0004_auto_20160127_0010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaflettilelayer',
            name='id',
        ),
        migrations.AddField(
            model_name='leaflettilelayer',
            name='leafletbaselayer_ptr',
            field=models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='maps.LeafletBaseLayer', default=0),
            preserve_default=False,
        ),
    ]
