from django.shortcuts import render
from django.urls import path
from . import views


app_name = "GoDigApp"

urlpatterns=[
  path('getPasscode',views.getPasscode),
  path('savePetroliumPrice', views.saveCurrentPetroliumPrices)
]