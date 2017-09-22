# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('geoinfo', '0008_gislayermaster_feature_titles_template'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gislayermaster',
            name='feature_titles_template',
            field=models.CharField(null=True, max_length=200, blank=True,
                                   help_text="If you know the column headers in your attributes table you can provide a title template here.  Wrap column names in percent signs (e.g. My layer feature %ID% %poly name%) Some additional features can also be accessed by surrounding parts of the template with pound signs. Currently available is #seq# which provides the feature's place in the sequence of features being generated."),
        ),
    ]
