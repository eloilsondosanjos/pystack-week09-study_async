from django.urls import path
from . import views

urlpatterns = [
    path('add_handout/', views.add_handout, name="add_handout"),
    path('handout/<int:id>', views.handout, name="handout"),
]