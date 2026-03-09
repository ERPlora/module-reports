"""
Views for Reports Module.

Provides dashboard, sales analytics, and reporting views.
"""
import json
from datetime import date, timedelta

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from apps.accounts.decorators import login_required
from apps.core.htmx import htmx_view

from .services import get_report_service


def parse_date_params(request):
    """Parse date parameters from request."""
    period = request.GET.get('period', 'today')
    service = get_report_service()

    if period in ['today', 'yesterday', 'week', 'month', 'year']:
        start_date, end_date = service.get_date_range(period)
    else:
        # Custom date range
        start_str = request.GET.get('start_date')
        end_str = request.GET.get('end_date')
        try:
            start_date = date.fromisoformat(start_str) if start_str else timezone.now().date()
            end_date = date.fromisoformat(end_str) if end_str else timezone.now().date()
        except ValueError:
            start_date = end_date = timezone.now().date()

    return start_date, end_date, period


@require_http_methods(["GET"])
@login_required
@htmx_view('reports/pages/dashboard.html', 'reports/partials/dashboard_content.html')
def dashboard(request):
    """
    Reports dashboard - main entry point.
    Shows KPIs, charts, and quick insights.
    """
    service = get_report_service()
    start_date, end_date, period = parse_date_params(request)

    # Get KPIs
    kpi = service.get_sales_kpi(start_date, end_date)

    # Get top products
    top_products = service.get_top_products(start_date, end_date, limit=5)

    # Get hourly sales for today
    today = timezone.now().date()
    hourly = service.get_hourly_sales(today)

    # Get payment breakdown
    payment_methods = service.get_payment_method_breakdown(start_date, end_date)

    return {
        'current_view': 'dashboard',
        'current_section': 'reports',
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'kpi': kpi,
        'top_products': top_products,
        'hourly_sales': hourly,
        'payment_methods': payment_methods,
    }


@require_http_methods(["GET"])
@login_required
@htmx_view('reports/pages/sales.html', 'reports/partials/sales_content.html')
def sales_report(request):
    """
    Detailed sales report with charts and tables.
    """
    service = get_report_service()
    start_date, end_date, period = parse_date_params(request)

    # Get KPIs
    kpi = service.get_sales_kpi(start_date, end_date)

    # Get daily sales for chart
    daily_sales = service.get_daily_sales(start_date, end_date)

    # Get payment breakdown
    payment_methods = service.get_payment_method_breakdown(start_date, end_date)

    return {
        'current_view': 'sales',
        'current_section': 'reports',
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'kpi': kpi,
        'daily_sales': daily_sales,
        'payment_methods': payment_methods,
    }


@require_http_methods(["GET"])
@login_required
@htmx_view('reports/pages/products.html', 'reports/partials/products_content.html')
def products_report(request):
    """
    Product performance report.
    """
    service = get_report_service()
    start_date, end_date, period = parse_date_params(request)

    # Get order preference
    order_by = request.GET.get('order_by', 'revenue')

    # Get top products
    top_products = service.get_top_products(
        start_date, end_date,
        limit=20,
        order_by=order_by
    )

    return {
        'current_view': 'products',
        'current_section': 'reports',
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'order_by': order_by,
        'products': top_products,
    }


@require_http_methods(["GET"])
@login_required
@htmx_view('reports/pages/employees.html', 'reports/partials/employees_content.html')
def employees_report(request):
    """
    Employee performance report.
    """
    service = get_report_service()
    start_date, end_date, period = parse_date_params(request)

    # Get employee performance
    employees = service.get_employee_performance(start_date, end_date, limit=20)

    return {
        'current_view': 'employees',
        'current_section': 'reports',
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'employees': employees,
    }


# ==============================================================================
# API ENDPOINTS (for charts and HTMX updates)
# ==============================================================================

@require_http_methods(["GET"])
@login_required
def api_kpi(request):
    """Get KPI data as JSON for charts."""
    service = get_report_service()
    start_date, end_date, _ = parse_date_params(request)

    kpi = service.get_sales_kpi(start_date, end_date)

    return JsonResponse({
        'total_sales': str(kpi.total_sales),
        'total_transactions': kpi.total_transactions,
        'average_ticket': str(kpi.average_ticket),
        'items_sold': kpi.items_sold,
        'net_sales': str(kpi.net_sales),
        'refunds_total': str(kpi.refunds_total),
        'refunds_count': kpi.refunds_count,
        'sales_change_pct': kpi.sales_change_pct,
        'transactions_change_pct': kpi.transactions_change_pct,
    })


@require_http_methods(["GET"])
@login_required
def api_hourly(request):
    """Get hourly sales data for charts."""
    service = get_report_service()

    target_date = request.GET.get('date')
    if target_date:
        try:
            target_date = date.fromisoformat(target_date)
        except ValueError:
            target_date = timezone.now().date()
    else:
        target_date = timezone.now().date()

    hourly = service.get_hourly_sales(target_date)

    return JsonResponse({
        'date': target_date.isoformat(),
        'data': [
            {
                'hour': h.hour,
                'total': str(h.total_sales),
                'transactions': h.transactions
            }
            for h in hourly
        ]
    })


@require_http_methods(["GET"])
@login_required
def api_daily(request):
    """Get daily sales data for charts."""
    service = get_report_service()
    start_date, end_date, _ = parse_date_params(request)

    daily = service.get_daily_sales(start_date, end_date)

    return JsonResponse({
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'data': [
            {
                'date': d['date'].isoformat(),
                'total': str(d['total']),
                'transactions': d['transactions']
            }
            for d in daily
        ]
    })


@require_http_methods(["GET"])
@login_required
def api_top_products(request):
    """Get top products data for charts."""
    service = get_report_service()
    start_date, end_date, _ = parse_date_params(request)

    limit = int(request.GET.get('limit', 10))
    order_by = request.GET.get('order_by', 'revenue')

    products = service.get_top_products(start_date, end_date, limit, order_by)

    return JsonResponse({
        'data': [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'quantity_sold': p.quantity_sold,
                'total_revenue': str(p.total_revenue),
                'average_price': str(p.average_price)
            }
            for p in products
        ]
    })


@require_http_methods(["GET"])
@login_required
def api_payment_methods(request):
    """Get payment method breakdown for charts."""
    service = get_report_service()
    start_date, end_date, _ = parse_date_params(request)

    methods = service.get_payment_method_breakdown(start_date, end_date)

    return JsonResponse({
        'data': [
            {
                'method': m['method'],
                'total': str(m['total']),
                'transactions': m['transactions'],
                'percentage': m['percentage']
            }
            for m in methods
        ]
    })


@require_http_methods(['GET'])
@login_required
@htmx_view('reports/pages/settings.html', 'reports/partials/settings_content.html')
def settings(request):
    return {'page_title': 'Settings'}
