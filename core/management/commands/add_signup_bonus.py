from django.core.management.base import BaseCommand
from core.models import Wallet, Transaction
from users.models import User


class Command(BaseCommand):
    help = 'Add ₨100 signup bonus to all existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        bonus_amount = 100
        count = 0
        
        for user in users:
            wallet, created = Wallet.objects.get_or_create(user=user)
            
            transaction_exists = Transaction.objects.filter(
                user=user,
                transaction_type='deposit',
                description='Signup bonus'
            ).exists()
            
            if not transaction_exists:
                wallet.signup_bonus += bonus_amount
                wallet.balance += bonus_amount
                wallet.save()
                
                Transaction.objects.create(
                    user=user,
                    transaction_type='deposit',
                    amount=bonus_amount,
                    status='completed',
                    description='Signup bonus'
                )
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Added bonus to {user.email}'))
        
        self.stdout.write(self.style.SUCCESS(f'Total users updated: {count}'))
