from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db.models import Sum
from decimal import Decimal
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)
    referral_code = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password2', 'referral_code']

    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        from core.models import Referral
        
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            password=validated_data['password']
        )
        
        referral_code = validated_data.get('referral_code', '').strip() if 'referral_code' in validated_data else ''
        
        if referral_code:
            try:
                referrer = User.objects.get(referral_code__iexact=referral_code)
                user.referred_by = referrer
                user.save()
                
                Referral.objects.get_or_create(
                    referrer=referrer,
                    referral_user=user,
                    defaults={'level': 1, 'commission_percentage': Decimal('5.00')}
                )
            except User.DoesNotExist:
                user.save()
            except Exception as e:
                user.save()
                raise serializers.ValidationError(f"Failed to create referral: {str(e)}")
        else:
            user.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    total_invested = serializers.SerializerMethodField()
    active_packages = serializers.SerializerMethodField()
    total_referrals = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(format='iso-8601')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'referral_code', 
                  'is_verified', 'account_status', 'is_active', 'is_staff', 'is_superuser', 
                  'created_at', 'date_joined', 'total_invested', 'active_packages', 'total_referrals']
        read_only_fields = ['total_invested', 'active_packages', 'total_referrals']

    def get_total_invested(self, obj):
        from core.models import Deposit
        total = Deposit.objects.filter(user=obj, status='approved').aggregate(
            total=Sum('amount'))['total']
        return total or 0

    def get_active_packages(self, obj):
        from core.models import Deposit
        return Deposit.objects.filter(user=obj, status='approved', package__duration_days__gt=0).count()

    def get_total_referrals(self, obj):
        return obj.referrals.count()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'is_active']
