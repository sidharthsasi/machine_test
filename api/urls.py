# api/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api-register'),
    path('login/', LoginAPIView.as_view(), name='api-login'),
    path('profile/', UserProfileAPIView.as_view(), name='api-profile'),
    path('profile/change_password/', ChangePasswordAPIView.as_view(), name='api-change-password'),
    path('logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('employee/', EmployeeProfileCreateUpdateAPIView.as_view(), name='create_update_employee_profile'),
    path('employee/<int:employee_id>/', EmployeeProfileDetailAPIView.as_view(), name='employee_profile_detail'),
    path('employee/<int:employee_id>/update/', EmployeeProfileCreateUpdateAPIView.as_view(), name='update_employee_profile'),
   
]
