from django.shortcuts import render
from rest_framework.views import Response,APIView
from rest_framework.permissions import AllowAny
from rest_framework import serializers as s
from api import serializers

# Create your views here.

class Register(APIView):

    permission_classes= [AllowAny]
    registration_serializer = serializers.RegistrationSerializer

    def post(self,request):
        try:
            regisration_data = self.registration_serializer(data=request.data)
            regisration_data.is_valid(raise_exception=True)
            data = regisration_data.validated_data
            print(data)
            return Response({"success":True})
        
        except Exception as e:
            return Response({"error":str(e)})
