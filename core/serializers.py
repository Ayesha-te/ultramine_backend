from rest_framework import serializers
from django.conf import settings
import base64
from .models import (
    MiningPackage, Deposit, Wallet, DailyEarning, Transaction,
    Referral, Withdrawal, Product, Order, ROISetting, ReinvestSetting, WithdrawalTaxSetting, Category, ProductImage
)
from users.models import User


class MiningPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiningPackage
        fields = '__all__'


class DepositSerializer(serializers.ModelSerializer):
    package_name = serializers.SerializerMethodField()
    daily_earning = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    deposit_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = Deposit
        fields = ['id', 'user', 'package', 'package_name', 'amount', 'status', 
              'payment_method', 'transaction_id', 'deposit_proof_url', 'account_name', 'daily_earning', 'remaining_days',
              'approved_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'user', 'approved_by', 'approved_at']

    def get_package_name(self, obj):
        try:
            return obj.package.name
        except Exception:
            return None

    def get_daily_earning(self, obj):
        try:
            return obj.package.daily_earning
        except Exception:
            return None

    def get_remaining_days(self, obj):
        try:
            return obj.remaining_days
        except Exception:
            return 0

    def get_deposit_proof_url(self, obj):
        if obj.deposit_proof:
            # Convert binary data to base64 for display
            return f"data:{obj.deposit_proof_content_type};base64,{base64.b64encode(obj.deposit_proof).decode()}"
        return None


class DepositDetailSerializer(serializers.ModelSerializer):
    package = MiningPackageSerializer(read_only=True)
    approved_by_email = serializers.CharField(source='approved_by.email', read_only=True, allow_null=True)
    daily_earning = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    deposit_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = Deposit
        fields = ['id', 'user', 'package', 'amount', 'status', 'payment_method', 
              'transaction_id', 'deposit_proof_url', 'account_name', 'daily_earning', 'remaining_days',
              'approved_by', 'approved_by_email', 'approved_at', 'rejection_reason',
              'created_at', 'updated_at']

    def get_daily_earning(self, obj):
        try:
            return obj.package.daily_earning
        except Exception:
            return None

    def get_remaining_days(self, obj):
        try:
            return obj.remaining_days
        except Exception:
            return 0

    def get_deposit_proof_url(self, obj):
        if obj.deposit_proof:
            # Convert binary data to base64 for display
            return f"data:{obj.deposit_proof_content_type};base64,{base64.b64encode(obj.deposit_proof).decode()}"
        return None


class WalletSerializer(serializers.ModelSerializer):
    total_earnings = serializers.DecimalField(read_only=True, max_digits=14, decimal_places=2)

    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ['user', 'balance']


class DailyEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEarning
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user']


class ReferralSerializer(serializers.ModelSerializer):
    referrer_email = serializers.CharField(source='referrer.email', read_only=True)
    referral_email = serializers.CharField(source='referral_user.email', read_only=True)
    referral_name = serializers.CharField(source='referral_user.get_full_name', read_only=True)

    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referrer_email', 'referral_user', 'referral_email', 
                  'referral_name', 'level', 'commission_percentage', 'total_earned', 'created_at']
        read_only_fields = ['total_earned', 'commission_percentage']


class WithdrawalSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Withdrawal
        fields = ['id', 'user', 'user_email', 'amount', 'withdrawal_method', 'withdrawal_account',
                  'status', 'tax_amount', 'net_amount', 'created_at', 'updated_at']
        read_only_fields = ['status', 'user', 'tax_amount', 'net_amount', 'approved_by']


class WithdrawalDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    approved_by_email = serializers.CharField(source='approved_by.email', read_only=True, allow_null=True)

    class Meta:
        model = Withdrawal
        fields = '__all__'
        read_only_fields = ['user', 'tax_amount', 'net_amount']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'is_primary', 'order']

    def get_image_url(self, obj):
        if obj.image:
            # Convert binary data to base64 for display
            return f"data:{obj.image_content_type};base64,{base64.b64encode(obj.image).decode()}"
        return None


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    product_images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            # Convert binary data to base64 for display
            return f"data:{obj.image_content_type};base64,{base64.b64encode(obj.image).decode()}"
        return None


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image_url = serializers.SerializerMethodField()
    txid_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'product_name', 'product_image_url', 'quantity',
              'total_price', 'discount_percentage', 'final_price', 'delivery_charges', 'payment_method',
              'status', 'shipping_address', 'phone', 'email', 'customer_name', 'transaction_id',
              'txid', 'txid_proof_url', 'created_at', 'updated_at']
        read_only_fields = ['status', 'user', 'total_price', 'final_price']

    def get_product_image_url(self, obj):
        if obj.product and getattr(obj.product, 'image', None):
            return f"data:{obj.product.image_content_type};base64,{base64.b64encode(obj.product.image).decode()}"
        return None

    def get_txid_proof_url(self, obj):
        if obj.txid_proof:
            return f"data:{obj.txid_proof_content_type};base64,{base64.b64encode(obj.txid_proof).decode()}"
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    txid_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'product', 'quantity',
                  'total_price', 'discount_percentage', 'final_price', 'delivery_charges', 'payment_method',
                  'status', 'shipping_address', 'phone', 'email', 'customer_name', 'transaction_id',
                  'txid', 'txid_proof_url', 'created_at', 'updated_at']
        read_only_fields = ['user', 'total_price', 'final_price']

    def get_txid_proof_url(self, obj):
        if obj.txid_proof:
            # Convert binary data to base64 for display
            return f"data:{obj.txid_proof_content_type};base64,{base64.b64encode(obj.txid_proof).decode()}"
        return None


class ROISettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ROISetting
        fields = '__all__'


class ReinvestSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReinvestSetting
        fields = '__all__'


class WithdrawalTaxSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalTaxSetting
        fields = '__all__'
