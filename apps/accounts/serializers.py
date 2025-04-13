from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from .models import FarmerProfile, SupplierProfile, OfftakerProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'is_verified']
        read_only_fields = ['is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 
                  'last_name', 'user_type', 'phone_number']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user_type = validated_data.get('user_type')
        validated_data.pop('password2')
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            user_type=user_type,
            phone_number=validated_data.get('phone_number', '')
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        # Create corresponding profile based on user type
        if user_type == User.UserType.FARMER:
            FarmerProfile.objects.create(user=user)
        elif user_type == User.UserType.SUPPLIER:
            SupplierProfile.objects.create(user=user, company_name=f"{user.first_name}'s Company")
        elif user_type == User.UserType.OFFTAKER:
            OfftakerProfile.objects.create(user=user, company_name=f"{user.first_name}'s Company")
            
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)