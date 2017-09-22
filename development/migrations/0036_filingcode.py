# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0035_developmentproject_misc_textareas'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilingCode',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(unique=True, max_length=200)),
                ('label', models.CharField(unique=True, max_length=200)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(null=True, blank=True, related_name='children', to='development.FilingCode')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
