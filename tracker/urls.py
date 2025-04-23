from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import MonthlyTotalsView, DailyTotalsView

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')

# Include JWT authentication URLs if needed (usually better to put in project urls)
urlpatterns = [
    path('', include(router.urls)),
    path('monthly-totals/', MonthlyTotalsView.as_view(), name='monthly-totals'),
     path('daily-totals/', DailyTotalsView.as_view(), name='daily-totals'),
]