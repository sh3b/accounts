# Generated by Django 3.1.1 on 2020-09-22 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accountancy', '0001_initial'),
        ('sales', '0003_customer_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accountancy.address'),
        ),
    ]