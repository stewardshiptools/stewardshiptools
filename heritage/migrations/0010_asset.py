# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0009_auto_20160105_2326'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='')),
                ('origin_path', models.CharField(max_length=1000, null=True, blank=True)),
                ('type', models.CharField(max_length=5, choices=[('photo', 'Photo'), ('video', 'Video'), ('audio', 'Audio'), ('document', 'Document')])),
                ('session', models.ForeignKey(to='heritage.Session')),
            ],
        ),
    ]
