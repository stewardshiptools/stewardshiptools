# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0014_casebrief'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casebrief',
            name='sources',
            field=models.ManyToManyField(verbose_name='Source(s)', blank=True, to='library.Item', help_text='Select the library item(s) containing the digital version of the story cited.'),
        ),
    ]
