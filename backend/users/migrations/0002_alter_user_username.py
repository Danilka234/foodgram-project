# Generated by Django 3.2 on 2023-10-31 15:04

from django.db import migrations, models

import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[users.validators.validate_username_own], verbose_name='Пользователь'),
        ),
    ]