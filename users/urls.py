from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'auth', views.UserViewSet, basename='auth')
router.register(r'list', views.UserListViewSet, basename='user-list')

urlpatterns = [
    path('', include(router.urls)),
]
