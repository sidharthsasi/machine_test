
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from accounts.models import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from django.core.validators import validate_email

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Check for missing email or password
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': "Login successful"
            }, status=status.HTTP_200_OK)
        
        # Handle invalid credentials
        return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        # Check if the refresh token is provided
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Attempt to blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token

            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        
        except ValidationError:
            # Catch validation errors (e.g., if the token is invalid)
            return Response(
                {"error": "Invalid token. Please provide a valid refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Handle any unexpected errors
            return Response(
                {"error": "An error occurred during logout. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        # Check if old and new passwords are provided
        if not old_password:
            return Response({"error": "Old password is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the old password is correct
        if not user.check_password(old_password):
            return Response({"error": "The old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the new password
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            # Provide detailed feedback if password does not meet validation criteria
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        
        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully!"}, status=status.HTTP_200_OK)
    


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile  # Assumes OneToOne relation exists
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)



        
class EmployeeProfileCreateUpdateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
      
        serializer = EmployeeProfileSerializer(data=request.data)
        if serializer.is_valid():
            employee_profile = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, employee_id):
        try:
            employee_profile = EmployeeProfile.objects.get(id=employee_id)
        except EmployeeProfile.DoesNotExist:
          
            return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)

       
        serializer = EmployeeProfileSerializer(employee_profile, data=request.data, partial=True)
        if serializer.is_valid():
            updated_profile = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeProfileDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, employee_id):
        try:
            employee_profile = EmployeeProfile.objects.get(id=employee_id)
        except EmployeeProfile.DoesNotExist:
            return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeProfileSerializer(employee_profile)
        return Response(serializer.data)
