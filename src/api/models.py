from django.db import models
from django.contrib.auth.models import AbstractBaseUser,AbstractUser
from .managers import StreamgerManager
from datetime import timedelta


# Create your models here.
class Users (AbstractUser,AbstractBaseUser):

    username=None
    is_superuser=None
    date_joined=None
    last_login=None

    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL,null=True, blank=True)
    email = models.EmailField(unique=True)
    password= models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects = StreamgerManager()  #We can use this like new_user = User.objects.create_user(email='example@example.com', password='password123')
 
    def __str__(self):
        return self.email
    

class Streamger (models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)   #In this model user will be primary key instead of id
    dob = models.DateField()
    GENDER_CHOICES = [
        ('M','Male'),
        ('F','Female'),
        ('O','Other')
    ]
    gender = models.CharField(max_length=1,choices=GENDER_CHOICES)


class Guideapp (models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    
  
    
    
class Wishlist(models.Model):
    content_id = models.PositiveBigIntegerField()
    streamger = models.ForeignKey(Streamger, on_delete=models.CASCADE) # streamger field establishes a many-to-one relationship with the Streamger model. Each wishlist is associated with a single streamger through this field.

    def __str__(self):
        return self.content_id
    
    
class Avatar(models.Model):
    streamger = models.ForeignKey(Streamger,on_delete=models.CASCADE)

    saved_location= models.ImageField(upload_to="avatars/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self): 
        return self.streamger.user.first_name
    
class Otp(models.Model):
    otp = models.CharField(max_length=6, null=True, blank=True)

    user = models.OneToOneField(Users,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()


    type = models.CharField(max_length=255)
    # once validate set this to false so that this otp cant be used again. if is active true then only validate otp initially
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.otp
    
    

