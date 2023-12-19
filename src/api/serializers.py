from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    gender = serializers.CharField(required=False)
    age = serializers.CharField(required=False)

    password = serializers.CharField(required=True)
    reenter_password = serializers.CharField(required=True)


    #validate() method is a special method recognized by the validation process.
    #It is automatically invoked as part of the validation cycle when calling .is_valid() on the serializer instance.
    def validate(self, attrs):                                              #This attrs argument represents the dictionary of serialized data that is being validated.                                 
        if attrs['password'] != attrs['reenter_password']:                  #The attrs argument contains the serialized data extracted from the input passed to the serialize
            raise serializers.ValidationError("Password didn't matched")
        
        return attrs

   