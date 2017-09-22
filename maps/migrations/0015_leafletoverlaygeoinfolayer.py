# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0015_auto_20160901_0023'),
        ('maps', '0014_leafletmap_other_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeafletOverlayGeoinfoLayer',
            fields=[
                ('leafletoverlaylayer_ptr', models.OneToOneField(serialize=False, parent_link=True, primary_key=True, auto_created=True, to='maps.LeafletOverlayLayer')),
                ('geoinfo_layer', models.ForeignKey(to='geoinfo.GISLayerMaster')),
            ],
            options={
                'abstract': False,
            },
            bases=('maps.leafletoverlaylayer',),
        ),
    ]
