from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home , name='home'),
    path('gestionarTransacciones/', gestionarTransacciones, name='gestionar_transacciones'),
    path('asignarPeriodo/', asignarPeriodo, name='asignar_periodo'),
    path('asignarAsiento/', asignarAsiento, name='asignar_asiento'),
    path('gestionarTransacciones/registrarTransaccion/', registrarTransaccion, name='registrar_transaccion'),
    path('catalogoCuentas/', catalogoCuentas, name='catalogoCuentas'),
    path('estadoDeCapital/', estadoDeCapital, name='estado_de_capital'),
    path('logout/', logout_view, name='logout'),  
    path('estadoResultados/', estadoResultados, name='estadoResultados'),
    path('guardar-resultado/', guardar_resultado, name='guardar_resultado'),
    path('inventario/', inventario, name='inventario'),
    path('inventario/nuevoProducto/', nuevoProducto, name='nuevo_producto'),
    path('inventario/eliminar/<int:producto_id>/', eliminarProducto, name='eliminar_producto'),
]