# Generated by Django 5.1.2 on 2024-10-22 04:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodoContable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Periodo Contable',
                'verbose_name_plural': 'Periodos Contables',
                'ordering': ['fecha_inicio'],
            },
        ),
        migrations.CreateModel(
            name='CuentaContable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_cuenta', models.CharField(max_length=100)),
                ('codigo_cuenta', models.CharField(max_length=10)),
                ('tipo', models.CharField(max_length=50)),
                ('cuenta_padre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcuentas', to='contable.cuentacontable')),
            ],
            options={
                'verbose_name': 'Cuenta Contable',
                'verbose_name_plural': 'Cuentas Contables',
                'ordering': ['codigo_cuenta'],
                'unique_together': {('codigo_cuenta', 'nombre_cuenta')},
            },
        ),
        migrations.CreateModel(
            name='EstadoFinanciero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('BALANCE_GENERAL', 'Balance General'), ('ESTADO_RESULTADOS', 'Estado de Resultados'), ('CAMBIO_PATRIMONIO', 'Estado de Cambio en el Patrimonio')], max_length=50)),
                ('fecha_generacion', models.DateField()),
                ('periodo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estados_financieros', to='contable.periodocontable')),
            ],
            options={
                'verbose_name': 'Estado Financiero',
                'verbose_name_plural': 'Estados Financieros',
                'ordering': ['fecha_generacion'],
            },
        ),
        migrations.CreateModel(
            name='AsientoContable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('descripcion', models.TextField()),
                ('periodo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asientos', to='contable.periodocontable')),
            ],
            options={
                'verbose_name': 'Asiento Contable',
                'verbose_name_plural': 'Asientos Contables',
                'ordering': ['fecha'],
            },
        ),
        migrations.CreateModel(
            name='Transaccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('descripcion', models.TextField()),
                ('monto_total', models.DecimalField(decimal_places=2, max_digits=15)),
                ('asiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones', to='contable.asientocontable')),
            ],
            options={
                'verbose_name': 'Transacción',
                'verbose_name_plural': 'Transacciones',
                'ordering': ['fecha'],
            },
        ),
        migrations.CreateModel(
            name='TransaccionCuenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=15)),
                ('tipo', models.CharField(choices=[('DEBITO', 'Débito'), ('CREDITO', 'Crédito')], max_length=10)),
                ('cuenta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contable.cuentacontable')),
                ('transaccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contable.transaccion')),
            ],
            options={
                'verbose_name': 'Transacción Cuenta',
                'verbose_name_plural': 'Transacciones Cuentas',
                'ordering': ['transaccion', 'cuenta'],
            },
        ),
        migrations.AddField(
            model_name='transaccion',
            name='cuentas',
            field=models.ManyToManyField(through='contable.TransaccionCuenta', to='contable.cuentacontable'),
        ),
    ]
