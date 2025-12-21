import os
import django
import getpass
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()


def main():
    print('=== Create Admin Superuser ===\n')
    
    email = input('Email: ').strip()
    
    if User.objects.filter(email=email).exists():
        print(f'Admin with email {email} already exists')
        return False
    
    username = input('Username: ').strip()
    
    if User.objects.filter(username=username).exists():
        print(f'Admin with username {username} already exists')
        return False
    
    first_name = input('First Name: ').strip()
    last_name = input('Last Name: ').strip()
    
    while True:
        password = getpass.getpass('Password (min 8 characters): ')
        password_confirm = getpass.getpass('Confirm Password: ')
        
        if password != password_confirm:
            print('❌ Passwords do not match. Try again.\n')
            continue
        
        if len(password) < 8:
            print('❌ Password must be at least 8 characters long.\n')
            continue
        
        break
    
    try:
        admin = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        print(f'\n✓ Admin account created successfully!')
        print(f'  Email: {admin.email}')
        print(f'  Username: {admin.username}')
        print(f'  Name: {admin.first_name} {admin.last_name}')
        print(f'\nLogin to the admin panel with:')
        print(f'  Username: {admin.username}')
        print(f'  Password: (the password you entered)')
        return True
        
    except Exception as e:
        print(f'❌ Error creating admin: {str(e)}')
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
