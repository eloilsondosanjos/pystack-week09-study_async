from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth

def register(request):

  if request.method == "GET":
      return render(request, 'register.html')
  elif request.method == "POST":
      username = request.POST.get('username')
      password = request.POST.get('password')
      confirm_password = request.POST.get('confirm_password')

  if len(username.strip()) == 0 or len(password.strip()) == 0  or len(confirm_password.strip()) == 0:
      messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
      return redirect('/users/register/')

  if not password == confirm_password:
      messages.add_message(request, constants.ERROR, 'Senha e confimar senha são diferentes')
      return redirect('/users/register/')
  
  user = User.objects.filter(username = username)

  if user.exists():
      messages.add_message(request, constants.ERROR, 'Usuário já existe')
      return redirect('/users/register/')

  try:      
      User.objects.create_user(
          username = username,
          password = password
      )
      return redirect('/users/signin/')
  except:
       messages.add_message(request, constants.ERROR, 'Erro interno de servidor')
       return redirect('/users/register/')
  
def signin(request):
    if request.method == "GET":
      return render(request, 'signin.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(request, username = username, password = password)

        if user:
            auth.login(request, user)
            messages.add_message(request, constants.SUCCESS, 'Login efetuado com sucesso')
            return redirect('/flashcard/new_flashcard/')
        else:
             messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
             return redirect('/users/signin/')

def signout(request):
    auth.logout(request)
    return redirect('/users/signin/')
    
