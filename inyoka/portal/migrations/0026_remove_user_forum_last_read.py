# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0025_delete_sessioninfo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='forum_last_read',
        ),
    ]