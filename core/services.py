from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from datetime import timedelta
from .models import (
    Deposit, DailyEarning, Wallet, Transaction, Referral,
    ROISetting, ReinvestSetting
)
from users.models import User


class EarningService:
    
    @staticmethod
    def calculate_daily_earnings():
        """Calculate daily mining and ROI earnings for all active deposits"""
        today = timezone.now().date()
        
        approved_deposits = Deposit.objects.filter(
            status='approved',
            package__is_active=True
        )
        
        for deposit in approved_deposits:
            if not deposit.approved_at:
                continue
                
            approved_date = deposit.approved_at.date()
            days_elapsed = (today - approved_date).days
            
            if days_elapsed >= deposit.package.duration_days:
                continue
            
            user = deposit.user
            wallet = user.wallet
            
            mining_earning = deposit.package.daily_earning
            
            roi_setting = ROISetting.objects.filter(is_active=True).first()
            if not roi_setting:
                roi_percentage = Decimal('1.0')
            else:
                roi_percentage = (roi_setting.min_percentage + roi_setting.max_percentage) / 2
            
            roi_earning = (wallet.balance * roi_percentage) / 100
            
            existing_mining = DailyEarning.objects.filter(
                user=user,
                earning_type='mining',
                earned_date=today,
                deposit=deposit
            ).exists()
            
            if not existing_mining:
                DailyEarning.objects.create(
                    user=user,
                    earning_type='mining',
                    amount=mining_earning,
                    deposit=deposit,
                    earned_date=today
                )
                
                wallet.mining_income += mining_earning
                Transaction.objects.create(
                    user=user,
                    transaction_type='mining',
                    amount=mining_earning,
                    description=f'Daily mining from {deposit.package.name}'
                )
            
            existing_roi = DailyEarning.objects.filter(
                user=user,
                earning_type='roi',
                earned_date=today,
                deposit=deposit
            ).exists()
            
            if not existing_roi and roi_earning > 0:
                DailyEarning.objects.create(
                    user=user,
                    earning_type='roi',
                    amount=roi_earning,
                    deposit=deposit,
                    earned_date=today
                )
                
                wallet.roi_earnings += roi_earning
                Transaction.objects.create(
                    user=user,
                    transaction_type='roi',
                    amount=roi_earning,
                    description=f'Daily ROI earning ({roi_percentage}%)'
                )
            
            reinvest_setting = ReinvestSetting.objects.filter(is_active=True).first()
            if reinvest_setting and reinvest_setting.percentage > 0:
                total_daily_earning = mining_earning + roi_earning
                reinvest_amount = (total_daily_earning * reinvest_setting.percentage) / 100
                
                if reinvest_amount > 0:
                    existing_reinvest = DailyEarning.objects.filter(
                        user=user,
                        earning_type='reinvest',
                        earned_date=today,
                        deposit=deposit
                    ).exists()
                    
                    if not existing_reinvest:
                        DailyEarning.objects.create(
                            user=user,
                            earning_type='reinvest',
                            amount=reinvest_amount,
                            deposit=deposit,
                            earned_date=today
                        )
                        
                        wallet.balance += reinvest_amount
                        Transaction.objects.create(
                            user=user,
                            transaction_type='reinvest',
                            amount=reinvest_amount,
                            description=f'Auto reinvest ({reinvest_setting.percentage}%)'
                        )
            
            total_earning = mining_earning + roi_earning
            
            if reinvest_setting and reinvest_setting.percentage > 0:
                available_earning = total_earning - ((total_earning * reinvest_setting.percentage) / 100)
            else:
                available_earning = total_earning
            
            wallet.balance += available_earning
            wallet.last_earning_date = today
            wallet.save()
    
    @staticmethod
    def process_referral_earnings():
        """Process referral earnings for active referrals"""
        today = timezone.now().date()
        
        referrals = Referral.objects.all()
        
        for referral in referrals:
            referrer = referral.referrer
            referred_user = referral.referral_user
            
            active_deposits = Deposit.objects.filter(
                user=referred_user,
                status='approved'
            ).exists()
            
            if not active_deposits:
                continue
            
            today_earnings = DailyEarning.objects.filter(
                user=referred_user,
                earned_date=today
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            if today_earnings > 0:
                commission_percentage = EarningService.get_referral_commission(referral.level)
                referral_earning = (today_earnings * commission_percentage) / 100
                
                if referral_earning > 0:
                    existing = DailyEarning.objects.filter(
                        user=referrer,
                        earning_type='referral',
                        earned_date=today
                    ).exists()
                    
                    if not existing:
                        DailyEarning.objects.create(
                            user=referrer,
                            earning_type='referral',
                            amount=referral_earning,
                            earned_date=today
                        )
                        
                        wallet = referrer.wallet
                        wallet.referral_earnings += referral_earning
                        wallet.balance += referral_earning
                        wallet.save()
                        
                        referral.total_earned += referral_earning
                        referral.save()
                        
                        Transaction.objects.create(
                            user=referrer,
                            transaction_type='referral',
                            amount=referral_earning,
                            description=f'Referral commission from {referred_user.email} ({commission_percentage}%)'
                        )
    
    @staticmethod
    def get_referral_commission(level):
        """Get commission percentage based on referral level"""
        commissions = {
            1: Decimal('5'),
            2: Decimal('2'),
            3: Decimal('1'),
        }
        return commissions.get(level, Decimal('0'))
    
    @staticmethod
    def create_referral_on_deposit(user, deposit):
        """Create referral relationship when user makes their first deposit"""
        if user.referred_by:
            referrer = user.referred_by
            
            ref, created = Referral.objects.get_or_create(
                referrer=referrer,
                referral_user=user,
                defaults={'level': 1}
            )
            
            if created:
                ref.commission_percentage = EarningService.get_referral_commission(1)
                ref.save()
    
    @staticmethod
    def get_user_dashboard_stats(user):
        """Get comprehensive dashboard statistics for a user"""
        wallet = user.wallet
        
        active_packages = Deposit.objects.filter(
            user=user,
            status='approved'
        ).count()
        
        total_invested = Deposit.objects.filter(
            user=user,
            status='approved'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        total_withdrawals = Withdrawal.objects.filter(
            user=user,
            status='completed'
        ).aggregate(Sum('net_amount'))['net_amount__sum'] or Decimal('0.00')
        
        referral_count = user.referrals_given.count()
        
        today_earnings = DailyEarning.objects.filter(
            user=user,
            earned_date=timezone.now().date()
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        return {
            'balance': wallet.balance,
            'total_earnings': wallet.total_earnings,
            'mining_income': wallet.mining_income,
            'roi_earnings': wallet.roi_earnings,
            'referral_earnings': wallet.referral_earnings,
            'active_packages': active_packages,
            'total_invested': total_invested,
            'total_withdrawals': total_withdrawals,
            'referral_count': referral_count,
            'today_earnings': today_earnings,
            'last_earning_date': wallet.last_earning_date,
        }
