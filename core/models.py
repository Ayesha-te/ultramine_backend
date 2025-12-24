from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta
from decimal import Decimal
from users.models import User

class MiningPackage(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(500)])
    daily_earning = models.DecimalField(max_digits=12, decimal_places=2)
    duration_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ₨{self.price}"


class Deposit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    package = models.ForeignKey(MiningPackage, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('crypto', 'Cryptocurrency'),
        ('cod', 'Cash on Delivery'),
    ])
    transaction_id = models.CharField(max_length=100, blank=True)
    deposit_proof = models.URLField(max_length=500, null=True, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_deposits')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - ₨{self.amount}"

    @property
    def remaining_days(self):
        if not self.package:
            return 0
        if self.status == 'approved' and self.approved_at:
            elapsed = (timezone.now() - self.approved_at).days
            remaining = self.package.duration_days - elapsed
            return max(0, remaining)
        return self.package.duration_days


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    mining_income = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    roi_earnings = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    referral_earnings = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    signup_bonus = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    last_earning_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - ₨{self.balance}"

    @property
    def total_earnings(self):
        return self.mining_income + self.roi_earnings + self.referral_earnings + self.signup_bonus


class DailyEarning(models.Model):
    EARNING_TYPE = [
        ('mining', 'Mining Income'),
        ('roi', 'ROI Earnings'),
        ('referral', 'Referral Earnings'),
        ('reinvest', 'Auto Reinvest'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_earnings')
    earning_type = models.CharField(max_length=20, choices=EARNING_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.ForeignKey(Deposit, null=True, blank=True, on_delete=models.SET_NULL)
    earned_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-earned_date']
        unique_together = ['user', 'earning_type', 'earned_date', 'deposit']

    def __str__(self):
        return f"{self.user.email} - {self.earning_type} - ₨{self.amount}"


class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('deposit', 'Deposit'),
        ('mining', 'Mining Income'),
        ('roi', 'ROI Earnings'),
        ('referral', 'Referral Earnings'),
        ('withdrawal', 'Withdrawal'),
        ('reinvest', 'Auto Reinvest'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='completed')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - ₨{self.amount}"


class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_given')
    referral_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by_users')
    level = models.IntegerField(default=1)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['referrer', 'referral_user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.referrer.email} → {self.referral_user.email} (Level {self.level})"


class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1000)])
    withdrawal_method = models.CharField(max_length=50, choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('easypaisa', 'EasyPaisa'),
        ('jazzcash', 'JazzCash'),
    ])
    withdrawal_account = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_withdrawals')
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tax_amount:
            tax_setting = WithdrawalTaxSetting.objects.filter(is_active=True).first()
            tax_rate = (tax_setting.percentage / 100) if tax_setting else Decimal(0.20)
            self.tax_amount = self.amount * tax_rate
            self.net_amount = self.amount - self.tax_amount
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - ₨{self.amount} - {self.status}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image = models.URLField(max_length=500, null=True, blank=True)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD = [
        ('cod', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    shipping_address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    customer_name = models.CharField(max_length=200, blank=True)
    txid_proof = models.URLField(max_length=500, null=True, blank=True)
    txid = models.CharField(max_length=200, blank=True, verbose_name="Transaction ID for Payment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.product.price * self.quantity
        
        discount = (self.total_price * self.discount_percentage) / 100
        self.final_price = (self.total_price - discount) + self.delivery_charges
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"


class ROISetting(models.Model):
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.8)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=1.2)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ROI: {self.min_percentage}% - {self.max_percentage}%"


class ReinvestSetting(models.Model):
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=30)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Auto Reinvest: {self.percentage}%"


class WithdrawalTaxSetting(models.Model):
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Withdrawal Tax: {self.percentage}%"
