# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='value',
            field=models.CharField(max_length=255, db_index=True),
            preserve_default=True,
        ),
    ]
