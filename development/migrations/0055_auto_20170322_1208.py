# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0054_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='due_date',
            field=models.DateField(null=True, verbose_name='Due Date', blank=True, help_text='Whichever due date is of concern.'),
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='final_decision',
            field=models.CharField(max_length=100, verbose_name='FN Final Decision', default='pending', choices=[('pending', 'Pending'), ('approved', 'Recommended'), ('rejected', 'Not Recommended')]),
        ),
    ]
