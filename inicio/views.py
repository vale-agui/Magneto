from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required(login_url='accounts/login')
def home(request):
    return render(request, 'home.html')
