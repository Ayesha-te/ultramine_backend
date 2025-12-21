from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import uuid
from .models import User
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserDetailSerializer, UserProfileUpdateSerializer
)


class AuthenticationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['register', 'login']:
            return True
        return request.user and request.user.is_authenticated


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class UserViewSet(viewsets.ViewSet):
    permission_classes = [AuthenticationPermission]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.referral_code = str(uuid.uuid4())[:8].upper()
            user.save()
            
            from core.models import Wallet, Transaction
            from django.utils import timezone
            
            wallet = Wallet.objects.create(user=user, balance=100)
            
            Transaction.objects.create(
                user=user,
                transaction_type='deposit',
                amount=100,
                status='completed',
                description='Signup bonus'
            )
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User registered successfully',
                'user': UserDetailSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user': UserDetailSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserDetailSerializer(request.user).data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})

    @action(detail=False, methods=['get'])
    def referral_code(self, request):
        user = request.user
        return Response({'referral_code': user.referral_code})

    @action(detail=False, methods=['get'])
    def my_referrals(self, request):
        user = request.user
        referrals = user.referrals.all()
        data = [{
            'id': ref.id,
            'email': ref.email,
            'name': ref.get_full_name(),
            'joined': ref.created_at,
            'status': ref.account_status,
        } for ref in referrals]
        return Response({'referrals': data})


class UserListViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action in ['partial_update', 'update']:
            return UserProfileUpdateSerializer
        return UserDetailSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def verify(self, request, pk=None):
        user = self.get_object()
        user.is_verified = True
        user.save()
        return Response({
            'message': 'User verified successfully',
            'data': UserDetailSerializer(user).data
        })
