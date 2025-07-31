from django.shortcuts import render

# Create your views here.
def index(request):

    return render(request, 'layout/base.html')

# _4th_proj\templates\layout\base.html