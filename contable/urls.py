from django.urls import path
from .views import *

urlpatterns = [
    path('', login),
    path('gestionarTransacciones/', gestionarTransacciones, name='gestionar_transacciones'),
    path('gestionarTransacciones/registrarTransaccion/', registrarTransaccion, name='registrar_transaccion'),
]