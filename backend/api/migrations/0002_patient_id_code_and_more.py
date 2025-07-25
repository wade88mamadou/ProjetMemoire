# Generated by Django 4.2.7 on 2025-07-12 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='id_code',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='comportement',
            name='laveLesMainsAvantDeManger',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='comportement',
            name='laveLesMainsDesEnfants',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='comportement',
            name='lieuRepas',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='comportement',
            name='mangeAvecLesMains',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='comportement',
            name='utiliseDuSavon',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='comportement',
            name='utiliseGelHydroalcoolique',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='lieuNaissance',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='niveauEtude',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='poids',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='sexe',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='taille',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
