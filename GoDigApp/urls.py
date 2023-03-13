from django.shortcuts import render
from django.urls import path
from . import views


app_name = "GoDigApp"

urlpatterns=[
  path('savePetroliumPrice/', views.saveCurrentPetroliumPrices),
  path('enrollUser/',views.EnrollUser),
  path('getPasscode/',views.getPasscode),
  path('verifyAllFields/',views.getVerifiedAllField,name='getVerifiedAllField'),
  path('verifyPasscode/',views.verifyPasscode,name='verifyPasscode'),
  path('registration/',views.Registration,name='Registration'),
  path('login/',views.login,name='login')
]