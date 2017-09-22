# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0014_auto_20161105_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadocumentasset',
            name='contributor',
            field=models.TextField(verbose_name='Contributors', help_text='An entity responsible for making contributions to the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='coverage',
            field=models.TextField(verbose_name='Coverage', help_text='The spatial or temporal topic of the resource, the spatial applicability                            of the resource, or the jurisdiction under which the resource is relevant.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='creator',
            field=models.TextField(verbose_name='Creators', help_text='An entity primarily responsible for making the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='date',
            field=models.DateField(verbose_name='Date', help_text='A point or period of time associated with an event in the lifecycle of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='description',
            field=models.TextField(verbose_name='Description', help_text='An account of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='format',
            field=models.TextField(verbose_name='Format', help_text='The file format, physical medium, or dimensions of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='identifier',
            field=models.TextField(verbose_name='Identifier', help_text='An unambiguous reference to the resource within a given context.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='language',
            field=models.TextField(verbose_name='Language', help_text='A language of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='publisher',
            field=models.TextField(verbose_name='Publishers', help_text='An entity responsible for making the resource available.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='relation',
            field=models.TextField(verbose_name='Relation', help_text='A related resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='rights',
            field=models.TextField(verbose_name='Rights', help_text='Information about rights held in and over the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='source',
            field=models.TextField(verbose_name='Source', help_text='A related resource from which the described resource is derived.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='subject',
            field=models.TextField(verbose_name='Subject', help_text='The topic of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='title',
            field=models.TextField(verbose_name='Title', help_text='A name given to the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentasset',
            name='type',
            field=models.TextField(verbose_name='Type', help_text='The nature or genre of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='contributor',
            field=models.TextField(verbose_name='Contributors', help_text='An entity responsible for making contributions to the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='coverage',
            field=models.TextField(verbose_name='Coverage', help_text='The spatial or temporal topic of the resource, the spatial applicability                            of the resource, or the jurisdiction under which the resource is relevant.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='creator',
            field=models.TextField(verbose_name='Creators', help_text='An entity primarily responsible for making the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='date',
            field=models.DateField(verbose_name='Date', help_text='A point or period of time associated with an event in the lifecycle of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='description',
            field=models.TextField(verbose_name='Description', help_text='An account of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='format',
            field=models.TextField(verbose_name='Format', help_text='The file format, physical medium, or dimensions of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='identifier',
            field=models.TextField(verbose_name='Identifier', help_text='An unambiguous reference to the resource within a given context.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='language',
            field=models.TextField(verbose_name='Language', help_text='A language of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='publisher',
            field=models.TextField(verbose_name='Publishers', help_text='An entity responsible for making the resource available.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='relation',
            field=models.TextField(verbose_name='Relation', help_text='A related resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='rights',
            field=models.TextField(verbose_name='Rights', help_text='Information about rights held in and over the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='source',
            field=models.TextField(verbose_name='Source', help_text='A related resource from which the described resource is derived.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='subject',
            field=models.TextField(verbose_name='Subject', help_text='The topic of the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='title',
            field=models.TextField(verbose_name='Title', help_text='A name given to the resource.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='type',
            field=models.TextField(verbose_name='Type', help_text='The nature or genre of the resource.', null=True, blank=True),
        ),
    ]
