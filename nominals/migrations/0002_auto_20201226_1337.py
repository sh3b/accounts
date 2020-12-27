# Generated by Django 3.1.3 on 2020-12-26 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalnominal',
            name='type',
            field=models.CharField(blank=True, choices=[('pl', 'profit and loss'), ('b', 'balance sheet')], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='nominal',
            name='type',
            field=models.CharField(blank=True, choices=[('pl', 'profit and loss'), ('b', 'balance sheet')], max_length=2, null=True),
        ),
    ]