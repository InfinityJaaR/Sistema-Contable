from django.urls import path
from .views import *

urlpatterns = [
    path('', home , name='home'),
    path('gestionarTransacciones/', gestionarTransacciones, name='gestionar_transacciones'),
    path('asignarPeriodo/', asignarPeriodo, name='asignar_periodo'),
    path('asignarAsiento/', asignarAsiento, name='asignar_asiento'),
    path('gestionarTransacciones/registrarTransaccion/', registrarTransaccion, name='registrar_transaccion'),
    path('catalogoCuentas/', catalogoCuentas, name='catalogoCuentas'),
    path('logout/', logout_view, name='logout'),  
]