from django.shortcuts import render, redirect
from django.http import HttpResponse
# Create your views here.

def login(request):
    return render(request, 'login.html')

def gestionarTransacciones(request):
    return render(request, 'gestionarTransacciones.html')

def registrarTransaccion(request):
    if request.method == 'POST':
        # Lógica para guardar la transacción en la base de datos
        # ...
        return redirect('gestionar_transacciones')  # Redirige a la página anterior
    return render(request, 'registrarTransaccion.html')