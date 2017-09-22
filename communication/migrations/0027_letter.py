# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0026_auto_20161026_1812'),
    ]

    operations = [
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('document', models.ForeignKey(null=True, to='communication.CommunicationFileRelation', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
