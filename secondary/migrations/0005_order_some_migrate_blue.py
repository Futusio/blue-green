# Generated by Django 4.2.5 on 2023-09-09 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secondary', '0004_order_new_table_green'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='some_migrate',
            field=models.BooleanField(default=False),
        ),
    ]