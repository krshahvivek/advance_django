from django.shortcuts import render
import datetime
# from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import Http404
from .utils import Validation, PasswordValidator
# import pyotp
import json
import uuid
import re
import base64
import smtplib
# from django.core.mail import send_mail
from django.core import serializers
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .src.generate_key import GenerateKey
import requests
from .src.data import Data
import os
import pathlib
from GoDigApp.functions import valid_mobile, validate_password
from .models import AuthUserEmails, User, LoginUuids, GroupAdmins, Groups, Productions, Welldescription
import pandas as pd
from django.core.validators import RegexValidator
from django.db import DatabaseError, IntegrityError
from rest_framework import status
from rest_framework.response import Response
from datetime import timezone


@csrf_exempt
def saveCurrentPetroliumPrices(request):
    configDir = os.path.join(pathlib.Path(__file__).parents[1], "config")
    with open(os.path.join(configDir, "config.json")) as configFile:
        config = json.load(configFile)

    with open(os.path.join(configDir, config["secretsJson"])) as secretsJson:
        config["secrets"] = json.load(secretsJson)

    prices= dict()
    data=Data(config = config)
    base_currency = 'USD'
    symbol = ['BRENTOIL','NG']
    petroliumType = ["CrudeRate", "GasRate", "CBMRate", "CondensateRate"]
    endpoint = 'latest'
    access_key = config["secrets"]["comodityAccessKey"]
    prices["Date"] = datetime.date.today()
    for idx, sym in enumerate(symbol):
        resp = requests.get(
            'https://commodities-api.com/api/'+endpoint+'?access_key='+access_key+'&base='+base_currency+'&symbols='+sym)
        if resp.status_code != 200:
            # This means something went wrong.
            raise KeyError('GET /'+endpoint+'/ {}'.format(resp.status_code))
        # print(f'::::{sym}::: {resp.json()["data"]["rates"][sym]}::')
        symData = (1/ resp.json()["data"]["rates"][sym])
        prices[petroliumType[idx]]=round(symData,2)

    prices["CBMRate"] = 49.7
    prices["CondensateRate"] = 44.7
    data.addNewRowInTable(tableName="petrolium_rates", values=prices, schema = "digipi")
    print(prices)
    return JsonResponse({"message": "Petrolium Price uploaded", "status":200})
class SendPasscode(APIView):
    http_method_names = ['get']
    @staticmethod
    def sendPasscode(self):
        existPasscodecheck = None
        email = self.data["PasscodeEmail"]
        keygen = GenerateKey()
        create_date = datetime.datetime.today()
        try:
            existPasscodecheck = LoginUuids.objects.filter(emailid=email)
            if existPasscodecheck:
                if existPasscodecheck[0].expireon.astimezone(timezone.utc).replace(tzinfo=None) >= create_date:
                    key = keygen.send(email,recipients=[email],key=existPasscodecheck[0].uuid)
                else:
                    existPasscodecheck[0].delete()
                    key = keygen.send(email,recipients=[email],key=None)
                    login = LoginUuids(uuid=key, emailid=email, createdon=create_date)
                    login.save()
            else:
                key = keygen.send(email,recipients=[email],key=None)
                login = LoginUuids(uuid=key, emailid=email, createdon=create_date)
                login.save()
        except Exception as e:
            return Response({"message": f"Unable to send the passcode due to {e}", "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Passcode sent", "title": "OK"}, status=status.HTTP_200_OK)
    def get(self,request):
        self.data = json.loads(request.body)
        self.isEnroll = self.data["IsEnroll"]
        self.groupID = self.data["GroupID"]
        self.adminEmail = self.data["AdminEmail"]
        self.passcodeEmail = self.data["PasscodeEmail"]
        if self.isEnroll:
            try:
                ObjectGroupAdminTable = GroupAdmins.objects.filter(adminemailid=self.adminEmail)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if len(ObjectGroupAdminTable) == 0: return Response(status=status.HTTP_400_BAD_REQUEST)
            tableAdminId = ObjectGroupAdminTable[0].adminid
            try:
                self.objectAuthUserEmailsTable = AuthUserEmails.objects.filter(emailid=self.passcodeEmail,adminid=tableAdminId)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if len(self.objectAuthUserEmailsTable) == 0: return Response(status=status.HTTP_400_BAD_REQUEST)
            tableAdminId = self.objectAuthUserEmailsTable[0].adminid.adminid
            tablePermitAs = self.objectAuthUserEmailsTable[0].permitas

            try:
                self.tableGroups = Groups.objects.get(groupid=tablePermitAs)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not (tablePermitAs == self.groupID):
                return JsonResponse({"status": 400, "title": "Bad Request", "message": "Sorry! You are not authorized to  Register as you want."})
            self.isEnrollsendPasscode = self.sendPasscode(self)
            if not self.isEnrollsendPasscode.status_code == 200:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif self.groupID == 4:
            self.groupIdSendPasscode = self.sendPasscode(self)
        else:
            try:
                ObjectGroupAdminTable = GroupAdmins.objects.filter(adminemailid=self.adminEmail)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                ObjectAuthUserEmail = AuthUserEmails.objects.filter(emailid=self.passcodeEmail)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if len(ObjectGroupAdminTable) == 0: return Response(status=status.HTTP_400_BAD_REQUEST)
            if len(ObjectAuthUserEmail) == 0: return Response({"message":"You are not authorized to register as you want, Please try to register as User"},status=status.HTTP_400_BAD_REQUEST)
            self.groupIdSendPasscode = self.sendPasscode(self)
        return Response(status=status.HTTP_200_OK)
sendPasscode = SendPasscode.as_view()
class VerifyPascode(APIView):
    http_method_names = ['get']
    @staticmethod
    def verifyPasscode(self):
        passcode = self.data['Passcode']
        email = self.data['PasscodeEmail']
        create_date = datetime.datetime.today()
        loginPasscode = None
        loginID = LoginUuids.objects.filter(emailid=email)
        if loginID:
            if not loginID[0].expireon.astimezone(timezone.utc).replace(tzinfo=None) >= create_date:
                return Response({"message": "Your passcode is expired, Please do send the passcode again", "title": "NOT ACCEPTABLE"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not loginID:
            return Response({"message": "Opps! there is not passcode to verify. Please do send the passcode again and then try to verify", "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        loginPasscode = loginID[0].uuid
        if passcode != loginPasscode:
            return Response({"message": "Your passcode did not match", "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Your passcode has matched", "title": "OK"}, status=status.HTTP_200_OK)
    def get(self, request):
        import pdb
        pdb.set_trace()
        self.data = json.loads(request.body)
        self.isVerifiedPasscode = self.verifyPasscode(self)
        if self.isVerifiedPasscode:
            return Response({"message": self.isVerifiedPasscode.data["message"]}, status=status.HTTP_200_OK)
        return Response({"message": self.isVerifiedPasscode.data["message"]}, status=status.HTTP_400_BAD_REQUEST)
verifyPasscode = VerifyPascode.as_view()   
class EnrollUser(APIView):
    http_method_names = ['post']
    def post(self, request):
        self.data = json.loads(request.body)
        self.email = self.data["PasscodeEmail"].lower()
        self.isadmin = self.data["IsEnroll"]
        self.groupId = self.data["GroupID"]
        self.adminEmail = self.data["AdminEmail"]
        self.name = self.data["UserName"]
        try:
            self.ObjectAuthUserTable = AuthUserEmails.objects.filter(emailid=self.email)
            self.ObjectUserTable = User.objects.filter(emailid=self.email)
        except:
            return Response({"message": "Error from server end", "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            self.groupAdmin = GroupAdmins.objects.filter(adminemailid=self.adminEmail)
        except:
            return Response({"message": "Error from server end", "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not self.groupAdmin:
            return Response({"message":"you are not alowed to enroll the user"},status=status.HTTP_400_BAD_REQUEST)
        if len(self.ObjectAuthUserTable) > 0:
            return Response({"message": "Already Enrolled", "title": "Bad Request"},status=status.HTTP_400_BAD_REQUEST)
        if len(self.ObjectUserTable) > 0:
            if len(self.groupAdmin) == 0:
                return Response({"message": "You are not allowed to register", "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                authUserEmail = AuthUserEmails(emailid=self.email, permitas=self.groupId, adminid=self.groupAdmin[0])
                authUserEmail.save()
                self.groupTable = Groups.objects.get(groupid=self.groupId)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if self.groupTable:
                user = User(groupid=self.groupTable)
                user.save()
        elif self.isadmin:
            try:
                groupsTable = Groups.objects.get(groupid=self.groupId)
            except:
                return Response({"message": "Error from server end", "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                self.objectGroupAdmin, self.GroupAdminTable =  GroupAdmins.objects.get_or_create(adminemailid=self.email,adminname=self.name,groupid=groupsTable)
                if not self.GroupAdminTable:
                    return Response({"title": "CONFLICT", "message": f"Email id {self.email} already been presented"}, status=status.HTTP_409_CONFLICT)
            except:
                return Response({"message": "Error from server end", "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                authUserEmail = AuthUserEmails(emailid=self.email, permitas=self.groupId, adminid=self.groupAdmin[0])
                authUserEmail.save()
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            try:
                authUserEmail = AuthUserEmails(emailid=self.email, permitas=self.groupId, adminid=self.groupAdmin[0])
                authUserEmail.save()
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)
enrolluser = EnrollUser.as_view()
class IsEmailRegistered(APIView):
    def get(self, request):
        self.data = json.loads(request.body)
        self.userEmail=self.data["UserEmail"]
        self.ObjectUserTable = User.objects.filter(emailid=self.userEmail)
        if len(self.ObjectUserTable) > 0:
            return Response(status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_200_OK)
isEmailRegistered = IsEmailRegistered.as_view()
class RegisterUser(APIView):
    def post(self,request):
        self.data = json.loads(request.body)
        self.userName = self.data["UserName"]
        self.number = self.data["ContactNo"]
        self.userEmail = self.data["UserEmail"]
        self.groupId = self.data["GroupID"]
        self.password = self.data["Password"]
        self.adminEmail = self.data["AdminEmail"]
        self.DateTime = datetime.datetime.today()
        if self.groupId == 4:
            """
                If User will register as a User
            """
            self.tableGroups = Groups.objects.get(groupid=self.groupId)
            created = User(username=self.userName,password=self.password,groupid=self.tableGroups,emailid=self.userEmail,isadmin=0,datecreated=self.DateTime,contactno = self.number)
            created.save()
        else:
            """If User will not register as a User """
            try:
                self.tableGroupAdmins = GroupAdmins.objects.filter(adminemailid=self.userEmail)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if len(self.tableGroupAdmins) == 0:
                isadmin = 0
            else:
                isadmin = self.tableGroupAdmins
            try:
                self.tableGroups = Groups.objects.get(groupid=self.groupId)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                userTable = User(username=self.userName,password=self.password,groupid=self.tableGroups,emailid=self.userEmail,isadmin=isadmin,datecreated=self.DateTime,contactno = self.number)
                userTable.save()
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Passcode sent", "title": "OK"}, status=status.HTTP_200_OK)
registeruser = RegisterUser.as_view()