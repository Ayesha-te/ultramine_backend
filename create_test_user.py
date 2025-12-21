import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from rest_framework.authtoken.models import Token

email = 'test@example.com'
password = 'password123'

user = User.objects.create_user(
    username=email,
    email=email,
    first_name='Test',
    last_name='User',
    phone='1234567890',
    password=password,
    is_staff=True,
    is_superuser=True
)

token, created = Token.objects.get_or_create(user=user)

print(f"User created successfully!")
print(f"Email: {email}")
print(f"Password: {password}")
print(f"Token: {token.key}")
