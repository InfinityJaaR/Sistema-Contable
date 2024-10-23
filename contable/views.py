from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

# def login(request):
#     return render(request, '/registration/login.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def gestionarTransacciones(request):
    return render(request, 'gestionarTransacciones.html')

@login_required
def registrarTransaccion(request):
    if request.method == 'POST':
        # Lógica para guardar la transacción en la base de datos
        # ...
        return redirect('gestionar_transacciones')  # Redirige a la página anterior
    return render(request, 'registrarTransaccion.html')