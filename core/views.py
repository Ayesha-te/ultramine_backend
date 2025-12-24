from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from decimal import Decimal
import uuid

from .models import (
    MiningPackage, Deposit, Wallet, DailyEarning, Transaction,
    Referral, Withdrawal, Product, Order, ROISetting, ReinvestSetting, WithdrawalTaxSetting, Category, ProductImage
)
from .serializers import (
    MiningPackageSerializer, DepositSerializer, DepositDetailSerializer,
    WalletSerializer, DailyEarningSerializer, TransactionSerializer,
    ReferralSerializer, WithdrawalSerializer, WithdrawalDetailSerializer,
    ProductSerializer, ProductImageSerializer, OrderSerializer, OrderDetailSerializer,
    ROISettingSerializer, ReinvestSettingSerializer, WithdrawalTaxSettingSerializer, CategorySerializer
)
from .reports import (
    generate_users_report_excel, generate_users_report_pdf,
    generate_earnings_report_excel, generate_earnings_report_pdf,
    generate_orders_report_excel, generate_orders_report_pdf
)
from .services import EarningService
from users.models import User


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsAuthenticatedOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class MiningPackageViewSet(viewsets.ModelViewSet):
    queryset = MiningPackage.objects.all()
    serializer_class = MiningPackageSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['list', 'active_packages', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdmin()]

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return MiningPackage.objects.all().order_by('price')
        return MiningPackage.objects.filter(is_active=True).order_by('price')

    @action(detail=False, methods=['get'])
    def active_packages(self, request):
        packages = MiningPackage.objects.filter(is_active=True).order_by('price')
        serializer = self.get_serializer(packages, many=True)
        return Response(serializer.data)


class DepositViewSet(viewsets.ModelViewSet):
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticatedOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Deposit.objects.all()
        return Deposit.objects.filter(user=self.request.user)

def create(self, request, *args, **kwargs):
    package_id = request.data.get('package')
    amount = request.data.get('amount')
    payment_method = request.data.get('payment_method')

    try:
        package = MiningPackage.objects.get(id=package_id, is_active=True)
    except MiningPackage.DoesNotExist:
        return Response(
            {'error': 'Package not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if Decimal(amount) < package.price:
        return Response(
            {'error': f'Minimum investment is ₨{package.price}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    proof_file = request.FILES.get('deposit_proof')

    if not proof_file:
        return Response(
            {'error': 'Deposit proof image is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    deposit = Deposit.objects.create(
        user=request.user,
        package=package,
        amount=amount,
        payment_method=payment_method,
        transaction_id=request.data.get('transaction_id', ''),
        deposit_proof=proof_file,  # ✅ FILE OBJECT ONLY
        account_name=request.data.get('account_name', ''),
        status='pending'
    )

    Transaction.objects.create(
        user=request.user,
        transaction_type='deposit',
        amount=amount,
        description=f'Deposit for {package.name}'
    )

    return Response(
        DepositSerializer(deposit, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


    
    def _process_referral_commissions(self, deposit):
        levels_config = [
            {'level': 1, 'percentage': Decimal('5.00'), 'requires_deposit': False},
            {'level': 2, 'percentage': Decimal('2.00'), 'requires_deposit': True},
            {'level': 3, 'percentage': Decimal('1.00'), 'requires_deposit': True},
        ]
        
        current_user = deposit.user.referred_by
        current_level = 1
        
        while current_user and current_level <= 3:
            if current_user.account_status != 'active':
                break
            
            level_config = levels_config[current_level - 1]
            
            if current_level > 1:
                has_deposit = Deposit.objects.filter(
                    user=current_user,
                    status='approved'
                ).exists()
                if not has_deposit:
                    current_user = current_user.referred_by
                    current_level += 1
                    continue
            
            commission_amount = Decimal(deposit.amount) * (level_config['percentage'] / Decimal('100'))
            
            referral, created = Referral.objects.get_or_create(
                referrer=current_user,
                referral_user=deposit.user,
                defaults={'level': current_level, 'commission_percentage': level_config['percentage']}
            )
            referral.total_earned += commission_amount
            referral.save()
            
            try:
                referrer_wallet = current_user.wallet
            except Wallet.DoesNotExist:
                referrer_wallet = Wallet.objects.create(user=current_user, balance=0)
            
            referrer_wallet.referral_earnings += commission_amount
            referrer_wallet.save()
            
            Transaction.objects.create(
                user=current_user,
                transaction_type='referral',
                amount=commission_amount,
                description=f'Level {current_level} referral commission from {deposit.user.email} deposit'
            )
            
            current_user = current_user.referred_by
            current_level += 1

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        deposit = self.get_object()
        if deposit.status != 'pending':
            return Response({'error': 'Deposit already processed'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        user = deposit.user
        wallet = user.wallet
        
        wallet_balance_before = wallet.balance
        wallet_signup_bonus_before = wallet.signup_bonus

        deposit.status = 'approved'
        deposit.approved_by = request.user
        deposit.approved_at = timezone.now()
        deposit.save()

        wallet.refresh_from_db()
        
        if wallet.balance > wallet_balance_before:
            wallet.balance = wallet_balance_before
            wallet.save()
        
        if wallet.signup_bonus > wallet_signup_bonus_before:
            wallet.signup_bonus = wallet_signup_bonus_before
            wallet.save()

        if deposit.user.referred_by:
            self._process_referral_commissions(deposit)

        try:
            EarningService.calculate_daily_earnings()
            EarningService.process_referral_earnings()
        except Exception as e:
            pass

        return Response({'message': 'Deposit approved', 'data': DepositSerializer(deposit, context={'request': request}).data})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        deposit = self.get_object()
        if deposit.status != 'pending':
            return Response({'error': 'Deposit already processed'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        deposit.status = 'rejected'
        deposit.rejection_reason = request.data.get('reason', '')
        deposit.save()

        return Response({'message': 'Deposit rejected', 'data': DepositSerializer(deposit, context={'request': request}).data})

    @action(detail=False, methods=['get'])
    def pending(self, request):
        deposits = Deposit.objects.filter(status='pending').order_by('-created_at')
        if not request.user.is_staff:
            deposits = deposits.filter(user=request.user)
        
        page = self.paginate_queryset(deposits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(deposits, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_deposits(self, request):
        deposits = Deposit.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(deposits)
        if page is not None:
            serializer = DepositDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = DepositDetailSerializer(deposits, many=True, context={'request': request})
        return Response(serializer.data)


class WalletViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrAdmin]

    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        wallet = get_object_or_404(Wallet, user=request.user)
        return Response(WalletSerializer(wallet, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def balance(self, request):
        wallet = get_object_or_404(Wallet, user=request.user)
        return Response({
            'balance': wallet.balance,
            'mining_income': wallet.mining_income,
            'roi_earnings': wallet.roi_earnings,
            'referral_earnings': wallet.referral_earnings,
            'signup_bonus': wallet.signup_bonus,
            'total_earnings': wallet.total_earnings,
            'last_earning_date': wallet.last_earning_date,
        })


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticatedOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.request.user)


class ReferralViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    permission_classes = [IsAuthenticatedOrAdmin]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return Referral.objects.all()
        return Referral.objects.filter(referrer=self.request.user)

    @action(detail=False, methods=['get'])
    def my_team(self, request):
        user = request.user
        direct_referrals = user.referrals_given.all()
        
        team_stats = {
            'total_team': user.referrals_given.count(),
            'total_team_earnings': Referral.objects.filter(referrer=user).aggregate(
                total=Sum('total_earned'))['total'] or 0,
            'referrals': ReferralSerializer(direct_referrals, many=True, context={'request': request}).data
        }
        
        return Response(team_stats)

    @action(detail=False, methods=['get'])
    def team_statistics(self, request):
        user = request.user
        
        level1_referrals = Referral.objects.filter(referrer=user, level=1)
        level2_referrals = Referral.objects.filter(referrer=user, level=2)
        level3_referrals = Referral.objects.filter(referrer=user, level=3)
        
        level1_count = level1_referrals.count()
        level2_count = level2_referrals.count()
        level3_count = level3_referrals.count()
        
        level1_earnings = level1_referrals.aggregate(total=Sum('total_earned'))['total'] or Decimal('0.00')
        level2_earnings = level2_referrals.aggregate(total=Sum('total_earned'))['total'] or Decimal('0.00')
        level3_earnings = level3_referrals.aggregate(total=Sum('total_earned'))['total'] or Decimal('0.00')
        total_earnings = level1_earnings + level2_earnings + level3_earnings
        
        return Response({
            'direct_referrals': level1_count,
            'total_team': level1_count + level2_count + level3_count,
            'team_earnings': float(total_earnings),
            'level1_count': level1_count,
            'level1_earnings': float(level1_earnings),
            'level2_count': level2_count,
            'level2_earnings': float(level2_earnings),
            'level3_count': level3_count,
            'level3_earnings': float(level3_earnings),
        })


class WithdrawalViewSet(viewsets.ModelViewSet):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticatedOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Withdrawal.objects.all()
        return Withdrawal.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        amount = Decimal(request.data.get('amount'))
        user = request.user
        
        if amount < 1000:
            return Response({'error': 'Minimum withdrawal is ₨1000'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        wallet = user.wallet
        if wallet.balance < amount:
            return Response({'error': 'Insufficient balance'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        first_withdrawal = user.withdrawals.filter(status__in=['completed', 'approved']).count() == 0
        if not first_withdrawal:
            referral_count = user.referrals_given.count()
            if referral_count < 2:
                return Response({
                    'error': f'You need at least 2 referrals to withdraw. Current: {referral_count}'
                }, status=status.HTTP_400_BAD_REQUEST)

        withdrawal = Withdrawal.objects.create(
            user=user,
            amount=amount,
            withdrawal_method=request.data.get('withdrawal_method'),
            withdrawal_account=request.data.get('withdrawal_account'),
            status='pending'
        )

        return Response(WithdrawalDetailSerializer(withdrawal, context={'request': request}).data, 
                       status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != 'pending':
            return Response({'error': 'Withdrawal already processed'}, 
                          status=status.HTTP_400_BAD_REQUEST)

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

        return Response({'message': 'Withdrawal approved', 
                        'data': WithdrawalDetailSerializer(withdrawal, context={'request': request}).data})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != 'pending':
            return Response({'error': 'Withdrawal already processed'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        withdrawal.status = 'rejected'
        withdrawal.rejection_reason = request.data.get('reason', '')
        withdrawal.save()

        wallet = withdrawal.user.wallet
        wallet.balance += withdrawal.amount
        wallet.save()

        return Response({'message': 'Withdrawal rejected', 
                        'data': WithdrawalDetailSerializer(withdrawal, context={'request': request}).data})

    @action(detail=False, methods=['get'])
    def pending(self, request):
        withdrawals = Withdrawal.objects.filter(status='pending').order_by('-created_at')
        if not request.user.is_staff:
            withdrawals = withdrawals.filter(user=request.user)
        
        page = self.paginate_queryset(withdrawals)
        if page is not None:
            serializer = WithdrawalDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = WithdrawalDetailSerializer(withdrawals, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_withdrawals(self, request):
        withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(withdrawals)
        if page is not None:
            serializer = WithdrawalDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = WithdrawalDetailSerializer(withdrawals, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return Category.objects.all()
        return Category.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdmin()]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category__name', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Product.objects.all()
        return Product.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'categories', 'by_category']:
            return [permissions.AllowAny()]
        return [IsAdmin()]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def upload_images(self, request, pk=None):
        product = self.get_object()
        files = request.FILES.getlist('images')
        
        if not files:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_images = []
        for idx, file in enumerate(files):
            product_image = ProductImage.objects.create(
                product=product,
                image=file,
                alt_text=request.data.get(f'alt_text_{idx}', ''),
                order=idx,
                is_primary=(idx == 0)
            )
            uploaded_images.append(ProductImageSerializer(product_image, context={'request': request}).data)
        
        return Response({
            'message': f'{len(uploaded_images)} images uploaded successfully',
            'images': uploaded_images
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], permission_classes=[IsAdmin])
    def delete_image(self, request, pk=None):
        product = self.get_object()
        image_id = request.query_params.get('image_id')
        
        if not image_id:
            return Response({'error': 'image_id parameter required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            image = ProductImage.objects.get(id=image_id, product=product)
            image.delete()
            return Response({'message': 'Image deleted successfully'})
        except ProductImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'category_id parameter required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(category_id=category_id, is_active=True)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
            return Response({'error': 'Insufficient stock'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        discount = Decimal('10.00') if request.user.is_authenticated else Decimal('0.00')

        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            payment_method=request.data.get('payment_method'),
            discount_percentage=discount,
            shipping_address=request.data.get('shipping_address'),
            phone=request.data.get('phone'),
            email=request.data.get('email', request.user.email if request.user.is_authenticated else ''),
            customer_name=request.data.get('customer_name', ''),
            status='pending'
        )

        product.stock -= quantity
        product.save()

        Transaction.objects.create(
            user=request.user,
            transaction_type='order',
            amount=-order.final_price,
            description=f'Order for {product.name}'
        )

        return Response(OrderDetailSerializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def confirm(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': 'Order status cannot be changed'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        order.status = 'confirmed'
        order.save()
        
        return Response({'message': 'Order confirmed', 'data': OrderDetailSerializer(order, context={'request': request}).data})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def deliver(self, request, pk=None):
        order = self.get_object()
        if order.status != 'confirmed':
            return Response({'error': 'Order must be confirmed first'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        order.status = 'delivered'
        order.save()
        
        return Response({'message': 'Order delivered', 'data': OrderDetailSerializer(order, context={'request': request}).data})

    @action(detail=False, methods=['get'])
    def pending(self, request):
        orders = Order.objects.filter(status='pending').order_by('-created_at')
        if not request.user.is_staff:
            orders = orders.filter(user=request.user)
        
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderDetailSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderDetailSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data)


class ROISettingViewSet(viewsets.ModelViewSet):
    queryset = ROISetting.objects.all()
    serializer_class = ROISettingSerializer
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def current(self, request):
        roi = ROISetting.objects.filter(is_active=True).first()
        if roi:
            return Response(ROISettingSerializer(roi, context={'request': request}).data)
        return Response({'error': 'ROI setting not configured'}, 
                       status=status.HTTP_404_NOT_FOUND)


class ReinvestSettingViewSet(viewsets.ModelViewSet):
    queryset = ReinvestSetting.objects.all()
    serializer_class = ReinvestSettingSerializer
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def current(self, request):
        setting = ReinvestSetting.objects.filter(is_active=True).first()
        if setting:
            return Response(ReinvestSettingSerializer(setting, context={'request': request}).data)
        return Response({'error': 'Reinvest setting not configured'}, 
                       status=status.HTTP_404_NOT_FOUND)


class WithdrawalTaxSettingViewSet(viewsets.ModelViewSet):
    queryset = WithdrawalTaxSetting.objects.all()
    serializer_class = WithdrawalTaxSettingSerializer
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def current(self, request):
        setting = WithdrawalTaxSetting.objects.filter(is_active=True).first()
        if setting:
            return Response(WithdrawalTaxSettingSerializer(setting, context={'request': request}).data)
        return Response({'error': 'Withdrawal tax setting not configured'}, 
                       status=status.HTTP_404_NOT_FOUND)


class DailyEarningViewSet(viewsets.ModelViewSet):
    serializer_class = DailyEarningSerializer
    permission_classes = [IsAuthenticatedOrAdmin]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return DailyEarning.objects.all()
        return DailyEarning.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_earnings(self, request):
        earnings = DailyEarning.objects.filter(user=request.user).order_by('-earned_date')
        
        page = self.paginate_queryset(earnings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(earnings, many=True)
        return Response(serializer.data)


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        return Response({'detail': 'Use /users_report/, /earnings_report/, or /orders_report/'})

    @action(detail=False, methods=['get'])
    def users_report(self, request):
        file_format = request.query_params.get('format', 'excel')
        
        try:
            if file_format.lower() == 'pdf':
                buffer = generate_users_report_pdf()
                filename = 'users_report.pdf'
                content_type = 'application/pdf'
            else:
                buffer = generate_users_report_excel()
                filename = 'users_report.xlsx'
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            return FileResponse(
                buffer,
                as_attachment=True,
                filename=filename,
                content_type=content_type
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def earnings_report(self, request):
        file_format = request.query_params.get('format', 'excel')
        
        try:
            if file_format.lower() == 'pdf':
                buffer = generate_earnings_report_pdf()
                filename = 'earnings_report.pdf'
                content_type = 'application/pdf'
            else:
                buffer = generate_earnings_report_excel()
                filename = 'earnings_report.xlsx'
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            return FileResponse(
                buffer,
                as_attachment=True,
                filename=filename,
                content_type=content_type
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def orders_report(self, request):
        file_format = request.query_params.get('format', 'excel')
        
        try:
            if file_format.lower() == 'pdf':
                buffer = generate_orders_report_pdf()
                filename = 'orders_report.pdf'
                content_type = 'application/pdf'
            else:
                buffer = generate_orders_report_excel()
                filename = 'orders_report.xlsx'
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            return FileResponse(
                buffer,
                as_attachment=True,
                filename=filename,
                content_type=content_type
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
