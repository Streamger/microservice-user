from django.shortcuts import render
from rest_framework.views import Response,APIView
from rest_framework.permissions import AllowAny
# from rest_framework import serializers
from api import serializers
from .models import Users,Otp

from datetime import datetime,timedelta
from django.utils import timezone

from .email import send_email

from .save_utils import Register_Users


# Create your views here.

class Register(APIView):

    permission_classes= [AllowAny]
    registration_serializer = serializers.RegistrationSerializer



    def post(self,request,type):
        try:
            regisration_data = self.registration_serializer(data=request.data)
            regisration_data.is_valid(raise_exception=True)
            data = regisration_data.validated_data

            #Check whether user is already saved in Users model or not.
            if not Users.objects.filter(email=data.get('email')).exists():
                user_instance = Users.objects.create_user(
                    email=data.get('email'),
                    password = data.get('password'),
                    first_name = data.get('first_name'),
                    last_name = data.get('last_name'),
                    middle_name = data.get('middle_name','')
                    )
            else:
                user_instance=Users.objects.get(email=data.get('email'))
            
            Register_Users(data,type,user_instance)
            
            send_email(data.get('email'),"User registration")


      
            return Response({"success":True})

        
        except Exception as e:
            return Response({"error":str(e)})
        

    
class Verify_Otp(APIView):
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
            
            user_instance.is_verified=True
            user_instance.is_active = True
            user_instance.save()



            return Response({"success":True,"message":"User created successfully"})
        except Exception as e:
            return Response ({"error":str(e)})
        

class ForgetPassword(APIView):

    permission_classes = [AllowAny]
    forget_password_serializer = serializers.ForgetPasswordSerializer

    def post(self,request):
        try:
            forget_data = self.forget_password_serializer(data=request.data)
            forget_data.is_valid(raise_exception=True)
            data = forget_data.validated_data

            send_email(data.get('email'),"Password Reset OTP")

            return Response({"success":True})
        except Exception as e:
            return Response ({"error":str(e)})

