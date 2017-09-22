# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0010_remove_dublincore_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confidentiality',
            name='confidential',
            field=models.BooleanField(default=True, verbose_name='Confidential'),
        ),
        migrations.AlterField(
            model_name='dublincore',
            name='creator',
            field=models.TextField(verbose_name='Author/Creator', null=True, blank=True, help_text='An entity primarily responsible for making the resource.'),
        ),
    ]
