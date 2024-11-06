# api/serializers.py

from rest_framework import serializers
from accounts.models import *
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            "min_length": "Password must be at least 8 characters long."
        }
    )
    email = serializers.EmailField(
        error_messages={
            "invalid": "Enter a valid email address."
        }
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')

    def validate_email(self, value):
        """Check that the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_password(self, value):
        """Ensure password has at least one uppercase letter, one number, and one symbol."""
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate_first_name(self, value):
        """Ensure first name is not empty and has valid characters."""
        if not value.isalpha():
            raise serializers.ValidationError("First name can only contain alphabetic characters.")
        return value

    def validate_last_name(self, value):
        """Ensure last name is not empty and has valid characters."""
        if value and not value.isalpha():
            raise serializers.ValidationError("Last name can only contain alphabetic characters.")
        return value

    def create(self, validated_data):
        """Create a new user with encrypted password."""
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    profile_pic = serializers.ImageField(required=False)
    designation = serializers.CharField(required=True, max_length=100, error_messages={
        "required": "Designation is required.",
        "max_length": "Designation cannot exceed 100 characters."
    })
    experience = serializers.IntegerField(required=True, min_value=0, error_messages={
        "required": "Experience is required.",
        "min_value": "Experience must be a positive number."
    })
    salary = serializers.DecimalField(required=True, max_digits=10, decimal_places=2, error_messages={
        "required": "Salary is required.",
        "max_digits": "Salary cannot exceed 10 digits."
    })
    date_of_birth = serializers.DateField(required=True, error_messages={
        "required": "Date of birth is required.",
        "invalid": "Date of birth must be a valid date format (YYYY-MM-DD)."
    })
    contact_number = serializers.CharField(required=True, max_length=12, error_messages={
        "required": "Contact number is required.",
        "max_length": "Contact number cannot exceed 12 digits."
    })
    emergency_contact = serializers.CharField(required=False, max_length=12, error_messages={
        "max_length": "Emergency contact cannot exceed 12 digits."
    })
    skills = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'profile_pic', 'designation', 'experience', 'salary',
            'qualification', 'date_of_birth', 'address', 'skills', 
            'contact_number', 'emergency_contact'
        ]

    def validate_contact_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Contact number must contain only digits.")
        return value

    def validate_emergency_contact(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Emergency contact must contain only digits.")
        return value

    def validate(self, data):
        if data.get('experience', 0) < 0:
            raise serializers.ValidationError({"experience": "Experience must be zero or a positive number."})
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    


class CustomFieldSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(max_length=50)
    field_value = serializers.CharField(max_length=128)

    class Meta:
        model = CustomField
        fields = ['field_name', 'field_value']

    def validate_field_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Field name cannot be empty.")
        if not re.match(r'^[a-zA-Z0-9_ ]*$', value):
            raise serializers.ValidationError("Field name can only contain letters, numbers, spaces, and underscores.")
        return value

    def validate_field_value(self, value):
        if not value.strip():
            raise serializers.ValidationError("Field value cannot be empty.")
        return value




class EmployeeProfileSerializer(serializers.ModelSerializer):
    custom_fields = CustomFieldSerializer(many=True, required=False)

    class Meta:
        model = EmployeeProfile
        fields = ['employee', 'phone_number', 'position', 'custom_fields']

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number should only contain digits.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def validate_position(self, value):
        if not value.strip():
            raise serializers.ValidationError("Position cannot be empty.")
        return value

    def create(self, validated_data):
        custom_fields_data = validated_data.pop('custom_fields', [])
        employee_profile = EmployeeProfile.objects.create(**validated_data)
        self._update_custom_fields(employee_profile, custom_fields_data)
        return employee_profile

    def update(self, instance, validated_data):
        custom_fields_data = validated_data.pop('custom_fields', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._update_custom_fields(instance, custom_fields_data)
        return instance

    def _update_custom_fields(self, employee_profile, custom_fields_data):
        for field_data in custom_fields_data:
            if CustomField.objects.filter(employee=employee_profile, field_name=field_data['field_name']).exists():
                raise serializers.ValidationError(f"Field name '{field_data['field_name']}' already exists for this employee.")
            
            CustomField.objects.update_or_create(
                employee=employee_profile,
                field_name=field_data['field_name'],
                defaults={'field_value': field_data['field_value']}
            )