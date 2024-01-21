from django.contrib import admin
from .models import Category, Flashcard, Challenge, ChallengeFlashcard

# Register your models here.

admin.site.register(Category)
admin.site.register(Flashcard)
admin.site.register(Challenge)
admin.site.register(ChallengeFlashcard)
