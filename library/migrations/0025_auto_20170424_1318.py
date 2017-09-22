# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0024_remove_itemtype_belongs_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='casebrief',
            name='belongs_to',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='App that this object belongs to'),
        ),
        migrations.AddField(
            model_name='casebrieftag',
            name='belongs_to',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='App that this object belongs to'),
        ),
        migrations.AddField(
            model_name='collectiontag',
            name='belongs_to',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='App that this object belongs to'),
        ),
        migrations.AddField(
            model_name='dublincore',
            name='belongs_to',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='App that this object belongs to'),
        ),
        migrations.AddField(
            model_name='holdings',
            name='belongs_to',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='App that this object belongs to'),
        ),
        migrations.AddField(
            model_name='researchernotes',
            name='belongs_to',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='App that this object belongs to'),
        ),
        migrations.AddField(
            model_name='synthesis',
            name='belongs_to',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='App that this object belongs to'),
        ),
        migrations.AddField(
            model_name='synthesisitem',
            name='belongs_to',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='App that this object belongs to'),
        ),
    ]
