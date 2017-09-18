# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 13:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0004_auto_20170206_0407'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'permissions': (('view_sale', 'Can View Sale in Dashboard'), ('edit_sale', 'Can Edit Sale in Dashboard')), 'verbose_name': 'sale', 'verbose_name_plural': 'sales'},
        ),
        migrations.AlterModelOptions(
            name='voucher',
            options={'permissions': (('view_voucher', 'Can View Voucher in Dashboard'), ('edit_voucher', 'Can Edit Voucher in Dashboard')), 'verbose_name': 'voucher', 'verbose_name_plural': 'vouchers'},
        ),
    ]