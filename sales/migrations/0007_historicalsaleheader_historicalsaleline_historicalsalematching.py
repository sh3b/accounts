# Generated by Django 3.1.1 on 2020-10-03 20:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('cashbook', '0006_historicalcashbook_historicalcashbookheader_historicalcashbookline_historicalcashbooktransaction'),
        ('vat', '0003_auto_20200712_1303'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nominals', '0013_historicalnominal_historicalnominalheader_historicalnominalline_historicalnominaltransaction'),
        ('items', '0001_initial'),
        ('sales', '0006_historicalcustomer'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalSaleMatching',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateField(blank=True, editable=False)),
                ('value', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('period', models.CharField(max_length=6)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('matched_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sales.saleheader')),
                ('matched_to', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sales.saleheader')),
            ],
            options={
                'verbose_name': 'historical sale matching',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSaleLine',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('line_no', models.IntegerField()),
                ('description', models.CharField(max_length=100)),
                ('goods', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vat', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('goods_nominal_transaction', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='nominals.nominaltransaction')),
                ('header', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sales.saleheader')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='items.item')),
                ('nominal', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='nominals.nominal')),
                ('total_nominal_transaction', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='nominals.nominaltransaction')),
                ('vat_code', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='vat.vat', verbose_name='Vat Code')),
                ('vat_nominal_transaction', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='nominals.nominaltransaction')),
            ],
            options={
                'verbose_name': 'historical sale line',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSaleHeader',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('ref', models.CharField(max_length=20)),
                ('goods', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vat', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('paid', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('due', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('date', models.DateField()),
                ('due_date', models.DateField(blank=True, null=True)),
                ('period', models.CharField(max_length=6)),
                ('status', models.CharField(choices=[('c', 'cleared'), ('v', 'void')], default='c', max_length=2)),
                ('type', models.CharField(choices=[('sbi', 'Brought Forward Invoice'), ('sbc', 'Brought Forward Credit Note'), ('sbp', 'Brought Forward Receipt'), ('sbr', 'Brought Forward Refund'), ('sp', 'Receipt'), ('sr', 'Refund'), ('si', 'Invoice'), ('sc', 'Credit Note')], max_length=3)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('cash_book', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='cashbook.cashbook')),
                ('customer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sales.customer')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical sale header',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
