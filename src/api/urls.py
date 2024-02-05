from django.urls import path
from .views import Register,VerifyUser,ForgetPassword,ResetPassword,Login,GetUserType,ReSendOTP,UserPrefences
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('register/<str:type>',Register.as_view(),name="register"),
    path('verifyotp/',VerifyUser.as_view(),name="register_otp"),
    path('forgetpassword/',ForgetPassword.as_view(),name="forget_password"),
    path('resetpassword/',ResetPassword.as_view(),name="Reset Password"),
    path('login/',Login.as_view(),name="Login"),
    path('resendotp/<str:type>',ReSendOTP.as_view(),name="resend"),

    #TokenObtainPairView is responsible for generating access and refresh token pairs upon successful authentication by the user.
    #It expects a POST request with valid user credentials (usually username(in our case email) and password) and, upon successful validation, returns a response containing both the access token and refresh token.

    # path('token/',TokenObtainPairView.as_view(), name="token_obtain_pair"),



    # When an access token expires, the client can use the refresh token to obtain a new access token without needing to re-authenticate the user.
    path('refresh/',TokenRefreshView.as_view(),name="token_refresh_views"),

    path('usertype/',GetUserType.as_view(),name='get user type'),

    path('preference/', UserPrefences.as_view(), name='user_preference')
]
