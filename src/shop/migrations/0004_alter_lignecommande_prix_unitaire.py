# Generated by Django 5.1.7 on 2025-03-29 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_alter_utilisateur_groups_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lignecommande',
            name='prix_unitaire',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
    ]
