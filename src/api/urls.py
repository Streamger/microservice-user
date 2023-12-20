from django.urls import path
from .views import Register,Verify_Otp

urlpatterns = [
    path('register/<str:type>',Register.as_view(),name="register"),
    path('verifyotp/',Verify_Otp.as_view(),name="register_otp")
]
