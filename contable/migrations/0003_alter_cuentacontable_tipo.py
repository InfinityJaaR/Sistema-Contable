# Generated by Django 5.1.2 on 2024-10-23 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contable', '0002_alter_cuentacontable_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuentacontable',
            name='tipo',
            field=models.CharField(choices=[('ACTIVO', 'Activo'), ('PASIVO', 'Pasivo'), ('PATRIMONIO', 'Patrimonio'), ('INGRESOS', 'Ingresos'), ('COSTOS', 'Costos'), ('GASTOS', 'Gastos'), ('C. DE CIERRE', 'C. de cierre')], max_length=50),
        ),
    ]
