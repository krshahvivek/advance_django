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


class GetFieldVerified(APIView):
    def get(self, request):
        self.data = json.loads(request.body)
        fields = self.getFieldVerified()
        if fields.status_code == 200:
            return Response({'success':True, 'message': 'All field verified'},  status=status.HTTP_200_OK)
        else:
            return Response({'success':False,'message': fields.data['message']}, status=status.HTTP_400_BAD_REQUEST)
    def getPasscodeField(self):
        Email = self.data["Email"].lower()
        RegisterAs = self.data.get('GroupID') if self.data.get('GroupID') else None
        AdminEmail = self.data.get('AdminEmail').lower() if self.data.get('AdminEmail') else None
        if not RegisterAs:
            return Response({'success':False,'message': 'Group ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Email:
            return Response({'success':False,'message': 'Email ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Validation().emailValidate(email=Email):
            return Response({'success':False,'message': 'Not Valid Email'}, status=status.HTTP_400_BAD_REQUEST)
        elif not AdminEmail:
            return Response({'success':False,'message': 'Admin ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Validation().emailValidate(email=AdminEmail):
            return Response({'success':False,'message': 'Not Valid Admin Email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success':True, 'message': 'All field verified'},  status=status.HTTP_200_OK)
    def getEnrollFieldVerified(self):
        # import pdb
        # pdb.set_trace()
        Email = self.data["EnrollEmail"].lower()
        AdminEmail = self.data.get('AdminEmail').lower() if self.data.get('AdminEmail') else None
        RegisterAs = self.data['GroupID'] if self.data.get('GroupID') else None
        if not RegisterAs:
            return Response({'success':False,'message': 'Group ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Email:
            return Response({'success':False,'message': 'Email ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Validation().emailValidate(email=Email):
            return Response({'success':False,'message': 'Not Valid Email'}, status=status.HTTP_400_BAD_REQUEST)
        elif not AdminEmail:
            return Response({'success':False,'message': 'Admin ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Validation().emailValidate(email=AdminEmail):
            return Response({'success':False,'message': 'Not Valid Admin Email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success':True, 'message': 'All field verified'},  status=status.HTTP_200_OK)
    def getFieldVerified(self):
        Name = self.data["Name"] if self.data.get("Name") else None
        Number = self.data["Number"] if self.data.get("Number") else None
        Email = self.data["Email"].lower() if self.data.get("Email") else None
        Password = self.data["Password"] if self.data.get("Password") else None
        ConfirmPassword = self.data["ConfirmPassword"] if self.data.get("ConfirmPassword") else None
        RegisterAs = self.data.get('GroupID') if self.data.get('GroupID') else None
        # AdminEmail = self.data.get('AdminEmail').lower() if self.data.get('AdminEmail') else None
        if not Name:
            return Response({'success':False,'message': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not RegisterAs:
            return Response({'success':False,'message': 'Group ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Email:
            return Response({'success':False,'message': 'Email ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Validation().emailValidate(email=Email):
            return Response({'success':False,'message': 'Not Valid Email'}, status=status.HTTP_400_BAD_REQUEST)
        # elif not AdminEmail:
        #     return Response({'success':False,'message': 'Admin ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        # elif not Validation().emailValidate(email=AdminEmail):
        #     return Response({'success':False,'message': 'Not Valid AdminEmail'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Number:
            return Response({'success':False,'message': 'Number is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif not valid_mobile(Number):
            return Response({'success':False,'message': 'Not Valid Number'}, status=status.HTTP_400_BAD_REQUEST)        
        elif not Password:
            return Response({'success':False,'message': 'Not Valid Password'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            obj= PasswordValidator(Password)
            getPasswordValidation = obj.validate()
            if getPasswordValidation:
                return Response({'success':False,'message': getPasswordValidation}, status=status.HTTP_400_BAD_REQUEST)
            elif not Password == ConfirmPassword:
                return Response({'success':False,'message': 'Not Matched Password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success':True, 'message': 'All field verified'},  status=status.HTTP_200_OK)
verifyAllFields = GetFieldVerified.as_view()
from datetime import timezone
class GetVerifyPasscode(APIView):
    # http_method_names = ['get']
    def getPasscode(self):
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
                    key = keygen.send(email,recipients=[email],key=existPasscodecheck[0])
                    login = LoginUuids(uuid=key, emailid=email, createdon=create_date)
                    login.save()
            else:
                key = keygen.send(email,recipients=[email],key=None)
                login = LoginUuids(uuid=key, emailid=email, createdon=create_date)
                login.save()
        except Exception as e:
            return Response({"message": f"Unable to send the passcode due to {e}", "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Passcode sent", "title": "OK"}, status=status.HTTP_200_OK)
    def verifyPasscode(self):
        passcode = self.data['Passcode'] if self.data['Passcode'] else None
        email = self.data['PasscodeEmail']
        loginPasscode = None
        loginID = LoginUuids.objects.filter(emailid=email).order_by('-id')
        if not loginID:
            return Response({"message": "Your passcode not matched", "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        loginPasscode = loginID[0].uuid
        if passcode != loginPasscode:
            return Response({"message": "Your passcode not matched", "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Your passcode matched", "title": "OK"}, status=status.HTTP_200_OK)
# verify_passcode = VerifyPasscode.as_view(get='verifyPasscode')

class EnrollUser(GetFieldVerified,GetVerifyPasscode, APIView):
    http_method_names = ['get','post']
    def get(self,request):
        self.data = json.loads(request.body)
        fieldVelidation = self.getEnrollFieldVerified()
        if fieldVelidation.status_code == 200 :
            if not self.getPasscode().status_code == 200:
                return Response({"message": self.getPasscode().data['message'], "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": fieldVelidation.data['message'], "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Passcode sent", "title": "OK"}, status=status.HTTP_200_OK)
    def post(self, request):
        import pdb
        pdb.set_trace()
        isValid, groupAdmin, groupAdminEmailId,matchedPasscode = (None,)*4
        self.data = json.loads(request.body)
        enroll_user = EnrollUser()
        response = enroll_user.get(request)
        if response.status_code == 200 :
            """
                Here we taking input PasscodeEmail and Passcode as well to send the passcode and match it
            """
            isadmin = self.data["isAdmin"]
            name = self.data['EnrollName']
            email = self.data["EnrollEmail"].lower()
            adminId = self.data["AdminEmail"]
            groupId = self.data["GroupID"]
            matchedPasscode = self.verifyPasscode()
            if not matchedPasscode:
                return Response({"message": matchedPasscode.data['message'], "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                groupAdmin = GroupAdmins.objects.filter(adminemailid=adminId)
                if not groupAdmin:
                    return Response({"message": "You are not allowed to register", "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"message": "Error from server end", "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                if isadmin:
                    groupAdminObject, groupAdminEmailId =  GroupAdmins.objects.get_or_create(adminemailid=email,adminname=name,groupid=groupId)
                elif not groupAdminEmailId:
                    return Response({"title": "CONFLICT", "message": f"Email id {email} already been presented"}, status=status.HTTP_409_CONFLICT)
            except:
                return Response({"message": "Error from server end", "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                obj, isValid = AuthUserEmails.objects.get_or_create(
                    emailid=email, permitas=groupId, adminid=groupAdmin[0])
            except AuthUserEmails.MultipleObjectsReturned:
                isValid = AuthUserEmails.objects.filter(emailid=email).first()
                isValid = False
            if isValid:
                return Response({"title": "OK", "message": f"Email id {email} successfully has been saved"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"title": "CONFLICT", "message": f"Email id {email} already been presented"}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({"message": response.data['message'], "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
enrollUser = EnrollUser.as_view()
class Registration(GetFieldVerified,GetVerifyPasscode, APIView):

    http_method_names = ['get','post']
    
    @staticmethod
    def getGroupId(self):
        RegisterAs = self["GroupID"] if self["GroupID"] else None
        if not RegisterAs:
            return 0
        elif RegisterAs > 4:
            return 0
        elif RegisterAs != 4:
            return RegisterAs
        elif RegisterAs == 4:
            return RegisterAs
   
    @staticmethod
    def adminEmailId(self):
        EnterAdminEmail = self["AdminEmail"].lower() if self["AdminEmail"] else None
        if not EnterAdminEmail:
            return 0
        elif Validation().emailValidate(email=EnterAdminEmail):
            return EnterAdminEmail
        else:
            return 0
    
    # @staticmethod
    # def getPasscode(self):
        import pdb
        pdb.set_trace()
        email = self.data["Email"]
        keygen = GenerateKey()
        create_date = datetime.datetime.today()
        try:
            key = keygen.send(email, recipients=[email])
            login = LoginUuids(uuid=key, emailid=email, createdon=create_date)
            login.save()
            return True
        except:
            return False
    
    @staticmethod
    def UserTable(self):
        name = self.name
        password = self.password
        tableGroups = self.tableGroups
        email = self.email
        # isadmin = 1 if self.groupID == 1 else 0
        DateTime = datetime.datetime.today()
        # number = self.number
        try:
            if GroupAdmins.objects.filter(adminemailid=self.email):
                isadmin = 1
        except:
            pass
        try:
            obj, created = User.objects.get_or_create(
                username=name,
                password=password,
                groupid=tableGroups,
                emailid=email,
                isadmin=isadmin,
                datecreated=DateTime,
                # number = number
                )
            if created:
                return 1
            else:
                return 0
        except:
            return False
    
    def get(self, request):
        self.data = json.loads(request.body)
        fieldVelidation =  self.getPasscodeField()
        groupID = self.getGroupId(self.data)
        adminEmail = self.adminEmailId(self.data)
        self.email = self.data["PasscodeEmail"].lower()
        if not fieldVelidation.status_code == 200:
            return Response({"message": fieldVelidation.data['message'], "title": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        elif groupID == 4:
            # if self.getPasscode(self):
            if self.getPasscode().status_code==200:
                return Response({"title": "OK",'success':False,'message': f"Data sent to you email id - {self.email}"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": self.getPasscode().data['message'], "title": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            try:
                auth_user = AuthUserEmails.objects.filter(emailid=self.email)
                tableAdminId = auth_user[0].adminid.adminid
                groupAdmintable = GroupAdmins.objects.get(adminid=tableAdminId)
                tableAdminEmail = groupAdmintable.adminemailid
                tablePermitAs = auth_user[0].permitas
                emailid = auth_user[0].emailid
                if not (tableAdminEmail == adminEmail):
                    return Response({'success':False,'message': 'Sorry! You are not authorized to  Register as you want.'}, status=status.HTTP_400_BAD_REQUEST)
                elif not (tablePermitAs == groupID):
                    return Response({'success':False,'message': 'Sorry! You are not authorized to  Register as you want.'}, status=status.HTTP_400_BAD_REQUEST)
                elif emailid == self.email:
                    if self.getPasscode():
                    # if self.getPasscode(self):
                        return Response({"title": "OK",'success':False,'message': f"Data sent to you email id - {self.email}"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"title": "Internal Server Error",'success':False,'message': 'Sorry! Error from server end.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"title": "Internal Server Error",'success':False,'message': f'Sorry! Error from server end. {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request):
        auth_user, adminEmail, matchedPasscode = (None,)*3
        self.data = json.loads(request.body)
        self.EnterPassCode = self.data["Passcode"]
        fieldVelidation =  self.getFieldVerified()
        self.groupID = self.getGroupId(self.data)
        adminEmail = self.adminEmailId(self.data)
        if not fieldVelidation.status_code == 200:
            return Response({"message": fieldVelidation.data['message'], "title": "NOT ACCEPTABLE"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            self.name = self.data["Name"]
            self.email = self.data["Email"].lower()
            self.password = self.data["Password"]
            # self.number = self.data["Number"]
        if self.groupID == 4:
            matchedPasscode = self.verifyPasscode()
        else:
            try:
                auth_user = AuthUserEmails.objects.filter(emailid=self.email)
                tableAdminId = auth_user[0].adminid.adminid
                groupAdmintable = GroupAdmins.objects.get(adminid=tableAdminId)
                tableAdminEmail = groupAdmintable.adminemailid
                tablePermitAs = auth_user[0].permitas
                self.tableGroups = Groups.objects.get(groupid=tablePermitAs)
                if not (tableAdminEmail == adminEmail):
                    return JsonResponse({"status": 400, "title": "Bad Request", "message": "Sorry! You are not authorized to Register."})
                elif not (tablePermitAs == self.groupID):
                    return JsonResponse({"status": 400, "title": "Bad Request", "message": "Sorry! You are not authorized to  Register as you want."})
                emailid = auth_user[0].emailid
                if emailid == self.email:
                    matchedPasscode = self.verifyPasscode()
            except Exception as e:
                return JsonResponse({"status": 500, "title": "Internal server Error", "success": False, "message": f"{e}"}, safe=False)
        if not matchedPasscode.status_code == 200:  return JsonResponse({"status": 400, "title": "Bad Request", "message": "You are registring wrong user type"}, safe=False)
        if self.groupID == 4:
            """If User will register as a User"""
            self.tableGroups = Groups.objects.get(groupid=self.groupID)
            userTable = self.UserTable(self)
            if userTable==False:
                return JsonResponse({"status": 500, "title": "Internal server Error", "success": False, "message": "Something happened to the server side", "error": e}, safe=False)
            elif userTable == 0:
                return JsonResponse({"status": 409, "title": "CONFLICT", "success": False, "message": "sorry you are already registered"}, safe=False)  
            else:
                return JsonResponse({"status": 200, "title": "OK", "message": "Registered Successfully."}, safe=False) 
        else:
            """If User will not register as a User """
            userTable = self.UserTable(self)
            if userTable==False:
                return JsonResponse({"status": 500, "title": "Internal server Error", "success": False, "message": "Something happened to the server side", "error": e}, safe=False)
            elif userTable == 0:
                return JsonResponse({"status": 409, "title": "CONFLICT", "success": False, "message": "sorry you are already registered"}, safe=False)  
            else:
                return JsonResponse({"status": 200, "title": "OK", "message": "Registered Successfully."}, safe=False)          
registration = Registration.as_view()

class Login(APIView):
    def post(request):
        email, getPassword,userEmail = (None,)*3
        request_body = json.loads(request.body)
        Email = request_body["LoginEmail"] if request_body["LoginEmail"] else None
        Password = request_body["Password"]  if request_body["Password"] else None
        if not Email:
            return Response({'success':False,'message': 'Pleas provide email'}, status=status.HTTP_400_BAD_REQUEST)
        elif not Password:
            return Response({'success':False,'message': 'Pleas provide Password'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            email = Email.lower()
            validEmail = Validation().emailValidate(email=email)
            if not validEmail:
                return JsonResponse({"message": "Please Enter Valid Email ID", "status": 406, "title": "NOT ACCEPTABLE"}, safe=False)
        try:
            auth_user = AuthUserEmails.objects.filter(emailid=email)
            if auth_user:
                tableEmailId = auth_user[0].emailid
                userEmail = User.objects.filter(emailid=tableEmailId)
            else:
                return JsonResponse({"message": "Please Enter Correct Email ID", "status": 406, "title": "NOT ACCEPTABLE"}, safe=False)
        except Exception as e:
            return JsonResponse({"status": 500, "title": "Internal server Error", "success": False, "message": "sorry you are not authorized to register", "error": e}, safe=False)
        if userEmail:
            getPassword = userEmail[0].password
            if Password != getPassword:
                return JsonResponse({"message": "Entered Password is wrong", "status": 406, "title": "NOT ACCEPTABLE"}, safe=False)
        else:
            return JsonResponse({"status": 500, "title": "Internal server Error", "success": False, "message": "sorry you are not authorized to register", "error": e}, safe=False)
        return JsonResponse({"status": 200, "title": "OK", "success": True, "message": "Login successfully"}, safe=False)
login = Login.as_view()


@csrf_exempt
def CSVIntoProductionTable(request):
    if request.method != "POST" and request.FILES["csv_file"]:
        return JsonResponse({"status": 405, "title": "Method not allowed", "message": f"{request.method} method not allowed."}, safe=False)
    wellId = None
    excel_file = request.FILES["csv_file"]
    df = pd.read_excel(excel_file)
    if df.items():
        for index, row in df.iterrows():
            if Productions.objects.filter(wellid=row[2]).exists():
                continue
            if not wellId == row[2]:
                wellId = Welldescription.objects.get(wellid=row[2])
            productions = Productions(productionid=row[0], productiondate=row[1], wellid=wellId,
                                      crudeoil=row[6], naturalgas=row[7], condensate=row[9], cbm=row[8])
            productions.save()
        return JsonResponse({"status": 200, "message": "Successfully data uploaded"}, safe=False)
    else:
        return JsonResponse({"status": 500, "message": "sorry there was some error"}, safe=False)


@csrf_exempt
def getOilProductionData(request):
    if request.method != "GET":
        return JsonResponse({"status": 405, "title": "Method not allowed", "message": f"{request.method} method not allowed."}, safe=False)
    startDate, endDate = (None,)*2
    startDate = request.GET.get("startDate")
    endDate = request.GET.get("endDate")
    start = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    end = datetime.datetime.strptime(endDate, '%Y-%m-%d')
    if not (start and end):
        return JsonResponse({"status": 403, "title": "FORBIDDEN", "message": f"{startDate} Formate of date is not allowed."}, safe=False)
    dataQueryset = Productions.objects.filter(
        ~Q(productiondate__range=[start, end]))
    serializedData = serializers.serialize('json', dataQueryset, fields=(
        'productionid', 'productiondate', 'wellid', 'crudeoil'))
    return JsonResponse({"status": 200, "title": "OK", "Data": serializedData}, safe=False)


@csrf_exempt
def getGasProductionData(request):
    if request.method != 'GET':
        return JsonResponse({"status": 405, "title": "Method not allowed", "message": f"{request.method} method not allowed."}, safe=False)
    startDate, endDate = (None,)*2
    startDate = request.GET.get('startDate')
    endDate = request.GET.get('endDate')
    start = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    end = datetime.datetime.strptime(endDate, '%Y-%m-%d')
    if not (start and end):
        return JsonResponse({"status": 403, "title": "FORBIDDEN", "message": f"{startDate} Formate of date is not allowed."}, safe=False)
    dataQueryset = Productions.objects.filter(
        ~Q(productiondate__range=[start, end]))
    serializedData = serializers.serialize('json', dataQueryset, fields=(
        'productionid', 'productiondate', 'wellid', 'naturalgas'))
    return JsonResponse({"status": 200, "title": "OK", "Data": serializedData}, safe=False)


@csrf_exempt
def getCondensateProductionData(request):
    if request.method != 'GET':
        return JsonResponse({"status": 405, "title": "Method not allowed", "message": f"{request.method} method not allowed."}, safe=False)
    startDate, endDate = (None,)*2
    startDate = request.GET.get('startDate')
    endDate = request.GET.get('endDate')
    start = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    end = datetime.datetime.strptime(endDate, '%Y-%m-%d')
    if not (start and end):
        return JsonResponse({"status": 403, "title": "FORBIDDEN", "message": f"{startDate} Formate of date is not allowed."}, safe=False)
    dataQueryset = Productions.objects.filter(
        ~Q(productiondate__range=[start, end]))
    serializedData = serializers.serialize('json', dataQueryset, fields=(
        'productionid', 'productiondate', 'wellid', 'condensate'))
    return JsonResponse({"status": 200, "title": "OK", "Data": serializedData}, safe=False)


@csrf_exempt
def getCBMProductionData(request):
    if request.method != 'GET':
        return JsonResponse({"status": 405, "title": "Method not allowed", "message": f"{request.method} method not allowed."}, safe=False)
    startDate, endDate = (None,)*2
    startDate = request.GET.get('startDate')
    endDate = request.GET.get('endDate')
    start = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    end = datetime.datetime.strptime(endDate, '%Y-%m-%d')
    if not (start and end):
        return JsonResponse({"status": 403, "title": "FORBIDDEN", "message": f"{startDate} Formate of date is not allowed."}, safe=False)
    dataQueryset = Productions.objects.filter(
        ~Q(productiondate__range=[start, end]))
    serializedData = serializers.serialize('json', dataQueryset, fields=(
        'productionid', 'productiondate', 'wellid', 'cbm'))
    return JsonResponse({"status": 200, "title": "OK", "Data": serializedData}, safe=False)
