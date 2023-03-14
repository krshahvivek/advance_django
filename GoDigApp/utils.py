from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
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
            raise "Some error Occured :" + e

class Time:
    def generated(self) :
        return dt.datetime.now()

    def current_epoch(self):
        return int(time.time())

