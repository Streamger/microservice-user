from django.contrib.auth.models import BaseUserManager

class StreamgerManager(BaseUserManager): #BaseUserManager is a Django-provided base class that serves as a foundation for creating custom manager classes for user models
    use_in_migrations = True
 
    def create_user(self,email,password,registration_method,**extra_fields):
        if not email:
            raise ValueError("The email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)  #Similar to Model.object.create()

        if registration_method == "email":
            user.set_password(password)                    #used to securely set a user's password
        if registration_method == "google":
            pass
        user.save(using=self.db)

        return user

    def create_super_user(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True) 
        extra_fields.setdefault('is_superuser',True)  #Sets the 'is_superuser' key in extra_fields if this key is not already present in the extra_fields
        return self.create_user(email,password,**extra_fields)