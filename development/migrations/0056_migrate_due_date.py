# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.db import migrations, models
from django.utils import timezone

from development.models import DevelopmentProject, DevelopmentProjectAction

# Forward
def developmentProjectActionsToField(apps, schema_editor):
    # Fetch all the Due date development project actions from the database.
    actions = DevelopmentProjectAction.objects.filter(label="Due date")

    # Move the Due date value from action to project.
    for action in actions:
        obj = action.project
        obj.due_date = action.date
        obj.save()

    # Delete all the development project actions
    actions.delete()


def fieldToDevelopmentProjectActions(apps, schema_editor):
    # Fetch all DevelopmentProject instances
    projects = DevelopmentProject.objects.filter(due_date__isnull=False)

    # Copy the value of project.due_date into a DevelopmentProjectAction instance.
    for project in projects:
        if project.due_date:
            due_date_value = project.due_date

            # Convert to datetime object and Make it timezone-aware, default it to 9am:
            datetime_obj = datetime.combine(due_date_value, datetime.min.time())
            due_date_value = timezone.make_aware(datetime_obj, timezone.get_default_timezone()) + timezone.timedelta(hours=9)

            due_date, _ = DevelopmentProjectAction.objects.get_or_create(
                project=project,
                label="Due date"
            )

            due_date.date = due_date_value
            due_date.save()

    # Don't need to delete the values of the due_date field since it will either be ignored in this commit,
    # or deleted anyways, but something else.


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0055_auto_20170322_1208'),
    ]

    operations = [
        migrations.RunPython(developmentProjectActionsToField, fieldToDevelopmentProjectActions),
    ]
