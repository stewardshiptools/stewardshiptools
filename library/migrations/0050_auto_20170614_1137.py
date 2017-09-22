# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0049_auto_20170515_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dublincore',
            name='creator',
            field=models.TextField(null=True, blank=True, verbose_name='Author/Creator',
                                   help_text='An entity primarily responsible for making the resource. Format: Last Name, First Name - Title;'),
        ),
    ]
