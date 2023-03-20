from django.shortcuts import render
from django.urls import path
# from GoDigApp import views
from . import views


app_name = "GoDigApp"

urlpatterns=[
  path('savePetroliumPrice/', views.saveCurrentPetroliumPrices),
  path('enrollUser/',views.enrollUser),
  path('sendPasscode/',views.sendPasscode,name='sendPasscode'),
  path('isEmailRegistered/',views.isEmailRegistered,name='isEmailRegistered'),
  path('registerUser/',views.registerUser,name='registerUser'),
  path('verifyPasscode/',views.verifyPasscode,name='verifyPasscode'),
  path('checkLoginCredential/',views.checkLoginCredential,name='checkLoginCredential'),



]