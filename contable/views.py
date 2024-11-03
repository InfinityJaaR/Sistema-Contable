from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone  # Agregar este import
from django.db.models import Sum

# Create your views here.

# def login(request):
#     return render(request, '/registration/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def gestionarTransacciones(request):
    transacciones = Transaccion.objects.all().order_by('id')
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
        
        # Validar que los valores de debe y haber sean números válidos y no negativos
        try:
            total_debe = sum(float(debe) for debe in debes if debe)
            total_haber = sum(float(haber) for haber in haberes if haber)
            
            if any(float(debe) < 0 for debe in debes if debe):
                messages.error(request, 'Los valores de Debe no pueden ser negativos.')
                return redirect('registrar_transaccion')
            
            if any(float(haber) < 0 for haber in haberes if haber):
                messages.error(request, 'Los valores de Haber no pueden ser negativos.')
                return redirect('registrar_transaccion')
                
        except ValueError:
            messages.error(request, 'Los valores de Debe y Haber deben ser números válidos.')
            return redirect('registrar_transaccion')
        
        # Validar que la suma de debe y haber sea igual
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

@login_required
def catalogoCuentas(request):
    cuentas = CuentaContable.objects.all().order_by('codigo_cuenta')
    return render(request, 'catalogoCuentas.html', {'cuentas': cuentas})

@login_required
def estadoDeCapital(request):
    return render(request, 'estadoDeCapital.html')

@login_required
def estadoResultados(request):
    # Obtener todas las cuentas de INGRESOS, COSTOS y GASTOS
    cuentas = CuentaContable.objects.filter(tipo__in=['INGRESOS', 'COSTOS', 'GASTOS'])

    # Calcular los valores de debe y haber para cada cuenta
    cuentas_con_valores = []
    total_debe = 0
    total_haber = 0
    for cuenta in cuentas:
        debe = TransaccionCuenta.objects.filter(cuenta=cuenta, tipo='DEBITO').aggregate(Sum('monto'))['monto__sum'] or 0
        haber = TransaccionCuenta.objects.filter(cuenta=cuenta, tipo='CREDITO').aggregate(Sum('monto'))['monto__sum'] or 0
        if debe != 0 or haber != 0:
            cuentas_con_valores.append({
                'codigo': cuenta.codigo_cuenta,
                'nombre': cuenta.nombre_cuenta,
                'tipo': cuenta.tipo,
                'debe': debe,
                'haber': haber
            })
            total_debe += debe
            total_haber += haber

    utilidad_bruta_perdida = total_haber - total_debe

    # Actualizar la cuenta contable de "Pérdidas y Ganancias"
    try:
        cuenta_perdidas_ganancias = CuentaContable.objects.get(codigo_cuenta='71')
        cuenta_perdidas_ganancias.debe = 0 if utilidad_bruta_perdida >= 0 else abs(utilidad_bruta_perdida)
        cuenta_perdidas_ganancias.haber = abs(utilidad_bruta_perdida) if utilidad_bruta_perdida >= 0 else 0
        cuenta_perdidas_ganancias.save()
    except CuentaContable.DoesNotExist:
        messages.error(request, 'La cuenta contable de Pérdidas y Ganancias.')

    context = {
        'cuentas': cuentas_con_valores,
        'total_debe': total_debe,
        'total_haber': total_haber,
        'utilidad_bruta_perdida': utilidad_bruta_perdida,
    }
    return render(request, 'estadoResultado.html', context)

