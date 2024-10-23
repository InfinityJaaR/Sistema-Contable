from django.db import models
from django.core.exceptions import ValidationError

# Modelo para Periodo Contable
class PeriodoContable(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"Periodo {self.nombre} ({self.fecha_inicio} - {self.fecha_fin})"

    def clean(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

    class Meta:
        verbose_name = "Periodo Contable"
        verbose_name_plural = "Periodos Contables"
        ordering = ['fecha_inicio']


# Modelo para Estado Financiero
class EstadoFinanciero(models.Model):
    TIPO_ESTADO_CHOICES = [
        ('BALANCE_GENERAL', 'Balance General'),
        ('ESTADO_RESULTADOS', 'Estado de Resultados'),
        ('CAMBIO_PATRIMONIO', 'Estado de Cambio en el Patrimonio'),
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_ESTADO_CHOICES)
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE, related_name='estados_financieros')
    fecha_generacion = models.DateField()

    def __str__(self):
        return f"{self.get_tipo_display()} - Periodo: {self.periodo}"

    class Meta:
        verbose_name = "Estado Financiero"
        verbose_name_plural = "Estados Financieros"
        ordering = ['fecha_generacion']


# Modelo para Cuenta Contable
class CuentaContable(models.Model):
    nombre_cuenta = models.CharField(max_length=100)
    codigo_cuenta = models.CharField(max_length=10)
    #tipo = models.CharField(max_length=10, choices=[('DEBITO', 'Débito'), ('CREDITO', 'Crédito')])
    tipo = models.CharField(max_length=50, choices=[
        ('ACTIVO', 'Activo'), 
        ('PASIVO', 'Pasivo'),
        ('PATRIMONIO', 'Patrimonio'),
        ('INGRESOS', 'Ingresos'),
        ('COSTOS', 'Costos'),
        ('GASTOS', 'Gastos'),
        ('C. DE CIERRE', 'C. de cierre')])   # Activo, Pasivo, Patrimonio, etc.
    cuenta_padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcuentas')

    def __str__(self):
        return f"({self.codigo_cuenta}) - {self.nombre_cuenta} "

    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"
        unique_together = ['codigo_cuenta', 'nombre_cuenta']
        ordering = ['codigo_cuenta']


# Modelo para Asiento Contable
class AsientoContable(models.Model):
    fecha = models.DateField()
    descripcion = models.TextField()
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE, related_name='asientos')

    def __str__(self):
        return f"Asiento {self.id} - Periodo {self.periodo}"

    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"
        ordering = ['fecha']


# Modelo intermedio para relacionar Transacción y Cuenta Contable
class TransaccionCuenta(models.Model):
    transaccion = models.ForeignKey('Transaccion', on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=[('DEBITO', 'Débito'), ('CREDITO', 'Crédito')])

    def __str__(self):
        return f"Transacción {self.transaccion.id} - {self.cuenta.nombre_cuenta} - {self.tipo}"

    class Meta:
        verbose_name = "Transacción Cuenta"
        verbose_name_plural = "Transacciones Cuentas"
        ordering = ['transaccion', 'cuenta']


# Modelo para Transacción
class Transaccion(models.Model):
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='transacciones')
    fecha = models.DateField()
    descripcion = models.TextField()
    cuentas = models.ManyToManyField(CuentaContable, through='TransaccionCuenta')
    monto_total = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Transacción {self.id} - Asiento {self.asiento.id}"

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ['fecha']

