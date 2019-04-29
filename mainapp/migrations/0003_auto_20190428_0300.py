# Generated by Django 2.1.7 on 2019-04-28 00:00

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_placearticle_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='title',
            field=models.TextField(default='noname', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.TextField(max_length=65),
        ),
        migrations.AlterField(
            model_name='travler',
            name='username',
            field=models.SlugField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
    ]