# Generated by Django 3.2 on 2023-11-01 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20231031_1303'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tags',
            options={'verbose_name': 'Тэг', 'verbose_name_plural': 'Тэги'},
        ),
    ]