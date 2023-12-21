from django.urls import path
from .views import Register,Verify_Otp,ForgetPassword,ResetPassword,Login

urlpatterns = [
    path('register/<str:type>',Register.as_view(),name="register"),
    path('verifyotp/',Verify_Otp.as_view(),name="register_otp"),
    path('forgetpassword/',ForgetPassword.as_view(),name="forget_password"),
    path('resetpassword/',ResetPassword.as_view(),name="Reset Password"),
    path('login/',Login.as_view(),name="Login")
]
