from django.shortcuts import render
from rest_framework.views import Response,APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import serializers

from urllib.parse import urlencode

from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import authenticate,login
from django.conf import settings
from django.shortcuts import redirect

from api import serializers
from api.serializers import UserSerializer

from .models import Users,Otp,Streamger,Guideapp
from .models import UserPreference, Language,OTT


from datetime import datetime,timedelta
from django.utils import timezone

from .email import send_email

from .save_utils import Register_Users
from .generate_otp import get_otp

from .authentication.mixins import ApiErrorsMixin, PublicApiMixin
from .authentication.utils import google_get_access_token, google_get_user_info, generate_tokens_for_user

# Create your views here.


class Login(APIView, ApiErrorsMixin, PublicApiMixin):
    permission_classes = [AllowAny]
    login_serializer = serializers.LoginSerializer
    input_serializer = serializers.InputSerializer

    def post(self,request): 
        try:
            login_data = self.login_serializer(data=request.data)
            login_data.is_valid(raise_exception=True)
            data = login_data.validated_data

            #Authenticate is a function inside which we will enter email and password after checking it will return an object of user if the usernama and password is correct
            user = authenticate(request,email=data.get('email'),password = data.get('password'))

            if user is None:
                raise Exception("Incorrect credential")
            
            if not user.is_verified:
                raise Exception("User is not verified")
            
            user_detail = {
                "First_Name":user.first_name,
                "last_name": user.last_name,
                "email":user.email,
                "dob":Streamger.objects.get(user=user).dob if Streamger.objects.filter(user=user).exists() else "",
                "gender":Streamger.objects.get(user=user).gender if Streamger.objects.filter(user=user).exists() else ""
            }
            

            payload = {
                "user":"streamger" if hasattr(Streamger,'objects') and Streamger.objects.filter(user_id=user.id).exists()
                        else "guide" if hasattr(Guideapp,'objects') and Guideapp.objects.filter(user_id=user.id).exists()
                        else None,
                "name": f'{user.first_name} {user.last_name}'

            }


            refresh = RefreshToken.for_user(user)
            refresh.payload.update(payload)

            access_token = str(refresh.access_token)
            refresh_token = str(refresh)


            return Response ({
                "success":True,
                "data":user_detail,
                "token":{
                    "access":access_token,
                    "refresh":refresh_token
                }
            })

        except Exception as e:
            return Response({"success":False,"message":str(e)})

    def get(self,request):

        type = request.query_params.get('type')
        access_token = request.query_params.get('token')
        # input_serializer = self.input_serializer(data=request.GET)
        # input_serializer.is_valid(raise_exception=True)

        # validated_data = input_serializer.validated_data
        # code = validated_data.get('code')
        # error = validated_data.get('error')

        # login_url = f'{settings.BASE_FRONTEND_URL}/login' 
    
        # if error or not code:
        #     params = urlencode({'error': error})
        #     return redirect(f'{login_url}?{params}')

        # redirect_uri = f'{settings.BASE_FRONTEND_URL}/api/auth/callback/google'
        # access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)
        

        try:
            user_instance = Users.objects.get(email=user_data['email'])
            print(user_data)
            access_token, refresh_token = generate_tokens_for_user(user_instance)
            response_data = {
                'user': UserSerializer(user_instance).data,
                'access': str(access_token),
                'refresh': str(refresh_token)
            }
            return Response(response_data)
        
        except Users.DoesNotExist:
            username = user_data['email'].split('@')[0]
            first_name = user_data.get('given_name', '')
            last_name = user_data.get('family_name', '')

            # print("user_data_is",user_data, f'types is {request.query_params}')

            user_instance = Users.objects.create(
                # username=username,
                email=user_data['email'],
                first_name=first_name,
                last_name=last_name,
                registration_method='google',
            )

            data = {
                'gender':"m",
                "dob":"2001-09-20"
            }

            Register_Users(data,type,user_instance)

            access_token, refresh_token = generate_tokens_for_user(user_instance)
            response_data = {
                'user': UserSerializer(user_instance).data,
                'access': str(access_token),
                'refresh': str(refresh_token)
            }
            return Response(response_data)



class Register(APIView):

    permission_classes= [AllowAny]
    registration_serializer = serializers.RegistrationSerializer

    def post(self,request,type):
        try:
            regisration_data = self.registration_serializer(data=request.data)
            regisration_data.is_valid(raise_exception=True)
            data = regisration_data.validated_data

            # print(data)

            #Check whether user is already saved in Users model or not.
            if not (Users.objects.filter(email=data.get('email')).exists()):
                user_instance = Users.objects.create_user(
                    email=data.get('email'),
                    password = data.get('password'),
                    first_name = data.get('first_name'),
                    last_name = data.get('last_name'),
                    middle_name = data.get('middle_name','')
                    )
                
            elif Users.objects.filter(email=data.get('email')).exists():
                raise Exception ("User already exist")

            else:
                user_instance=Users.objects.get(email=data.get('email'))
            
            Register_Users(data,type,user_instance)

            otp = get_otp(data.get('email'),"register")
            # print(otp)
            
            send_email(data.get('email'),otp,"User registration")


      
            return Response({"success":True,"data":"User Created Successfully"})

        
        except Exception as e:
            return Response({"success":False,"message":str(e)})
        
    
class VerifyUser(APIView):
    permission_classes = [AllowAny]
    verify_otp_serializer = serializers.VerifyOTPSerializer

    def post(self,request):

        try:
            otp_data = self.verify_otp_serializer(data=request.data)
            otp_data.is_valid(raise_exception=True)
            data = otp_data.validated_data

            user_instance = Users.objects.get(email=data.get('email'))
            otp_instance = Otp.objects.get(user=user_instance)

            otp_created_time = otp_instance.created_at
            current_time = timezone.now()

            if otp_created_time and (current_time-otp_created_time)>timedelta(minutes=5):
                raise Exception("OTP expired")
            
            if not otp_instance.type=="register":
                raise Exception("Register First")
            
            otp_instance.is_active=False
            otp_instance.save()

            user_instance.is_verified=True
            user_instance.is_active = True
            user_instance.save()



            return Response({"success":True,"data":"User verified successfully"})
        except Exception as e:
            return Response ({"success":False,"message":str(e)})
        

class ForgetPassword(APIView):

    permission_classes = [AllowAny]
    forget_password_serializer = serializers.ForgetPasswordRequestSerializer

    def post(self,request):
        try:
            forget_data = self.forget_password_serializer(data=request.data)
            forget_data.is_valid(raise_exception=True)
            data = forget_data.validated_data


            otp = get_otp(data.get('email'),"forgot")
            # print("yeta")
            send_email(data.get('email'),otp,"Password Reset OTP")

            return Response({"success":True,"message":"Otps sent for forget password"})
        except Exception as e:
            return Response ({"success":False,"message":str(e)})
        
class ReSendOTP(APIView):
    permission_classes = [AllowAny]
    send_otp_serializer = serializers.SendOTPSerializer

    def post(self,request,type):
        try:
            send_otp_data = self.send_otp_serializer(data=request.data)
            send_otp_data.is_valid(raise_exception=True)
            data = send_otp_data.validated_data

            user_instance = Users.objects.get(email = data.get('email'))
            otp_instance = Otp.objects.get(user=user_instance)

            otp_created_time = otp_instance.created_at
            current = timezone.now()

            # if (current-otp_created_time)>timedelta(minutes=5):
            #     send_email(data.get('email'),"Resend Otp","")
            # else:
            #     return Response({"success":False,"message":"Wait for sometime"})

            otp = get_otp(data.get('email'),type)

            send_email(data.get('email'),otp,"Resend Email")

            return Response({"success":True,"data":"Otps resended"})
        except Exception as e:
            return Response({"success":False,"message":str(e)})



class ResetPassword(APIView):

    permission_classes = [AllowAny]
    reset_password_serializer = serializers.ResetPasswordSerializer

    def post(self,request):
        try:
            reset_data = self.reset_password_serializer(data=request.data)
            reset_data.is_valid(raise_exception=True)
            data = reset_data.validated_data

            user_instance = Users.objects.get(email=data.get('email'))
            otp_instance = Otp.objects.get(user=user_instance)

            otp_created_time = otp_instance.created_at
            current_time = timezone.now()

            if otp_created_time and (current_time - otp_created_time) > timedelta(minutes=5):
                # print(current_time,otp_created_time)
                # print(current_time - otp_created_time)
                raise Exception ("OTP is expired")

            # print(otp_instance.type == "forgot" and otp_instance.is_active)
            if not (otp_instance.type == "forgot" and otp_instance.is_active):
                raise Exception ("Click on Forgot password to reset password")
            otp_instance.is_active=False
            otp_instance.save()
            
            user_instance.set_password(data.get('password'))
            user_instance.save()

            # print(data)
            return Response({"success":True,"message":"Password resetted"})
        except Exception as e:
            return Response ({"success":False,"message":str(e)})
        


class GetUserType(APIView):
    # authentication_classes = [TokenAuthentication]

    #permission class ensures that only authenticated users with a valid token can access the view.
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
  
            access_token = AccessToken(str(request.auth))
    
            return Response({"success":True,
                             "user":access_token.payload.get('user'),
                             "user_id":access_token.payload.get('user_id'),
                             "user_name":access_token.payload.get('name')
                             })
        except Exception as e:
            return Response({"success":False,"message":str(e)})
        

class UserPrefences(APIView):
    permission_classes = [IsAuthenticated]

    preference_serializer = serializers.UserPreferenceSerializer

    def post(self, request):
        try:
            preference_data = self.preference_serializer(data=request.data)
            preference_data.is_valid(raise_exception=True)
            data= preference_data.validated_data

            access_token = AccessToken(str(request.auth))
            user = Users.objects.get(id= access_token.payload.get('user_id'))

            language_name = data.get('language',[])
            ott_name = data.get('ott',[])

            preferences = UserPreference.objects.create(
                user=user
            )
            preferences.save()

            ListModels = {
                Language : [str(language).lower() for language in language_name],
                OTT :[str(ott).lower() for ott in ott_name]
            }

            for model,lists in ListModels.items():
                for name in lists:
                    if not model.objects.filter(name=name.lower()).exists():
                        new_instance = model.objects.create(name=name.lower())
                        new_instance.save()

                    model_instance = model.objects.get(name=name)

                    preference_field = model.__name__.lower()


                    #prefernce_instance represents the many-to-many manager associated with the <preference_field> field in the UserPreference
                    # many-to-many manager represents the manager object that provides an interface for interacting with a many-to-many relationship between two models.
                    preference_instance = getattr(preferences,preference_field)  #preference_field is the field inside UserPreference Model

                    #used to add a related instance to a many-to-many relationship.
                    # Use the add method of the many-to-many manager to associate the model_instance
                    # with the preferences instance in the <preference_field> field
                    preference_instance.add(model_instance)



            return Response({"sucess":True, "data":{
                "user_name":f'{user.first_name} {user.last_name}',
                "language": language_name,
                "ott":ott_name
            }})
        

        except Exception as e:
            return Response({"success":False,"message":str(e)})
        
    def get (self, request):
        try:
            access_token = AccessToken(str(request.auth))

            user = Users.objects.get(id = access_token.payload.get('user_id'))

            
            user_preference_instance = UserPreference.objects.get(user=user) if UserPreference.objects.filter(user=user) else None
            data = {
                    "user": f'{user.first_name} {user.last_name}',
                    "language": [language.name for language in user_preference_instance.language.all()] if user_preference_instance else [],
                    "ott": [ott.name for ott in user_preference_instance.ott.all()] if user_preference_instance else []
                    }
           

            return Response({"sucess":True,"data":data})
        except Exception as e:
            return Response({"success":False,"message":str(e)})

