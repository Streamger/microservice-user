from .models import Users
from .models import Streamger,Guideapp

from.models import Otp,Wishlist,Avatar
from django.http import Http404



def Register_Users(data, type, user_instance):

    user_type = {
        'streamger':Streamger,
        'guide':Guideapp
    }
    
    try:
        # if type == 'streamger':
        #      #Check whether user is already assigned to Streamger or not. i.e a user is streamger user or not.
        #     #If a user is already a streamger user then do nothing
        #     if not Streamger.objects.filter(user=user_instance).exists():
        #         streamger_instance = Streamger.objects.create(
        #             user = user_instance,
        #             age = data.get('age'),
        #             gender = data.get('gender')
        #         )

        #         streamger_instance.save()

        user_type_instance = user_type.get(type)
        if not user_type_instance:
            raise Http404("Not Found")
        
        print('here',user_type_instance)
        if not user_type_instance.objects.filter(user=user_instance).exists():
            user_type_instance = user_type_instance.objects.create(
                user = user_instance
            )
            if type == "streamger":
                user_type_instance.age = data.get('age')
                user_type_instance.gender = data.get('gender')

            user_type_instance.save()


        


    except Exception as e:
     
        raise Exception (str(e))