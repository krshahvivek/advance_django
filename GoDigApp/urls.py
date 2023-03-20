from django.shortcuts import render
from django.urls import path
# from GoDigApp import views
from . import views


app_name = "GoDigApp"

urlpatterns=[
  path('savePetroliumPrice/', views.saveCurrentPetroliumPrices),
  path('enrolluser/',views.enrolluser),
  path('sendPasscode/',views.sendPasscode,name='sendPasscode'),
  path('isEmailRegistered/',views.isEmailRegistered,name='isEmailRegistered'),
  path('registeruser/',views.registeruser,name='registeruser'),
  path('verifyPasscode/',views.verifyPasscode,name='verifyPasscode')
  
  



]