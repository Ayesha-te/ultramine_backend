from django.contrib import admin
from .models import (
    MiningPackage, Deposit, Wallet, DailyEarning, Transaction,
    Referral, Withdrawal, Product, ProductImage, Order, ROISetting, ReinvestSetting, Category
)


@admin.register(MiningPackage)
class MiningPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'daily_earning', 'duration_days', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__email', 'package__name']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    
    fieldsets = (
        ('Deposit Info', {'fields': ('user', 'package', 'amount', 'payment_method', 'transaction_id')}),
        ('Status', {'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ['approve_deposits', 'reject_deposits']
    
    def approve_deposits(self, request, queryset):
        updated = 0
        for deposit in queryset:
            if deposit.status == 'pending':
                deposit.status = 'approved'
                deposit.approved_by = request.user
                from django.utils import timezone
                from decimal import Decimal
                deposit.approved_at = timezone.now()
                deposit.save()
                
                updated += 1
        
        self.message_user(request, f'{updated} deposits approved.')
    
    approve_deposits.short_description = 'Approve selected deposits'
    
    def reject_deposits(self, request, queryset):
        queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, 'Selected deposits rejected.')
    
    reject_deposits.short_description = 'Reject selected deposits'


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'mining_income', 'roi_earnings', 'referral_earnings', 'signup_bonus']
    list_filter = ['created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_earnings']


@admin.register(DailyEarning)
class DailyEarningAdmin(admin.ModelAdmin):
    list_display = ['user', 'earning_type', 'amount', 'earned_date', 'created_at']
    list_filter = ['earning_type', 'earned_date', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['user__email', 'description']
    readonly_fields = ['created_at']


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referral_user', 'level', 'commission_percentage', 'total_earned']
    list_filter = ['level', 'created_at']
    search_fields = ['referrer__email', 'referral_user__email']
    readonly_fields = ['created_at']


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'withdrawal_method', 'created_at']
    list_filter = ['status', 'withdrawal_method', 'created_at']
    search_fields = ['user__email', 'withdrawal_account']
    readonly_fields = ['created_at', 'updated_at', 'approval_date', 'tax_amount', 'net_amount']
    
    fieldsets = (
        ('Withdrawal Request', {'fields': ('user', 'amount', 'withdrawal_method', 'withdrawal_account')}),
        ('Tax Info', {'fields': ('tax_amount', 'net_amount')}),
        ('Approval', {'fields': ('status', 'approved_by', 'approval_date', 'rejection_reason')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ['approve_withdrawals', 'reject_withdrawals']
    
    def approve_withdrawals(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for withdrawal in queryset:
            if withdrawal.status == 'pending':
                withdrawal.status = 'approved'
                withdrawal.approved_by = request.user
                withdrawal.approval_date = timezone.now()
                withdrawal.save()
                
                wallet = withdrawal.user.wallet
                wallet.balance -= withdrawal.amount
                wallet.save()
                
                Transaction.objects.create(
                    user=withdrawal.user,
                    transaction_type='withdrawal',
                    amount=-withdrawal.amount,
                    description=f'Withdrawal via {withdrawal.withdrawal_method}'
                )
                updated += 1
        
        self.message_user(request, f'{updated} withdrawals approved.')
    
    approve_withdrawals.short_description = 'Approve selected withdrawals'
    
    def reject_withdrawals(self, request, queryset):
        queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, 'Selected withdrawals rejected.')
    
    reject_withdrawals.short_description = 'Reject selected withdrawals'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'category__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'order', 'alt_text', 'created_at']
    list_filter = ['is_primary', 'product', 'created_at']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'final_price', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__email', 'product__name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'total_price', 'final_price']
    
    fieldsets = (
        ('Order Info', {'fields': ('user', 'product', 'quantity')}),
        ('Pricing', {'fields': ('total_price', 'discount_percentage', 'final_price')}),
        ('Shipping', {'fields': ('shipping_address', 'phone', 'email')}),
        ('Payment', {'fields': ('payment_method', 'transaction_id')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ['confirm_orders', 'deliver_orders']
    
    def confirm_orders(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} orders confirmed.')
    
    confirm_orders.short_description = 'Confirm selected orders'
    
    def deliver_orders(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='delivered')
        self.message_user(request, f'{updated} orders delivered.')
    
    deliver_orders.short_description = 'Mark selected orders as delivered'


@admin.register(ROISetting)
class ROISettingAdmin(admin.ModelAdmin):
    list_display = ['min_percentage', 'max_percentage', 'is_active', 'updated_at']
    list_filter = ['is_active']


@admin.register(ReinvestSetting)
class ReinvestSettingAdmin(admin.ModelAdmin):
    list_display = ['percentage', 'is_active', 'updated_at']
    list_filter = ['is_active']
