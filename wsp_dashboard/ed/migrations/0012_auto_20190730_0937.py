# Generated by Django 2.1.1 on 2019-07-30 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ed', '0011_auto_20190718_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationalgoal',
            name='title',
            field=models.TextField(max_length=20, null=True),
        ),
    ]
