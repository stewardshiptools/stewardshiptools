# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0019_developmentproject_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='developmentproject',
            options={'permissions': (('view_developmentproject', 'Can view development projects'),)},
        ),
    ]
