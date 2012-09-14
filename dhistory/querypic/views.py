# Create your views here.
from django.shortcuts import render


def show_querypic(request):
    return render(request, 'index.html', {})
