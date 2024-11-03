from django.contrib import admin
from .models import PeriodoContable, EstadoFinanciero, CuentaContable, AsientoContable, Transaccion, TransaccionCuenta, Producto

# Register your models here.
admin.site.register(PeriodoContable)
admin.site.register(EstadoFinanciero)
admin.site.register(CuentaContable)
admin.site.register(AsientoContable)
admin.site.register(Transaccion)
admin.site.register(TransaccionCuenta)
admin.site.register(Producto)