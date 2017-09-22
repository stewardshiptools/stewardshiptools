# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0036_auto_20170502_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='dublincore',
            name='external_identifier',
            field=models.TextField(help_text='Publisher and Source data should follow the standard format used in the Chicago Manual of Style. Archival or record source information should also be included in this field as follows: Place: Name of Archive or Institution, Section (if known), Archival Collection Number, Volume Number, Folio or File Number; Microfilm Number. For example: Victoria, B.C.: Royal Columbia Museum, Anthropological Collections Section, MS. 421, Vol. 11, f. 4; Microfilm 267', verbose_name='External Identifier', blank=True, null=True),
        ),
    ]
