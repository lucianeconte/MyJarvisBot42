# Generated by Django 2.0.7 on 2018-07-16 00:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0007_itenslista_secao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itenslista',
            name='categoria',
        ),
    ]
