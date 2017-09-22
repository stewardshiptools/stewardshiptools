# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0007_auto_20160525_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='feature_titles_template',
            field=models.CharField(help_text='If you know the column headers in your attributes table youcan provide a title template here.  Wrap column names inpercent signs (e.g. My layer feature %ID% %poly name%)', null=True, blank=True, max_length=200),
        ),
    ]
