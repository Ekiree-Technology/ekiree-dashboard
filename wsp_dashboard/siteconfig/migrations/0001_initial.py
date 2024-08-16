# Generated by Django 2.1.1 on 2019-08-17 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HeroImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero', models.ImageField(upload_to='')),
                ('app', models.CharField(choices=[('default', 'default'), ('ed', 'ed'), ('vita', 'vita'), ('reports', 'reports')], default='default', max_length=10, unique=True)),
            ],
        ),
    ]
