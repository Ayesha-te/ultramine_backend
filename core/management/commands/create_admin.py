from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser/admin account for the admin panel'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Admin Account Creation ==='))
        
        email = input('Email: ').strip()
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Admin with email {email} already exists'))
            return
        
        username = input('Username: ').strip()
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Admin with username {username} already exists'))
            return
        
        first_name = input('First Name: ').strip()
        last_name = input('Last Name: ').strip()
        
        while True:
            password = getpass.getpass('Password: ')
            password_confirm = getpass.getpass('Confirm Password: ')
            
            if password != password_confirm:
                self.stdout.write(self.style.WARNING('Passwords do not match. Try again.'))
                continue
            
            if len(password) < 8:
                self.stdout.write(self.style.WARNING('Password must be at least 8 characters long.'))
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
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Admin account created successfully!'))
            self.stdout.write(f'  Email: {admin.email}')
            self.stdout.write(f'  Username: {admin.username}')
            self.stdout.write(f'  Name: {admin.first_name} {admin.last_name}')
            self.stdout.write(f'\nLogin to the admin panel with:')
            self.stdout.write(f'  Username: {admin.username}')
            self.stdout.write(f'  Password: (the password you entered)')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin: {str(e)}'))
