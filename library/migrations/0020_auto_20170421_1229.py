# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0019_synthesis_synthesiscategory_synthesisitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='synthesis',
            options={'verbose_name_plural': 'Syntheses'},
        ),
        migrations.AlterField(
            model_name='synthesisitem',
            name='casebriefs',
            field=models.ManyToManyField(to='library.CaseBrief', verbose_name='Case Brief Sources', blank=True),
        ),
        migrations.AlterField(
            model_name='synthesisitem',
            name='items',
            field=models.ManyToManyField(to='library.Item', verbose_name='Item Sources', blank=True),
        ),
    ]
