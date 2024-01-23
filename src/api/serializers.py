from rest_framework import serializers

from .models import Otp

from django.contrib.auth import get_user_model    #Return the currently active user model
User=get_user_model()


class UserSerializer(serializers.ModelSerializer): 
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email']


class InputSerializer(serializers.Serializer):
       code = serializers.CharField(required=False)
       error = serializers.CharField(required=False)


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    gender = serializers.CharField(required=True, max_length=1)
    dob = serializers.DateField(required=True)
 
    password = serializers.CharField(required=True)
    reenter_password = serializers.CharField(required=True)


    #validate() method is a special method recognized by the validation process.
    #It is automatically invoked as part of the validation cycle when calling .is_valid() on the serializer instance.
    def validate(self, attrs):                                              #This attrs argument represents the dictionary of serialized data that is being validated.                                 
        if attrs.get('password') != attrs.get('reenter_password'):                  #The attrs argument contains the serialized data extracted from the input passed to the serialize
            raise serializers.ValidationError("Password didn't matched")
        
        return attrs
    

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=128)
    otp = serializers.CharField(required=True, max_length=6)

    def validate(self,attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        otp = attrs.get('otp')

    

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise Exception("User not found")
        
        if not user.check_password(password):
            raise Exception("Password didn't match")
        
        if not Otp.objects.filter(user=user,otp=otp).exists():
            raise Exception("OTP didn't match")
        
        return attrs
    

class ForgetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')

        if not User.objects.filter(email=email).exists():
            raise Exception("Email does not exists")
        
        return attrs
    
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self,attrs):
        email = attrs.get('email')

        if not User.objects.filter(email=email).exists():
            raise Exception("Email does not exists")
        
        # if User.objects.filter(email=email).exists() and User.objects.get(email=email).is_verified:
        #     raise serializers.ValidationError("User is already verifeid")
        
        return attrs

     

class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6,required=True)
    email = serializers.EmailField(required=True)

    password = serializers.CharField(max_length=128,required=True)
    reenter_password = serializers.CharField(max_length=128, required=True)

    def validate(self, attrs):
        otp = attrs.get('otp')
        email = attrs.get('email')
        if attrs.get('password') != attrs.get('reenter_password'):
            raise Exception("Password didn't match")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise Exception("User does not exists")
        
        if not Otp.objects.filter(user=user, otp=otp).exists():
            raise Exception("OTP didn't match")
        
        return attrs
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        email = attrs.get('email')

        if not User.objects.filter(email=email).exists():
            raise Exception("User not found")
        
        return attrs


   
class UserPreferenceSerializer(serializers.Serializer):
    language = serializers.ListField(required=False)
    ott  = serializers.ListField(required = False)