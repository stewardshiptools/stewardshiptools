# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0012_auto_20160810_1310'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaDocumentAsset',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('contributor', models.TextField(help_text='An entity responsible for making contributions to the resource.', verbose_name='Contributors', blank=True)),
                ('coverage', models.TextField(help_text='The spatial or temporal topic of the resource, the spatial applicability                            of the resource, or the jurisdiction under which the resource is relevant.', verbose_name='Coverage', blank=True)),
                ('creator', models.TextField(help_text='An entity primarily responsible for making the resource.', verbose_name='Creators', blank=True)),
                ('date', models.DateField(help_text='A point or period of time associated with an event in the lifecycle of the resource.', verbose_name='Date', blank=True)),
                ('description', models.TextField(help_text='An account of the resource.', verbose_name='Description', blank=True)),
                ('format', models.TextField(help_text='The file format, physical medium, or dimensions of the resource.', verbose_name='Format', blank=True)),
                ('identifier', models.TextField(help_text='An unambiguous reference to the resource within a given context.', verbose_name='Identifier', blank=True)),
                ('language', models.TextField(help_text='A language of the resource.', verbose_name='Language', blank=True)),
                ('publisher', models.TextField(help_text='An entity responsible for making the resource available.', verbose_name='Publishers', blank=True)),
                ('relation', models.TextField(help_text='A related resource.', verbose_name='Relation', blank=True)),
                ('rights', models.TextField(help_text='Information about rights held in and over the resource.', verbose_name='Rights', blank=True)),
                ('source', models.TextField(help_text='A related resource from which the described resource is derived.', verbose_name='Source', blank=True)),
                ('subject', models.TextField(help_text='The topic of the resource.', verbose_name='Subject', blank=True)),
                ('title', models.TextField(help_text='A name given to the resource.', verbose_name='Title', blank=True)),
                ('type', models.TextField(help_text='The nature or genre of the resource.', verbose_name='Type', blank=True)),
                ('asset', models.OneToOneField(to='assets.Asset')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MetaDocumentSecureAsset',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('contributor', models.TextField(help_text='An entity responsible for making contributions to the resource.', verbose_name='Contributors', blank=True)),
                ('coverage', models.TextField(help_text='The spatial or temporal topic of the resource, the spatial applicability                            of the resource, or the jurisdiction under which the resource is relevant.', verbose_name='Coverage', blank=True)),
                ('creator', models.TextField(help_text='An entity primarily responsible for making the resource.', verbose_name='Creators', blank=True)),
                ('date', models.DateField(help_text='A point or period of time associated with an event in the lifecycle of the resource.', verbose_name='Date', blank=True)),
                ('description', models.TextField(help_text='An account of the resource.', verbose_name='Description', blank=True)),
                ('format', models.TextField(help_text='The file format, physical medium, or dimensions of the resource.', verbose_name='Format', blank=True)),
                ('identifier', models.TextField(help_text='An unambiguous reference to the resource within a given context.', verbose_name='Identifier', blank=True)),
                ('language', models.TextField(help_text='A language of the resource.', verbose_name='Language', blank=True)),
                ('publisher', models.TextField(help_text='An entity responsible for making the resource available.', verbose_name='Publishers', blank=True)),
                ('relation', models.TextField(help_text='A related resource.', verbose_name='Relation', blank=True)),
                ('rights', models.TextField(help_text='Information about rights held in and over the resource.', verbose_name='Rights', blank=True)),
                ('source', models.TextField(help_text='A related resource from which the described resource is derived.', verbose_name='Source', blank=True)),
                ('subject', models.TextField(help_text='The topic of the resource.', verbose_name='Subject', blank=True)),
                ('title', models.TextField(help_text='A name given to the resource.', verbose_name='Title', blank=True)),
                ('type', models.TextField(help_text='The nature or genre of the resource.', verbose_name='Type', blank=True)),
                ('asset', models.OneToOneField(to='assets.SecureAsset')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
