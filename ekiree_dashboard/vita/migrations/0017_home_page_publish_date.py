# Generated by Django 2.1.1 on 2019-10-08 21:52

import datetime
from django.db import migrations, models
from datetime import timezone 

# Then use timezone.utc instead of just utc utc


class Migration(migrations.Migration):

    dependencies = [
        ('vita', '0016_home_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='home_page',
            name='publish_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 8, 21, 52, 23, 72636, tzinfo=timezone.utc), verbose_name='Published'),
            preserve_default=False,
        ),
    ]
