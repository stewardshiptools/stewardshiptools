# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0001_initial'),
        ('development', '0043_developmentproject_project_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevelopmentAction',
            fields=[
                ('actionmaster_ptr', models.OneToOneField(auto_created=True, parent_link=True, to='actions.ActionMaster', serialize=False, primary_key=True)),
            ],
            bases=('actions.actionmaster',),
        ),
        migrations.CreateModel(
            name='DevelopmentProjectAction',
            fields=[
                ('developmentaction_ptr', models.OneToOneField(auto_created=True, parent_link=True, to='development.DevelopmentAction', serialize=False, primary_key=True)),
                ('project', models.ForeignKey(to='development.DevelopmentProject')),
            ],
            bases=('development.developmentaction',),
        ),
    ]
