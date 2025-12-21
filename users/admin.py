from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_verified', 'account_status', 'created_at']
    list_filter = ['is_verified', 'account_status', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'referral_code', 'referred_by', 'is_verified', 'account_status')}),
    )
