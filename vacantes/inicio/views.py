from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def home(request):
    context = {}
    return render(request, 'home.html', context)
