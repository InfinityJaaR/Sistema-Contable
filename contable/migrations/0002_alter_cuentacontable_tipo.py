# Generated by Django 5.1.2 on 2024-10-23 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contable', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuentacontable',
            name='tipo',
            field=models.CharField(choices=[('ACTIVO', 'Activo'), ('PASIVO', 'Pasivo'), ('PATRIMONIO', 'Patrimonio'), ('GASTOS Y COSTOS', 'Gastos y Costos'), ('INGRESOS', 'Ingresos'), ('C. DE CIERRE', 'C. de cierre')], max_length=50),
        ),
    ]
