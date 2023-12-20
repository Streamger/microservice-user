from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.exceptions import ObjectDoesNotExist
from .models import Otp,Users


def send_email(email,subject):

    try:
        otp= random.randint(100000,999999)
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        message = f'Your otp for email verification is {otp}'

        send_mail(subject,message,from_email,to_email)

        otp_instance = Otp.objects.get(user__email=email)
        otp_instance.otp = otp
        otp_instance.save()  #Updates the otp of certain user if the otp is already assigned to user

    except ObjectDoesNotExist:
        otp_instance = Otp.objects.create(
            otp=otp,
            user=Users.objects.get(email=email)
        )
        otp_instance.save()
     


    except Exception as e:
        
        raise Exception (str(e))

