Employee Management System

This Employee Management System is designed to allow admins to create and manage employee profiles, with the ability to dynamically add custom fields to each profile. It uses Django, Django REST Framework (DRF), and JWT authentication for secure user management.



1. Clone the Repository
git clone https://github.com/sidharthsasi/machine_test.git
cd veuz

2. Install Dependencies
pip install -r requirements.txt

3. Migrate the Database
python manage.py makemigrations
python manage.py migrate

4. Create Superuser (For Admin Access)
python manage.py createsuperuser

5. Run the Development Server
python manage.py runserver
