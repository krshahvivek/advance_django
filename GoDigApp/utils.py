from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
import re
from rest_framework import serializers
import datetime as dt
from datetime import date
from datetime import time as dt_time
import time

class Validation:
    def emailValidate(self, **kwargs):
        client_email = kwargs['email']
        try:
            validator = EmailValidator()
            validator(client_email)
            return 1
        except ValidationError as e:
            return 0
        except Exception as e:
            return 0
class Time:
    def generated(self) :
        return dt.datetime.now()

    def current_epoch(self):
        return int(time.time())



class PasswordValidator:
    def __init__(self,Password, min_length=8, max_length=25, at_least_one_lowercase=True, at_least_one_uppercase=True, at_least_one_digit=True, at_least_one_special=True):
        self.min_length = min_length
        self.max_length = max_length
        self.at_least_one_lowercase = at_least_one_lowercase
        self.at_least_one_uppercase = at_least_one_uppercase
        self.at_least_one_digit = at_least_one_digit
        self.at_least_one_special = at_least_one_special
        self.password = Password

    def getPasswordValidation(self):
        message = None
        if len(self.password) < self.min_length:
            message = 'Minimum length 8'
        elif len(self.password) > self.max_length:
            message = 'Mximum length 25'
        elif self.at_least_one_lowercase and not re.search(r'[a-z]', self.password):
            message = 'Password must contain at least one lowercase letter.'
        elif self.at_least_one_uppercase and not re.search(r'[A-Z]', self.password):
            message = 'Password must contain at least one uppercase letter.'
        elif self.at_least_one_digit and not re.search(r'\d', self.password):
            message = 'Password must contain at least one digit.'
        elif self.at_least_one_special and not re.search(r'[~!@#$%^&*()_+}{":?><,./;\'\[\]\\|=]', self.password):
            message = 'Password must contain at least one special character.'
        return message
