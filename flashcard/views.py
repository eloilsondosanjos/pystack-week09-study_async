from django.shortcuts import render, redirect
from .models import Category, Flashcard, Challenge, ChallengeFlashcard
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages
from django.db import transaction

# Create your views here.

def new_flashcard(request):
  
  if not request.user.is_authenticated:
     return redirect('/users/signin')
  if request.method == "GET":
     categories = Category.objects.all()
     difficulties = Flashcard.DIFFICULTY_CHOICES
     flashcards = Flashcard.objects.filter(user=request.user)

     category_filter = request.GET.get('category')
     difficulty_filter = request.GET.get('difficulty')

     if category_filter:
        flashcards = flashcards.filter(category__id = category_filter)
     
     if difficulty_filter:
        flashcards = flashcards.filter(difficulty = difficulty_filter)

     return render(request, 'new_flashcard.html', { 'categories': categories, 'difficulties': difficulties, 'flashcards': flashcards })
  elif request.method == "POST":
     question = request.POST.get('question')
     answer = request.POST.get('answer')
     category = request.POST.get('category')
     difficulty = request.POST.get('difficulty')
     
     if len(question.strip()) == 0 or len(answer.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha os campos de pergunta e resposta')
        return redirect('/flashcard/new_flashcard/')
     
     flashcard = Flashcard(
        user = request.user,
        question = question,
        answer = answer,
        category_id = category,
        difficulty = difficulty
     )

     flashcard.save()
     messages.add_message(request, constants.SUCCESS, 'Flashcard cadastrado com sucesso')
     return redirect('/flashcard/new_flashcard/')
  
def delete_flashcard(request, id):
   flashcard = Flashcard.objects.get(id=id)

   if(flashcard.user_id == request.user.id):
      flashcard.delete()
      messages.add_message(request, constants.SUCCESS, 'Flashcard deletado com sucesso.')
      return redirect('/flashcard/new_flashcard/')
   else:
      messages.add_message(request, constants.ERROR, 'Flashcard pertence a outro usuário.')
      return redirect('/flashcard/new_flashcard/')

def start_challenge(request):
    if request.method == "GET":
        categories = Category.objects.all()
        difficulties = Flashcard.DIFFICULTY_CHOICES
        return render(request, 'start_challenge.html', {'categories': categories, 'difficulties': difficulties})
    elif request.method == "POST":
        title = request.POST.get('title')
        categories = request.POST.getlist('category')
        question_qtd = request.POST.get('question_qtd')
        difficulty = request.POST.get('difficulty')
    
    if len(title.strip()) == 0 or len(categories) == 0  or len(question_qtd) == 0 or len(difficulty.strip()) == 0:
      messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
      return redirect('/flashcard/start_challenge/')

    try:
        with transaction.atomic():
            challenge = Challenge(
                user=request.user,
                title=title,
                question_quantity=question_qtd,
                difficulty=difficulty,
            )

            challenge.save()

            for category in categories:
                challenge.category.add(category)

            flashcards = (
                Flashcard.objects
                .filter(user=request.user)
                .filter(difficulty=difficulty)
                .filter(category_id__in=categories)
                .order_by('?')
            )

            if flashcards.count() < int(question_qtd):
                messages.add_message(request, constants.ERROR,
                f'Qtd questões escolhida é maior que {flashcards.count()} disponível na base. Desafio não foi salvo')
                transaction.set_rollback(True)  # Rollback the transaction
                return redirect('/flashcard/start_challenge/')
            
            flashcards = flashcards[: int(question_qtd)]

            for flashcard in flashcards:
                challenge_flashcard = ChallengeFlashcard(
                  flashcard = flashcard
                )
                challenge_flashcard.save()
                challenge.flashcards.add(challenge_flashcard)
            
            challenge.save()

            return redirect('/flashcard/list_challenges/') 

    except Exception as e:
        # Handle the exception here, for example, log the error
        messages.add_message(request, constants.ERROR, 'Ocorreu um erro ao criar o desafio. Tente novamente.')
        return redirect('/flashcard/list_challenges/')
    
def list_challenges(request):
   challenges = Challenge.objects.filter(user=request.user)
   # TODO: desenvolver os status
   # TODO: desenvolver os filtros
   return render(request, 'list_challenges.html', { 'challenges': challenges })

def challenge(request, id):   
  challenge = Challenge.objects.get(id=id)

  if not challenge.user == request.user:
    raise Http404()  
  
  if request.method == 'GET':
      correct_qtd = challenge.flashcards.filter(answered=True).filter(correct=True).count()
      errors_qtd = challenge.flashcards.filter(answered=True).filter(correct=False).count()
      missing_qtd = challenge.flashcards.filter(answered=False).count()
      return render(request, 'challenge.html', {'challenge': challenge, 'correct_qtd': correct_qtd, 'errors_qtd': errors_qtd , 'missing_qtd': missing_qtd})

def to_respond_flashcard(request, id):
   challenge_flashcard = ChallengeFlashcard.objects.get(id=id)
   correct = request.GET.get('correct')
   challenge_id = request.GET.get('challenge_id')

   if not challenge_flashcard.flashcard.user == request.user:
      raise Http404()

   challenge_flashcard.answered = True
   challenge_flashcard.correct = True if correct == "1" else False

   challenge_flashcard.save()
   return redirect(f'/flashcard/challenge/{challenge_id}')

def report(request, id):
   challenge = Challenge.objects.get(id=id)

   correct_qtd = challenge.flashcards.filter(correct=True).count()
   errors_qtd = challenge.flashcards.filter(correct=False).count()
   
   data = [correct_qtd, errors_qtd]

   categories = challenge.category.all()
   categories_name = [i.name for i in categories]
   
  #  categories_name = []
  #  for category in categories:
  #     categories_name.append(category.name)
  
   data2 = []
   for category in categories:
     data2.append(challenge.flashcards.filter(flashcard__category=category).filter(correct=True).count())

   return render(request, 'report.html', {'challenge': challenge, 'data': data, 'data2':data2, 'categories': categories_name})
  