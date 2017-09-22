# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0005_auto_20160127_0016'),
    ]

    operations = [
        migrations.AddField(
            model_name='leafletmap',
            name='default_center_lat',
            field=models.FloatField(default=54.9),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leafletmap',
            name='default_center_lon',
            field=models.FloatField(default=-128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leafletmap',
            name='default_initial_zoom',
            field=models.PositiveSmallIntegerField(default=4),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='leafletmap',
            name='default_base_layer',
            field=models.ForeignKey(help_text='Which layer will be displayed by default? (Choose from those selected above.)', related_name='default_base_layer', to='maps.LeafletBaseLayer'),
        ),
    ]
