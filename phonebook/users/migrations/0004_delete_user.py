# Generated by Django 3.2.3 on 2021-06-20 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]