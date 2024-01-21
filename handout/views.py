from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Handout, ViewHandout
from django.contrib.messages import constants
from django.contrib import messages

# Create your views here.
def add_handout(request):
  if request.method == 'GET':
    handouts = Handout.objects.filter(user=request.user)

    total_views = ViewHandout.objects.filter(handout__user=request.user).count()
    return render(request, 'add_handout.html', {'handouts': handouts, 'total_views': total_views})
  elif request.method == 'POST':
    title = request.POST.get('title')
    file = request.FILES['file']

    handout = Handout(
      user=request.user,
      title=title,
      file=file
    )

    handout.save()
    messages.add_message(request, constants.SUCCESS, 'Salvo com sucesso')
    return redirect('/handout/add_handout')
  
def handout(request, id):
  handout = Handout.objects.get(id=id)
  total_views = ViewHandout.objects.filter(handout=handout).count()
  unique_views = ViewHandout.objects.filter(handout=handout).values('ip').distinct().count()
  view = ViewHandout(
    ip = request.META['REMOTE_ADDR'],
    handout = handout
  )
  view.save()

  return render(request, 'handout.html', {'handout': handout, 'total_views': total_views, 'unique_views': unique_views})