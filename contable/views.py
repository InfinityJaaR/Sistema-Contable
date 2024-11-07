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
from django.http import JsonResponse
from datetime import datetime
import json
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
        cuentas = request.POST.getlist('codigo_cuenta[]')
        debes = request.POST.getlist('debe[]')
        haberes = request.POST.getlist('haber[]')
                
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
            cuenta_codigo = cuenta.split(' - ')[0]  # Obtener solo el código de la cuenta
            try:
                cuenta_obj = CuentaContable.objects.get(codigo_cuenta=cuenta_codigo)
            except CuentaContable.DoesNotExist:
                messages.error(request, f'La cuenta contable con código {cuenta_codigo} no existe.')
                transaccion.delete()  # Eliminar la transacción creada
                return redirect('registrar_transaccion')
            
            if debe:
                TransaccionCuenta.objects.create(transaccion=transaccion, cuenta=cuenta_obj, monto=float(debe), tipo='DEBITO')
            if haber:
                TransaccionCuenta.objects.create(transaccion=transaccion, cuenta=cuenta_obj, monto=float(haber), tipo='CREDITO')

        messages.success(request, 'Transacción guardada exitosamente.')
        return redirect('gestionar_transacciones')  # Redirige a la página anterior
    
    return render(request, 'registrarTransaccion.html', {'cuentas': cuentas, 'periodos': periodos})
    
@login_required
def catalogoCuentas(request):
    cuentas = CuentaContable.objects.all().order_by('codigo_cuenta')
    return render(request, 'catalogoCuentas.html', {'cuentas': cuentas})

@login_required
def estadoDeCapital(request):
    periodos = PeriodoContable.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        periodo_id = request.GET.get('periodo_id')
        asiento_id = request.GET.get('asiento_id')

        if periodo_id and not asiento_id:
            asientos = AsientoContable.objects.filter(periodo_id=periodo_id)
            asientos_data = [{'id': asiento.id, 'descripcion': asiento.descripcion} for asiento in asientos]
            return JsonResponse({'asientos': asientos_data})

        if periodo_id and asiento_id:
            cuenta71 = TransaccionCuenta.objects.filter(transaccion__asiento_id=asiento_id, cuenta__codigo_cuenta='71').first()
            cuenta71_data = {
                'cuenta': f"{cuenta71.cuenta.codigo_cuenta} - {cuenta71.cuenta.nombre_cuenta}",
                'debe': float(cuenta71.monto) if cuenta71.tipo == 'DEBITO' else 0,
                'haber': float(cuenta71.monto) if cuenta71.tipo == 'CREDITO' else 0
            }
            return JsonResponse({'cuenta71': cuenta71_data})

    if request.method == 'POST':
        data = json.loads(request.body)
        reinvertir_utilidades = data.get('reinvertir_utilidades', False)
        porcentaje_reinversion = data.get('porcentaje_reinversion', '0')
        cuenta71_debe = float(data.get('cuenta71_debe', 0))
        cuenta71_haber = float(data.get('cuenta71_haber', 0))

        try:
            porcentaje_reinversion = float(porcentaje_reinversion)
        except ValueError:
            porcentaje_reinversion = 0

        patrimonio_data = []

        # 3 - Patrimonio
        patrimonio_data.append({
            'cuenta': '3 - Patrimonio',
            'debe': None,
            'haber': None,
            'highlight': True
        })

        # 31 - Capital
        capital = CuentaContable.objects.filter(codigo_cuenta='31').first()
        if capital:
            debe = TransaccionCuenta.objects.filter(cuenta=capital, tipo='DEBITO').aggregate(total=Sum('monto'))['total'] or 0
            haber = TransaccionCuenta.objects.filter(cuenta=capital, tipo='CREDITO').aggregate(total=Sum('monto'))['total'] or 0
            patrimonio_data.append({
                'cuenta': f"{capital.codigo_cuenta} - {capital.nombre_cuenta}",
                'debe': float(debe),
                'haber': float(haber)
            })

        # 312 - Utilidades retenidas
        patrimonio_data.append({
            'cuenta': '312 - Utilidades Retenidas',
            'debe': None,
            'haber': None,
            'highlight': True
        })

        # 3121 - Utilidades No Distribuidas
        utilidades_no_distribuidas_debe = cuenta71_haber * (1 - porcentaje_reinversion / 100)
        patrimonio_data.append({
            'cuenta': '3121 - Utilidades No Distribuidas',
            'debe': utilidades_no_distribuidas_debe,
            'haber': 0
        })

        # 3122 - Reinversion de utilidades
        reinversion_haber = 0
        reinversion_debe = 0
        if cuenta71_debe > 0:
            reinversion_debe = cuenta71_debe
            patrimonio_data.append({
                'cuenta': '3122 - Reinversion de Utilidades',
                'debe': reinversion_debe,
                'haber': 0
            })
        elif reinvertir_utilidades:
            reinversion_haber = cuenta71_haber * (porcentaje_reinversion / 100)
            patrimonio_data.append({
                'cuenta': '3122 - Reinversion de Utilidades',
                'debe': 0,
                'haber': reinversion_haber
            })

        # 311 - Capital Social
        total_haber = sum(item['haber'] for item in patrimonio_data if item['cuenta'] == '31 - Capital') - reinversion_debe + reinversion_haber
        patrimonio_data.append({
            'cuenta': '311 - Capital Social',
            'debe': 0,
            'haber': total_haber,
            'highlight': True
        })

        return JsonResponse({'patrimonio': patrimonio_data})

    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            asiento = AsientoContable.objects.get(id=data.get('asiento_id'))
        except AsientoContable.DoesNotExist:
            return JsonResponse({'error': 'El asiento contable seleccionado no existe.'}, status=400)

        fecha = datetime.now()
        descripcion = f"Estado de Capital al día de {fecha.strftime('%d/%m/%Y')}"
        capital_social_haber = data.get('capital_social_haber', 0)
        utilidades_no_distribuidas_haber = data.get('utilidades_no_distribuidas_haber', 0)

        # Crear la transacción
        transaccion = Transaccion.objects.create(
            fecha=fecha,
            descripcion=descripcion,
            asiento=asiento,
            monto_total=capital_social_haber + utilidades_no_distribuidas_haber
        )

        # Guardar 3121 - Utilidades No Distribuidas
        utilidades_no_distribuidas_debe = data.get('utilidades_no_distribuidas_debe', 0)
        TransaccionCuenta.objects.create(
            cuenta=CuentaContable.objects.get(codigo_cuenta='3121'),
            transaccion=transaccion,
            tipo='DEBITO',
            monto=utilidades_no_distribuidas_debe
        )
        TransaccionCuenta.objects.create(
            cuenta=CuentaContable.objects.get(codigo_cuenta='3121'),
            transaccion=transaccion,
            tipo='CREDITO',
            monto=utilidades_no_distribuidas_haber
        )

        # Guardar 311 - Capital Social
        capital_social_debe = data.get('capital_social_debe', 0)
        TransaccionCuenta.objects.create(
            cuenta=CuentaContable.objects.get(codigo_cuenta='311'),
            transaccion=transaccion,
            tipo='DEBITO',
            monto=capital_social_debe
        )
        TransaccionCuenta.objects.create(
            cuenta=CuentaContable.objects.get(codigo_cuenta='311'),
            transaccion=transaccion,
            tipo='CREDITO',
            monto=capital_social_haber
        )

        return JsonResponse({'message': 'Datos guardados correctamente.'})

    return render(request, 'estadoDeCapital.html', {'periodos': periodos})
    
@login_required
def estadoResultados(request):
    asiento_id = request.GET.get('asiento_id')
    periodo_id = request.GET.get('periodo_id')
    periodos = PeriodoContable.objects.all().order_by('fecha_inicio')
    asientos = AsientoContable.objects.all().order_by('-fecha')

    # Inicializar variables
    cuentas_con_valores = []
    total_debe = 0
    total_haber = 0
    utilidad_bruta_perdida = 0

    # Si hay periodo seleccionado, filtrar asientos por ese periodo
    if periodo_id:
        try:
            periodo = PeriodoContable.objects.get(id=periodo_id)
            asientos = AsientoContable.objects.filter(periodo=periodo).order_by('-fecha')
        except PeriodoContable.DoesNotExist:
            messages.error(request, 'El período contable seleccionado no existe.')
            return redirect('estadoResultados')

    # Construir el filtro base para las transacciones
    transacciones_filter = Q(cuenta__tipo__in=['INGRESOS', 'COSTOS', 'GASTOS'])
    
    # Agregar filtros según los parámetros seleccionados
    if periodo_id and asiento_id:
        # Si ambos están seleccionados, filtrar por periodo y asiento
        transacciones_filter &= Q(
            transaccion__asiento__periodo_id=periodo_id,
            transaccion__asiento_id=asiento_id
        )
    elif periodo_id:
        # Solo filtrar por periodo
        transacciones_filter &= Q(transaccion__asiento__periodo_id=periodo_id)
    elif asiento_id:
        # Solo filtrar por asiento
        transacciones_filter &= Q(transaccion__asiento_id=asiento_id)
    else:
        # Si no hay filtros, no mostrar nada
        context = {
            'asientos': asientos,
            'periodos': periodos,
            'cuentas': [],
            'total_debe': 0,
            'total_haber': 0,
            'utilidad_bruta_perdida': 0,
            'asiento_id': asiento_id,
            'periodo_id': periodo_id,
        }
        return render(request, 'estadoResultado.html', context)

    # Obtener las transacciones según los filtros aplicados
    transacciones = TransaccionCuenta.objects.filter(transacciones_filter)

    # Agrupar las transacciones por cuenta
    cuentas_dict = {}
    for trans in transacciones:
        key = (trans.cuenta.codigo_cuenta, trans.cuenta.nombre_cuenta, trans.cuenta.tipo)
        if key not in cuentas_dict:
            cuentas_dict[key] = {'debe': 0, 'haber': 0}
        
        if trans.tipo == 'DEBITO':
            cuentas_dict[key]['debe'] += float(trans.monto)
        else:
            cuentas_dict[key]['haber'] += float(trans.monto)

    # Convertir el diccionario a lista de cuentas con valores
    for (codigo, nombre, tipo), valores in cuentas_dict.items():
        cuentas_con_valores.append({
            'codigo': codigo,
            'nombre': nombre,
            'tipo': tipo,
            'debe': valores['debe'],
            'haber': valores['haber']
        })

    # Calcular totales
    total_debe = sum(cuenta['debe'] for cuenta in cuentas_con_valores)
    total_haber = sum(cuenta['haber'] for cuenta in cuentas_con_valores)
    utilidad_bruta_perdida = total_haber - total_debe

    context = {
        'asientos': asientos,
        'periodo': periodo,
        'periodos': periodos,
        'cuentas': cuentas_con_valores,
        'total_debe': total_debe,
        'total_haber': total_haber,
        'utilidad_bruta_perdida': utilidad_bruta_perdida,
        'asiento_id': asiento_id,
        'periodo_id': periodo_id,
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
                # asiento_cierre = AsientoContable.objects.create(
                #     fecha=timezone.now(),
                #     descripcion=f"Cierre de resultados del asiento {asiento_id}",
                #     periodo=asiento_original.periodo
                # )
            else:
                messages.error(request, 'No se ha seleccionado un asiento contable.')
                return redirect('estadoResultados')

            # Obtener la cuenta de Pérdidas y Ganancias
            cuenta_perdidas_ganancias = CuentaContable.objects.get(codigo_cuenta='71')

            # Crear la transacción
            transaccion = Transaccion.objects.create(
                asiento=asiento_original,
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
            messages.error(request, 'La cuenta de Pérdidas y Ganancias no existe.')
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
    # Obtener el periodo contable y el asiento contable seleccionados, si se especifican
    periodo_id = request.GET.get('periodo_id')
    asiento_id = request.GET.get('asiento_id')
    
    # Obtener todos los períodos contables para el selector de períodos
    periodos = PeriodoContable.objects.all().order_by('fecha_inicio')
    
    # Si no se selecciona ningún período, no se muestran cuentas ni asientos
    if not periodo_id:
        context = {
            'periodos': periodos,
            'cuentas_activo': [],
            'cuentas_pasivo': [],
            'cuentas_patrimonio': [],
            'total_debe': 0,
            'total_haber': 0,
            'asientos': [],
        }
        return render(request, 'balanceGeneral.html', context)

    # Obtener el período seleccionado y los asientos relacionados con él
    periodo = get_object_or_404(PeriodoContable, id=periodo_id)
    asientos = AsientoContable.objects.filter(periodo=periodo).order_by('fecha')

    # Filtrar por asiento específico si se selecciona, o usar todos los asientos del período
    if asiento_id:
        asientos = asientos.filter(id=asiento_id)

    # Filtrar cuentas por tipo y calcular los totales de debe y haber solo para el período y asientos seleccionados
    cuentas_activo = CuentaContable.objects.filter(
        tipo='ACTIVO',
        transaccioncuenta__transaccion__asiento__in=asientos
    ).order_by('codigo_cuenta').annotate(
        debe=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='DEBITO')),
        haber=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='CREDITO'))
    )
    cuentas_pasivo = CuentaContable.objects.filter(
        tipo='PASIVO',
        transaccioncuenta__transaccion__asiento__in=asientos
    ).order_by('codigo_cuenta').annotate(
        debe=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='DEBITO')),
        haber=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='CREDITO'))
    )
    # Filtrar solo las cuentas de PATRIMONIO específicas
    cuentas_patrimonio = CuentaContable.objects.filter(
        tipo='PATRIMONIO',
        nombre_cuenta__in=['Capital social', 'Utilidades retenidas no distribuidas'],
        transaccioncuenta__transaccion__asiento__in=asientos
    ).order_by('codigo_cuenta').annotate(
        debe=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='DEBITO')),
        haber=Sum('transaccioncuenta__monto', filter=Q(transaccioncuenta__tipo='CREDITO'))
    )

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
        'total_debe': total_debe,  # Total general de debe
        'total_haber': total_haber,  # Total general de haber
        'asientos': AsientoContable.objects.filter(periodo=periodo),  # Cargar solo los asientos del periodo seleccionado
        'asiento_id': asiento_id
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