# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0028_auto_20161215_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communication',
            name='subject',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='message',
            name='message_id',
            field=models.TextField(verbose_name='Message ID'),
        ),
        migrations.AlterField(
            model_name='message',
            name='subject',
            field=models.TextField(verbose_name='Subject', max_length=1000),
        ),
    ]
