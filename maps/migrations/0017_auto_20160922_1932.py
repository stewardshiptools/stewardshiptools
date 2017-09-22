# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0016_remove_leafletmap_overlay_layers'),
    ]

    operations = [
        migrations.AddField(
            model_name='leafletmap',
            name='available_overlay_layers',
            field=models.ManyToManyField(to='maps.LeafletOverlayLayer', help_text='Choose the overlay layers that will be available (Displayed in the selector.)', related_name='available_overlay_layers', blank=True),
        ),
        migrations.AddField(
            model_name='leafletmap',
            name='visible_overlay_layers',
            field=models.ManyToManyField(to='maps.LeafletOverlayLayer', help_text='Choose the overlay layers that will be displayed (Choose from those selected above.)', related_name='visible_overlay_layers', blank=True),
        ),
    ]
