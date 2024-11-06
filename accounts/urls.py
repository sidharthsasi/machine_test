from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('password-reset/',change_password_view, name='password_reset'),
    path('profile/<int:id>/', profile_view, name='profile'),
    path('profile/<int:id>/edit/', edit_profile_view, name='edit_profile'),
    path('logout/', logout_view, name='logout'),
]
