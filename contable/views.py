from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import CuentaContable
# Create your views here.

# def login(request):
#     return render(request, '/registration/login.html')

@login_required
def home(request):
    return render(request, 'home.html')


def gestionarTransacciones(request):
    return render(request, 'gestionarTransacciones.html')


def registrarTransaccion(request):
    cuentas = CuentaContable.objects.all()
    if request.method == 'POST':
        # Lógica para guardar la transacción en la base de datos
        return redirect('gestionar_transacciones')  # Redirige a la página anterior
    return render(request, 'registrarTransaccion.html', {'cuentas': cuentas})