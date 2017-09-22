# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0020_auto_20170421_1229'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='synthesiscategory',
            options={'verbose_name_plural': 'Synthesis Categories'},
        ),
        migrations.AlterModelOptions(
            name='synthesisitem',
            options={'ordering': ('id',)},
        ),
        migrations.RemoveField(
            model_name='item',
            name='object_id',
        ),
        migrations.AddField(
            model_name='itemtype',
            name='belongs_to',
            field=models.CharField(null=True, verbose_name='App that this object belongs to', max_length=100),
        ),
    ]
