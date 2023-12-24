import random
from .models import Otp,Users
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
def get_otp(email,type):


    otp= random.randint(100000,999999)

    try:
        otp_instance = Otp.objects.get(user__email=email,type=type)

        if otp_instance.expires_at<timezone.now():
            otp_instance.otp=otp
            otp_instance.is_active=True
            otp_instance.expires_at = timezone.now()+timedelta(minutes=5)
            otp_instance.save()
            return otp
        else:

            raise Exception("Otp has been sent. Wait for 5 minutes to resend")
       

    except ObjectDoesNotExist:

        if not Otp.objects.filter(user__email=email).exists():
            otp_instance = Otp.objects.create(
                otp=otp,
                is_active=True,
                type=type,
                expires_at = timezone.now()+timedelta(minutes=5),
                user=Users.objects.get(email=email)
            )
        else:
            otp_instance=Otp.objects.get(user__email=email)
            otp_instance.otp=otp
            otp_instance.is_active=True
            otp_instance.type=type
            otp_instance.expires_at = timezone.now()+timedelta(minutes=5)

        otp_instance.save()
   
        return otp
    except Exception as e:
     
        raise Exception (str(e))