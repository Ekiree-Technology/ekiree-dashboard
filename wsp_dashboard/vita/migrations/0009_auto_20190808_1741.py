# Generated by Django 2.1.1 on 2019-08-09 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vita', '0008_auto_20190808_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
