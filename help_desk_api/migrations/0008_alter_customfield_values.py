# Generated by Django 4.2.14 on 2024-08-08 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("help_desk_api", "0007_alter_value_halo_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customfield",
            name="values",
            field=models.ManyToManyField(
                blank=True,
                related_name="field",
                to="help_desk_api.value",
                verbose_name="Value mappings",
            ),
        ),
    ]