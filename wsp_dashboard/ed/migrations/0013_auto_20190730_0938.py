# Generated by Django 2.1.1 on 2019-07-30 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ed', '0012_auto_20190730_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationalgoal',
            name='title',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
