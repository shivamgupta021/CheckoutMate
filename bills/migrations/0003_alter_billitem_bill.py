# Generated by Django 5.1.1 on 2024-09-30 15:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bills", "0002_alter_billitem_bill"),
    ]

    operations = [
        migrations.AlterField(
            model_name="billitem",
            name="bill",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="bills.bill",
            ),
        ),
    ]
