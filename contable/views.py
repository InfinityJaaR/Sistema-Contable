from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone  # Agregar este import
from django.db.models import Sum, Q
from .models import PeriodoContable, CuentaContable, TransaccionCuenta, Transaccion, TransaccionCuenta
from decimal import Decimal
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
    periodos = PeriodoContable.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        periodo_id = request.GET.get('periodo_id')
        asientos = AsientoContable.objects.filter(periodo_id=periodo_id)
        asientos_data = [{'id': asiento.id, 'descripcion': asiento.descripcion} for asiento in asientos]
        return JsonResponse({'asientos': asientos_data})

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
    
    return render(request, 'registrarTransaccion.html', {'cuentas': cuentas, 'periodos': periodos})

@login_required
def catalogoCuentas(request):
    cuentas = CuentaContable.objects.all().order_by('codigo_cuenta')
    return render(request, 'catalogoCuentas.html', {'cuentas': cuentas})

@login_required
def estadoDeCapital(request):
     # Definir la función para obtener el saldo de una cuenta específica
    def obtener_saldo(codigo_cuenta, asiento_id=None):
        transacciones = TransaccionCuenta.objects.filter(cuenta__codigo_cuenta=codigo_cuenta)
        if asiento_id:
            transacciones = transacciones.filter(transaccion__asiento_id=asiento_id)
        saldo_debe = transacciones.filter(tipo='DEBITO').aggregate(total=Sum('monto'))['total'] or 0
        saldo_haber = transacciones.filter(tipo='CREDITO').aggregate(total=Sum('monto'))['total'] or 0
        return saldo_debe, saldo_haber

    # Obtener todos los asientos contables
    asientos = AsientoContable.objects.all()

    # Obtener el asiento contable seleccionado
    asiento_id = request.GET.get('asiento_id')
    if asiento_id:
        asiento_id = int(asiento_id)

    utilidades = Decimal(0)
    if asiento_id:
        # Obtener el saldo de la cuenta de pérdidas y ganancias con codigo_cuenta 71
        saldo_debe_utilidades, saldo_haber_utilidades = obtener_saldo('71', asiento_id)
        utilidades = saldo_haber_utilidades - saldo_debe_utilidades

    # Verificar si la solicitud es una solicitud AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'utilidades': float(utilidades)})

    reinversion_utilidades = Decimal(0)
    nuevo_capital = Decimal(0)

    if request.method == 'POST':
        try:
            reinversion_utilidades = Decimal(request.POST.get('reinversion_utilidades', 0))
            reinversion_monto = (reinversion_utilidades / Decimal(100)) * utilidades
            resto_utilidades = utilidades - reinversion_monto

            # Calcular el monto total de la transacción
            monto_total = resto_utilidades + reinversion_monto

            # Crear una nueva transacción para el asiento contable seleccionado
            transaccion = Transaccion.objects.create(
                fecha=timezone.now(),
                descripcion='Actualización de Capital Social',
                monto_total=monto_total
            )

            # Crear las transacciones de cuenta para cumplir con la partida doble
            TransaccionCuenta.objects.create(
                transaccion=transaccion,
                cuenta=CuentaContable.objects.get(codigo_cuenta='311'),
                monto=monto_total,
                tipo='DEBITO'
            )
            TransaccionCuenta.objects.create(
                transaccion=transaccion,
                cuenta=CuentaContable.objects.get(codigo_cuenta='31'),
                monto=monto_total,
                tipo='CREDITO'
            )

            messages.success(request, 'Capital social actualizado exitosamente.')
            return redirect('estado_de_capital')
        except Exception as e:
            messages.error(request, f'Error al procesar los datos: {e}')

    # Obtener los saldos de las cuentas específicas
    saldo_debe_capital_social, saldo_haber_capital_social = obtener_saldo('311', asiento_id)
    saldo_debe_utilidades_retenidas, saldo_haber_utilidades_retenidas = obtener_saldo('312', asiento_id)

    # Calcular los valores de reinversión de utilidades
    resto_utilidades = utilidades - reinversion_utilidades

    # Definir las cuentas y sus valores
    cuentas = [
        {'nombre': 'Patrimonio Neto', 'debe': '', 'haber': ''},
        {'nombre': '311 Capital Social', 'debe': saldo_debe_capital_social, 'haber': saldo_haber_capital_social},
        {'nombre': '3.1.2 Utilidades retenidas', 'debe': saldo_debe_utilidades_retenidas, 'haber': saldo_haber_utilidades_retenidas},
        {'nombre': '3.1.2.2 Reinversion de utilidades', 'debe': resto_utilidades, 'haber': reinversion_utilidades},
    ]

    return render(request, 'estadoDeCapital.html', {
        'asientos': asientos,
        'asiento_id': asiento_id,
        'utilidades': utilidades,
        'cuentas': cuentas,
        'reinversion_utilidades': reinversion_utilidades,
        'nuevo_capital': nuevo_capital,
        'saldo_debe_capital_social': saldo_debe_capital_social,
        'saldo_haber_capital_social': saldo_haber_capital_social,
    })
    
@login_required
def estadoResultados(request):
    asiento_id = request.GET.get('asiento_id')
    asientos = AsientoContable.objects.all().order_by('-fecha')
    
    # Inicializar variables vacías
    cuentas_con_valores = []
    total_debe = 0
    total_haber = 0
    utilidad_bruta_perdida = 0

    if asiento_id:
        # Solo procesar transacciones si hay un asiento seleccionado
        transacciones = TransaccionCuenta.objects.filter(
            transaccion__asiento_id=asiento_id,
            cuenta__tipo__in=['INGRESOS', 'COSTOS', 'GASTOS']
        )

        # Calcular los valores de debe y haber para cada cuenta
        for transaccion in transacciones:
            cuenta = transaccion.cuenta
            debe = transaccion.monto if transaccion.tipo == 'DEBITO' else 0
            haber = transaccion.monto if transaccion.tipo == 'CREDITO' else 0

            cuenta_existente = next((c for c in cuentas_con_valores if c['codigo'] == cuenta.codigo_cuenta), None)
            if cuenta_existente:
                cuenta_existente['debe'] += debe
                cuenta_existente['haber'] += haber
            else:
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

    context = {
        'asientos': asientos,
        'cuentas': cuentas_con_valores,
        'total_debe': total_debe,
        'total_haber': total_haber,
        'utilidad_bruta_perdida': utilidad_bruta_perdida,
        'asiento_id': asiento_id,
    }
    return render(request, 'estadoResultado.html', context)

@login_required
def guardar_resultado(request):
    if request.method == 'POST':
        utilidad_bruta_perdida = float(request.POST.get('utilidad_bruta_perdida', 0))
        asiento_id = request.POST.get('asiento_id')

        try:
            # Obtener o crear un nuevo asiento para el registro
            if asiento_id:
                asiento_original = AsientoContable.objects.get(id=asiento_id)
                asiento_cierre = AsientoContable.objects.create(
                    fecha=timezone.now(),
                    descripcion=f"Cierre de resultados del asiento {asiento_id}",
                    periodo=asiento_original.periodo
                )
            else:
                messages.error(request, 'No se ha seleccionado un asiento contable.')
                return redirect('estadoResultados')

            # Obtener la cuenta de Pérdidas y Ganancias
            cuenta_perdidas_ganancias = CuentaContable.objects.get(codigo_cuenta='71')

            # Crear la transacción
            transaccion = Transaccion.objects.create(
                asiento=asiento_cierre,
                fecha=timezone.now(),
                descripcion="Registro de utilidad o pérdida",
                monto_total=abs(utilidad_bruta_perdida)
            )

            # Crear el registro en TransaccionCuenta
            if utilidad_bruta_perdida >= 0:
                TransaccionCuenta.objects.create(
                    transaccion=transaccion,
                    cuenta=cuenta_perdidas_ganancias,
                    monto=abs(utilidad_bruta_perdida),
                    tipo='CREDITO'
                )
            else:
                TransaccionCuenta.objects.create(
                    transaccion=transaccion,
                    cuenta=cuenta_perdidas_ganancias,
                    monto=abs(utilidad_bruta_perdida),
                    tipo='DEBITO'
                )

            messages.success(request, 'El resultado ha sido guardado exitosamente en la cuenta de Pérdidas y Ganancias.')

        except CuentaContable.DoesNotExist:
            messages.error(request, 'La cuenta de Pérdidas y Ganancias (71) no existe.')
        except Exception as e:
            messages.error(request, f'Error al guardar el resultado: {str(e)}')

    return redirect('estadoResultados')

@login_required
def inventario(request):
    productos = Producto.objects.all().order_by('id')
    return render(request, 'inventario.html', {'productos': productos})

@login_required
def nuevoProducto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        costo_total = request.POST.get('costo_total')

        # Validar que los campos requeridos estén presentes
        if not nombre or not descripcion or not costo_total:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('nuevo_producto')

        try:
            # Convertir costo_total a float y validar
            costo_total = float(costo_total)
            if costo_total <= 0:
                messages.error(request, 'El costo total debe ser mayor que 0.')
                return redirect('nuevo_producto')

            # Crear el producto solo con los campos que existen en el modelo
            Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                costo_neto=costo_total
            )
            messages.success(request, 'Software guardado exitosamente.')
            return redirect('inventario')
        except ValueError:
            messages.error(request, 'El costo total debe ser un número válido.')
            return redirect('nuevo_producto')

    return render(request, 'nuevoProducto.html')

@login_required
def eliminarProducto(request, producto_id):
    try:
        # Buscar el producto por su ID
        producto = Producto.objects.get(id=producto_id)
        nombre_producto = producto.nombre
        # Eliminar el producto
        producto.delete()
        messages.success(request, f'El producto "{nombre_producto}" ha sido eliminado exitosamente.')
    except Producto.DoesNotExist:
        messages.error(request, 'El producto no existe.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el producto: {str(e)}')
    
    return redirect('inventario')

@login_required
def balanceGeneral(request):
    # Obtener el periodo contable seleccionado, si se especifica
    periodo_id = request.GET.get('periodo_id')
    periodo = get_object_or_404(PeriodoContable, id=periodo_id) if periodo_id else None

    # Obtener todos los periodos contables para el selector
    periodos = PeriodoContable.objects.all().order_by('fecha_inicio')

    # Filtrar cuentas por tipo y calcular los totales de activo, pasivo y patrimonio, solo para el período seleccionado
    cuentas_activo = CuentaContable.objects.filter(
        tipo='ACTIVO',
        transaccioncuenta__transaccion__asiento__periodo=periodo  # Filtrar por el período contable
    ).order_by('codigo_cuenta').annotate(
        debe=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='DEBITO')),
        haber=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='CREDITO'))
    )
    cuentas_pasivo = CuentaContable.objects.filter(
        tipo='PASIVO',
        transaccioncuenta__transaccion__asiento__periodo=periodo  # Filtrar por el período contable
    ).order_by('codigo_cuenta').annotate(
        debe=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='DEBITO')),
        haber=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='CREDITO'))
    )
    cuentas_patrimonio = CuentaContable.objects.filter(
        tipo='PATRIMONIO',
        transaccioncuenta__transaccion__asiento__periodo=periodo  # Filtrar por el período contable
    ).order_by('codigo_cuenta').annotate(
        debe=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='DEBITO')),
        haber=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='CREDITO'))
    )

    # Calcular los totales y manejar valores None
    total_activo = sum((c.debe or 0) - (c.haber or 0) for c in cuentas_activo)
    total_pasivo = sum((c.haber or 0) - (c.debe or 0) for c in cuentas_pasivo)
    total_patrimonio = sum((c.haber or 0) - (c.debe or 0) for c in cuentas_patrimonio)

    # Calcular los totales generales de debe y haber de todas las cuentas
    total_debe = sum((c.debe or 0) for c in cuentas_activo) + \
                 sum((c.debe or 0) for c in cuentas_pasivo) + \
                 sum((c.debe or 0) for c in cuentas_patrimonio)

    total_haber = sum((c.haber or 0) for c in cuentas_activo) + \
                  sum((c.haber or 0) for c in cuentas_pasivo) + \
                  sum((c.haber or 0) for c in cuentas_patrimonio)


    context = {
        'periodo': periodo,
        'periodos': periodos,  # Pasamos todos los periodos al contexto
        'cuentas_activo': cuentas_activo,
        'cuentas_pasivo': cuentas_pasivo,
        'cuentas_patrimonio': cuentas_patrimonio,
        'total_activo': total_activo,
        'total_pasivo': total_pasivo,
        'total_patrimonio': total_patrimonio,
        'total_debe': total_debe, 
        'total_haber': total_haber 
    }
    return render(request, 'balanceGeneral.html', context)

@login_required
def verDetallesTransaccion(request, transaccion_id):
    # Obtener la transacción específica y sus detalles
    transaccion = get_object_or_404(Transaccion, id=transaccion_id)
    detalles_cuentas = TransaccionCuenta.objects.filter(transaccion=transaccion)

    context = {
        'transaccion': transaccion,
        'detalles_cuentas': detalles_cuentas
    }
    return render(request, 'verDetallesTransaccion.html', context)