# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0018_casebrief_keywords'),
    ]

    operations = [
        migrations.CreateModel(
            name='Synthesis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created', model_utils.fields.AutoCreatedField(editable=False, verbose_name='created', default=django.utils.timezone.now)),
                ('modified', model_utils.fields.AutoLastModifiedField(editable=False, verbose_name='modified', default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=500)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SynthesisCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=500)),
                ('weight', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SynthesisItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created', model_utils.fields.AutoCreatedField(editable=False, verbose_name='created', default=django.utils.timezone.now)),
                ('modified', model_utils.fields.AutoLastModifiedField(editable=False, verbose_name='modified', default=django.utils.timezone.now)),
                ('subject', models.CharField(max_length=500)),
                ('overview', models.TextField(blank=True, null=True)),
                ('casebriefs', models.ManyToManyField(to='library.CaseBrief', verbose_name='Case Brief Sources')),
                ('category', models.ForeignKey(to='library.SynthesisCategory', on_delete=django.db.models.deletion.PROTECT)),
                ('items', models.ManyToManyField(to='library.Item', verbose_name='Item Sources')),
                ('synthesis', models.ForeignKey(to='library.Synthesis')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
