# employees/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
import re
from django.core.validators import validate_email
from django.contrib.auth import logout

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid email or password'})
    return render(request, 'accounts/login.html')



def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        # Validation patterns
        name_pattern = r'^[A-Za-z]+$'  # Only letters allowed, no digits or symbols
        password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'  # Minimum 8 characters, 1 uppercase, 1 digit, 1 special character

        # First name validation
        if not re.match(name_pattern, first_name):
            messages.error(request, "First name should contain only letters.")
            return redirect('register')

        # Last name validation
        if not re.match(name_pattern, last_name):
            messages.error(request, "Last name should contain only letters.")
            return redirect('register')

        # Username validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return redirect('register')

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please use a different email.")
            return redirect('register')

        # Password validation
        if not re.match(password_pattern, password):
            messages.error(request, "Password must be at least 8 characters, include an uppercase letter, a number, and a symbol.")
            return redirect('register')

        # If all validations pass, create user
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        
        messages.success(request, "Registration successful")
        return redirect('login')  

    return render(request, 'accounts/register.html')



@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if old password is correct
        if not request.user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
            return redirect('change_password')

        # Validate new password
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
        
        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            messages.error(request, e.messages)
            return redirect('change_password')

        # Set new password
        request.user.set_password(new_password)
        request.user.save()

        # Update session to keep the user logged in
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Your password was successfully updated!')
        return redirect('profile')  # Redirect to the profile page or another appropriate view

    return render(request, 'accounts/change_password.html')



@login_required
def profile_view(request, id):
    profile = get_object_or_404(UserProfile, id=id, user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile, 'user': request.user})

@login_required
def edit_profile_view(request, id):
    # Fetch the profile based on the given id
    profile = get_object_or_404(UserProfile, id=id, user=request.user)
    
    if request.method == 'POST':
        # Update profile fields based on POST data
        profile.designation = request.POST.get('designation')
        profile.experience = request.POST.get('experience')
        profile.salary = request.POST.get('salary')
        profile.qualification = request.POST.get('qualification')
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.address = request.POST.get('address')
        profile.skills = request.POST.get('skills')
        profile.contact_number = request.POST.get('contact_number')
        profile.emergency_contact = request.POST.get('emergency_contact')
        
        # Handle profile picture upload
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']
        
        # Save the updated profile
        profile.save()
        
        # Redirect to the profile view or any appropriate page
        return redirect('profile', id=profile.user.id)
    
    # Render the profile edit template with the profile data
    return render(request, 'accounts/edit_profile.html', {'profile': profile})


def logout_view(request):
    logout(request)
    return redirect('login')