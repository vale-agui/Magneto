from django.shortcuts import render, redirect, get_object_or_404
from .models import Vacante
from .forms import VacanteForm

def gestion_vacantes(request):
    vacantes = Vacante.objects.all()
    return render(request, 'vacantes/gestion_vacantes.html', {'vacantes': vacantes})

def crear_vacante(request):
    if request.method == 'POST':
        form = VacanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vacantes:gestion_vacantes') # Ajusta al nombre de tu vista de listado si existe
    else:
        form = VacanteForm()
    return render(request, 'vacantes/crear_vacante.html', {'form': form})

def listar_vacantes(request):
    vacantes = Vacante.objects.all()
    return render(request, 'vacantes/listar_vacantes.html', {'vacantes': vacantes})


def eliminar_vacante(request, vacante_id):
    vacante = get_object_or_404(Vacante, id=vacante_id)
    vacante.delete()
    return redirect('vacantes:gestion_vacantes')  # ← esta URL sí existe

def editar_vacante(request, vacante_id):
    vacante = get_object_or_404(Vacante, id=vacante_id)

    if request.method == 'POST':
        form = VacanteForm(request.POST, instance=vacante)
        if form.is_valid():
            form.save()
            return redirect('vacantes:gestion_vacantes')
    else:
        form = VacanteForm(instance=vacante)

    return render(request, 'vacantes/editar_vacante.html', {'form': form, 'vacante': vacante})

