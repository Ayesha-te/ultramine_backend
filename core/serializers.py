from rest_framework import serializers
from django.conf import settings
from .models import (
    MiningPackage, Deposit, Wallet, DailyEarning, Transaction,
    Referral, Withdrawal, Product, Order, ROISetting, ReinvestSetting, WithdrawalTaxSetting, Category, ProductImage
)
from .image_utils import upload_image_to_supabase, delete_image_from_supabase
from users.models import User


def get_file_url(file_field, request=None):
    if not file_field:
        return None
    try:
        if isinstance(file_field, memoryview):
            return None
        if not hasattr(file_field, 'url'):
            return None
        url = file_field.url
        if request:
            return request.build_absolute_uri(url)
        return url
    except (AttributeError, ValueError, TypeError):
        return None
    except Exception:
        return None


class MiningPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiningPackage
        fields = '__all__'


class DepositSerializer(serializers.ModelSerializer):
    package_name = serializers.SerializerMethodField()
    daily_earning = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    deposit_proof_url = serializers.SerializerMethodField()
    deposit_proof_file = serializers.FileField(write_only=True, required=False)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Deposit
        fields = ['id', 'user', 'user_email', 'package', 'package_name', 'amount', 'status', 
              'payment_method', 'transaction_id', 'deposit_proof', 'deposit_proof_url', 'deposit_proof_file', 'account_name', 'daily_earning', 'remaining_days',
              'approved_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'user', 'user_email', 'approved_by', 'approved_at', 'created_at', 'updated_at']

    def get_package_name(self, obj):
        if not obj.package:
            return None
        try:
            return obj.package.name
        except Exception:
            return None

    def get_daily_earning(self, obj):
        if not obj.package:
            return None
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
        if not obj.deposit_proof:
            return None
        try:
            url = str(obj.deposit_proof).strip()
            if url and (url.startswith('http://') or url.startswith('https://')):
                return url
            return None
        except Exception:
            return None

    def _handle_deposit_proof_upload(self, validated_data):
        proof_file = validated_data.pop('deposit_proof_file', None)
        if proof_file:
            try:
                image_url = upload_image_to_supabase(proof_file, folder='deposit_proofs')
                if not image_url:
                    raise Exception("Upload returned empty URL")
                validated_data['deposit_proof'] = image_url
            except Exception as e:
                raise serializers.ValidationError(f"Failed to upload proof image: {str(e)}")
        else:
            validated_data['deposit_proof'] = None

    def create(self, validated_data):
        self._handle_deposit_proof_upload(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'deposit_proof_file' in validated_data:
            if instance.deposit_proof:
                delete_image_from_supabase(instance.deposit_proof)
            self._handle_deposit_proof_upload(validated_data)
        return super().update(instance, validated_data)


class DepositDetailSerializer(serializers.ModelSerializer):
    package = MiningPackageSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    approved_by_email = serializers.CharField(source='approved_by.email', read_only=True, allow_null=True)
    daily_earning = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    deposit_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = Deposit
        fields = ['id', 'user', 'user_email', 'package', 'amount', 'status', 'payment_method', 
              'transaction_id', 'deposit_proof', 'deposit_proof_url', 'account_name', 'daily_earning', 'remaining_days',
              'approved_by', 'approved_by_email', 'approved_at', 'rejection_reason',
              'created_at', 'updated_at']

    def get_daily_earning(self, obj):
        if not obj.package:
            return None
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
        if not obj.deposit_proof:
            return None
        try:
            url = str(obj.deposit_proof).strip()
            if url and (url.startswith('http://') or url.startswith('https://')):
                return url
            return None
        except Exception:
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
    image_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'image_file', 'alt_text', 'is_primary', 'order']
        read_only_fields = ['image']

    def get_image_url(self, obj):
        if obj.image:
            try:
                return str(obj.image)
            except Exception:
                return None
        return None

    def _handle_image_upload(self, validated_data):
        image_file = validated_data.pop('image_file', None)
        if image_file:
            try:
                image_url = upload_image_to_supabase(image_file, folder='product_images')
                validated_data['image'] = image_url
            except Exception as e:
                raise serializers.ValidationError(f"Image upload failed: {str(e)}")
        else:
            validated_data['image'] = None

    def create(self, validated_data):
        self._handle_image_upload(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'image_file' in validated_data:
            if instance.image:
                delete_image_from_supabase(instance.image)
            self._handle_image_upload(validated_data)
        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    product_images = ProductImageSerializer(many=True, read_only=True)
    image_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'delivery_charges', 'category', 'category_name', 'image', 'image_url', 'image_file', 'stock', 'is_active', 'product_images', 'created_at', 'updated_at']
        read_only_fields = ['image']

    def get_image_url(self, obj):
        if obj.image:
            try:
                return str(obj.image)
            except Exception:
                return None
        return None

    def _handle_image_upload(self, validated_data):
        image_file = validated_data.pop('image_file', None)
        if image_file:
            try:
                image_url = upload_image_to_supabase(image_file, folder='products')
                validated_data['image'] = image_url
            except Exception as e:
                raise serializers.ValidationError(f"Image upload failed: {str(e)}")
        else:
            validated_data['image'] = None

    def create(self, validated_data):
        self._handle_image_upload(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'image_file' in validated_data:
            if instance.image:
                delete_image_from_supabase(instance.image)
            self._handle_image_upload(validated_data)
        return super().update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image_url = serializers.SerializerMethodField()
    txid_proof_url = serializers.SerializerMethodField()
    txid_proof_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'product_name', 'product_image_url', 'quantity',
              'total_price', 'discount_percentage', 'final_price', 'delivery_charges', 'payment_method',
              'status', 'shipping_address', 'phone', 'email', 'customer_name', 'transaction_id',
              'txid', 'txid_proof', 'txid_proof_file', 'txid_proof_url', 'created_at', 'updated_at']
        read_only_fields = ['status', 'user', 'total_price', 'final_price', 'txid_proof']

    def get_product_image_url(self, obj):
        if not obj.product or not getattr(obj.product, 'image', None):
            return None
        image = getattr(obj.product, 'image', None)
        if image:
            return str(image) if isinstance(image, str) and image.startswith('http') else None
        return None

    def get_txid_proof_url(self, obj):
        if obj.txid_proof:
            return str(obj.txid_proof) if isinstance(obj.txid_proof, str) and obj.txid_proof.startswith('http') else None
        return None

    def _handle_txid_proof_upload(self, validated_data):
        proof_file = validated_data.pop('txid_proof_file', None)
        if proof_file:
            try:
                image_url = upload_image_to_supabase(proof_file, folder='order_proofs')
                validated_data['txid_proof'] = image_url
            except Exception as e:
                raise serializers.ValidationError(f"Image upload failed: {str(e)}")
        else:
            validated_data['txid_proof'] = None

    def create(self, validated_data):
        self._handle_txid_proof_upload(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'txid_proof_file' in validated_data:
            if instance.txid_proof:
                delete_image_from_supabase(instance.txid_proof)
            self._handle_txid_proof_upload(validated_data)
        return super().update(instance, validated_data)


class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    txid_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'product', 'quantity',
                  'total_price', 'discount_percentage', 'final_price', 'delivery_charges', 'payment_method',
                  'status', 'shipping_address', 'phone', 'email', 'customer_name', 'transaction_id',
                  'txid', 'txid_proof', 'txid_proof_url', 'created_at', 'updated_at']
        read_only_fields = ['user', 'total_price', 'final_price']

    def get_txid_proof_url(self, obj):
        if obj.txid_proof:
            return str(obj.txid_proof) if isinstance(obj.txid_proof, str) and obj.txid_proof.startswith('http') else None
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
