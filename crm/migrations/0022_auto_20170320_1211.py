# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0021_auto_20170110_1159'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='person',
            name='pic',
            field=models.ImageField(blank=True, verbose_name='Profile photo', upload_to=''),
        ),
    ]
