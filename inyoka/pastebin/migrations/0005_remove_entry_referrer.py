# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pastebin', '0004_auto_20160703_0051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='referrer',
        ),
    ]