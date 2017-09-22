# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='user',
        ),
        migrations.RemoveField(
            model_name='relations',
            name='cataloger',
        ),
        migrations.RemoveField(
            model_name='relations',
            name='related_items',
        ),
        migrations.RemoveField(
            model_name='relations',
            name='reviewer',
        ),
        migrations.AddField(
            model_name='item',
            name='cataloger',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='library_item_cataloger_related'),
        ),
        migrations.AddField(
            model_name='item',
            name='related_items',
            field=models.ManyToManyField(to='library.Item', blank=True),
        ),
        migrations.AddField(
            model_name='item',
            name='reviewer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='library_item_reviewer_related'),
        ),
    ]
