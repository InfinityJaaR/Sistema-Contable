from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
# Create your views here.

# def login(request):
#     return render(request, '/registration/login.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def gestionarTransacciones(request):
    transacciones = Transaccion.objects.all()
    return render(request, 'gestionarTransacciones.html', {'transacciones': transacciones})

@login_required
def asignarPeriodo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha_inicio = request.POST.get('fechaInicio')
        fecha_fin = request.POST.get('fechaFin')

        # Validar que todos los campos sean proporcionados
        if not nombre or not fecha_inicio or not fecha_fin:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('asignar_periodo')

        # Validar que la fecha de fin sea posterior a la fecha de inicio
        if fecha_fin <= fecha_inicio:
            messages.error(request, 'La fecha de fin debe ser posterior a la fecha de inicio.')
            return redirect('asignar_periodo')

        # Crear el período contable
        PeriodoContable.objects.create(nombre=nombre, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        messages.success(request, 'Período contable guardado exitosamente.')
        return redirect('gestionar_transacciones')

    return render(request, 'asignarPeriodo.html')

@login_required
def asignarAsiento(request):
    periodos = PeriodoContable.objects.all()
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')
        periodo_id = request.POST.get('periodo')

        # Validar que todos los campos sean proporcionados
        if not fecha or not descripcion or not periodo_id:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('asignar_asiento')

        # Validar que el período contable exista
        try:
            periodo = PeriodoContable.objects.get(id=periodo_id)
        except PeriodoContable.DoesNotExist:
            messages.error(request, 'El período contable seleccionado no existe.')
            return redirect('asignar_asiento')

        # Crear el asiento contable
        AsientoContable.objects.create(fecha=fecha, descripcion=descripcion, periodo=periodo)
        messages.success(request, 'Asiento contable guardado exitosamente.')
        return redirect('gestionar_transacciones')

    return render(request, 'asignarAsiento.html', {'periodos': periodos})

@login_required
def registrarTransaccion(request):
    cuentas = CuentaContable.objects.all()
    asientos = AsientoContable.objects.all()
    periodos = PeriodoContable.objects.all()
    
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')
        periodo_id = request.POST.get('periodo')
        asiento_id = request.POST.get('asiento')
        cuentas = request.POST.getlist('codigo_cuenta')
        debes = request.POST.getlist('debe')
        haberes = request.POST.getlist('haber')
                
        # Validar que la fecha y la descripción sean proporcionadas
        if not fecha:
            messages.error(request, 'Debe seleccionar una fecha.')
            return redirect('registrar_transaccion')
        
        if not descripcion:
            messages.error(request, 'Debe proporcionar una descripción.')
            return redirect('registrar_transaccion')
        
        # Validar que haya al menos dos cuentas en la transacción
        if len(cuentas) < 2:
            messages.error(request, 'Debe haber al menos dos cuentas en la transacción.')
            return redirect('registrar_transaccion')
        
        # Validar que la suma de debe y haber sea igual
        try:
            total_debe = sum(float(debe) for debe in debes if debe)
            total_haber = sum(float(haber) for haber in haberes if haber)
        except ValueError:
            messages.error(request, 'Los valores de Debe y Haber deben ser números válidos.')
            return redirect('registrar_transaccion')
        
        if total_debe != total_haber:
            messages.error(request, 'La suma de Debe y Haber debe ser igual.')
            return redirect('registrar_transaccion')
        
        # Obtener el periodo contable
        try:
            periodo = PeriodoContable.objects.get(id=periodo_id)
        except PeriodoContable.DoesNotExist:
            messages.error(request, 'El periodo contable seleccionado no existe.')
            return redirect('registrar_transaccion')
        
        # Obtener el Asiento Contable
        try:
            asiento = AsientoContable.objects.get(id=asiento_id)
        except AsientoContable.DoesNotExist:
            messages.error(request, 'El asiento contable seleccionado no existe.')
            return redirect('registrar_transaccion')

        # Crear Transacción
        transaccion = Transaccion.objects.create(asiento=asiento, fecha=fecha, descripcion=descripcion, monto_total=total_debe)

        # Crear Transacciones Cuentas
        for cuenta, debe, haber in zip(cuentas, debes, haberes):
            if debe:
                TransaccionCuenta.objects.create(transaccion=transaccion, cuenta_id=cuenta, monto=float(debe), tipo='DEBITO')
            if haber:
                TransaccionCuenta.objects.create(transaccion=transaccion, cuenta_id=cuenta, monto=float(haber), tipo='CREDITO')

        messages.success(request, 'Transacción guardada exitosamente.')
        return redirect('gestionar_transacciones')  # Redirige a la página anterior
    
    return render(request, 'registrarTransaccion.html', {'cuentas': cuentas, 'asientos': asientos, 'periodos': periodos})