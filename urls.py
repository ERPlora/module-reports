from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Report pages
    path('sales/', views.sales_report, name='sales'),
    path('products/', views.products_report, name='products'),
    path('employees/', views.employees_report, name='employees'),

    # API endpoints for charts
    path('api/kpi/', views.api_kpi, name='api_kpi'),
    path('api/hourly/', views.api_hourly, name='api_hourly'),
    path('api/daily/', views.api_daily, name='api_daily'),
    path('api/top-products/', views.api_top_products, name='api_top_products'),
    path('api/payment-methods/', views.api_payment_methods, name='api_payment_methods'),
]
