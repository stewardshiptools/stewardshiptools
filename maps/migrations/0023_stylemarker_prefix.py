# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0022_compositestyle_style_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stylemarker',
            name='prefix',
            field=models.CharField(default='fa', max_length=20,
                                   help_text="Icon library set prefix. 'fa' for font-awesome or 'glyphicon' for bootstrap 3."),
        ),
    ]
