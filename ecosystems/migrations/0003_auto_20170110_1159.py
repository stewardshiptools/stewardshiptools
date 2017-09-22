# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields
import django_hstore.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0021_auto_20170110_1159'),
        ('ecosystems', '0002_ecosystemsgislayer'),
    ]

    operations = [
        migrations.CreateModel(
            name='EcosystemsProject',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('cedar_project_name', models.CharField(max_length=250)),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Project Start Date', help_text='Date on which first contact was made.')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Project End Date', help_text='Date on which first contact was made.')),
                ('status', models.CharField(default='active', max_length=30, choices=[('active', 'Active'), ('inactive', 'Inactive')], verbose_name='Project status')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description', help_text='Short description of project/permit.')),
                ('misc_textareas', django_hstore.fields.DictionaryField(blank=True, null=True)),
                ('extra_info', django_hstore.fields.DictionaryField(blank=True, null=True)),
                ('author', models.ForeignKey(related_name='author', on_delete=django.db.models.deletion.PROTECT, to='crm.Person', verbose_name='Author')),
                ('contacts', models.ManyToManyField(blank=True, related_name='contacts', to='crm.Person', verbose_name='Contacts')),
            ],
            options={
                'permissions': (('view_ecosystemsproject', 'Can view ecosystems projects'),),
            },
        ),
        migrations.CreateModel(
            name='EcosystemsProjectAsset',
            fields=[
                ('ecosystemsasset_ptr', models.OneToOneField(auto_created=True, to='ecosystems.EcosystemsAsset', parent_link=True, primary_key=True, serialize=False)),
                ('project', models.ForeignKey(to='ecosystems.EcosystemsProject')),
            ],
            options={
                'abstract': False,
            },
            bases=('ecosystems.ecosystemsasset',),
        ),
        migrations.CreateModel(
            name='FilingCode',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=200, unique=True)),
                ('label', models.CharField(max_length=200, unique=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, related_name='children', null=True, to='ecosystems.FilingCode')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectTag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=30, verbose_name='Tag text')),
            ],
        ),
        migrations.AddField(
            model_name='ecosystemsproject',
            name='filing_code',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, to='ecosystems.FilingCode'),
        ),
        migrations.AddField(
            model_name='ecosystemsproject',
            name='tags',
            field=models.ManyToManyField(blank=True, to='ecosystems.ProjectTag'),
        ),
    ]
