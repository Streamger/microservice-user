from .models import Users
from .models import Streamger

from.models import Otp,Wishlist,Avatar



def Register_Users(data, type, user_instance):
    
    try:
        if type == 'streamger':
            

             #Check whether user is already assigned to Streamger or not. i.e a user is streamger user or not.
            #If a user is already a streamger user then do nothing
            if not Streamger.objects.filter(user=user_instance).exists():
                streamger_instance = Streamger.objects.create(
                    user = user_instance,
                    age = data.get('age'),
                    gender = data.get('gender')
                )

                streamger_instance.save()
        


    except Exception as e:
     
        raise Exception (str(e))