from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'packages', views.MiningPackageViewSet, basename='mining-package')
router.register(r'deposits', views.DepositViewSet, basename='deposit')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'referrals', views.ReferralViewSet, basename='referral')
router.register(r'withdrawals', views.WithdrawalViewSet, basename='withdrawal')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'roi-settings', views.ROISettingViewSet, basename='roi-setting')
router.register(r'reinvest-settings', views.ReinvestSettingViewSet, basename='reinvest-setting')
router.register(r'withdrawal-tax-settings', views.WithdrawalTaxSettingViewSet, basename='withdrawal-tax-setting')
router.register(r'daily-earnings', views.DailyEarningViewSet, basename='daily-earning')
router.register(r'reports', views.ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    path('wallet/', views.WalletViewSet.as_view({'get': 'my_wallet'}), name='wallet'),
    path('wallet/balance/', views.WalletViewSet.as_view({'get': 'balance'}), name='wallet-balance'),
]
