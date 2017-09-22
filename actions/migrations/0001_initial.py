# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionMaster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=250)),
                ('date', models.DateTimeField()),
                ('send_reminder', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('actionmaster_ptr', models.OneToOneField(serialize=False, parent_link=True, auto_created=True, to='actions.ActionMaster', primary_key=True)),
            ],
            bases=('actions.actionmaster',),
        ),
        migrations.AddField(
            model_name='actionmaster',
            name='assignee',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, related_name='assigned_actions', null=True),
        ),
        migrations.AddField(
            model_name='actionmaster',
            name='subscribers',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, related_name='subscribed_actions'),
        ),
    ]
