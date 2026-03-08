"""
Report Service for generating sales analytics and KPIs.
"""
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any

from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone

logger = logging.getLogger('reports')


@dataclass
class SalesKPI:
    """Key Performance Indicators for sales."""
    total_sales: Decimal
    total_transactions: int
    average_ticket: Decimal
    items_sold: int

    # Comparison with previous period
    sales_change_pct: Optional[float] = None
    transactions_change_pct: Optional[float] = None

    # Additional metrics
    refunds_total: Decimal = Decimal('0.00')
    refunds_count: int = 0
    net_sales: Optional[Decimal] = None

    def __post_init__(self):
        if self.net_sales is None:
            self.net_sales = self.total_sales - self.refunds_total


@dataclass
class ProductPerformance:
    """Product performance metrics."""
    product_id: str
    product_name: str
    quantity_sold: int
    total_revenue: Decimal
    average_price: Decimal


@dataclass
class EmployeePerformance:
    """Employee performance metrics."""
    employee_id: str
    employee_name: str
    total_sales: Decimal
    transactions: int
    average_ticket: Decimal


@dataclass
class HourlySales:
    """Hourly sales breakdown."""
    hour: int
    total_sales: Decimal
    transactions: int


class ReportService:
    """
    Service for generating sales reports and analytics.

    Provides methods to calculate KPIs, product performance,
    employee metrics, and time-based analytics.
    """

    def __init__(self):
        self._sale_model = None
        self._sale_item_model = None

    @property
    def Sale(self):
        """Lazy load Sale model."""
        if self._sale_model is None:
            from sales.models import Sale
            self._sale_model = Sale
        return self._sale_model

    @property
    def SaleItem(self):
        """Lazy load SaleItem model."""
        if self._sale_item_model is None:
            from sales.models import SaleItem
            self._sale_item_model = SaleItem
        return self._sale_item_model

    def get_date_range(self, period: str) -> tuple:
        """
        Get date range for a named period.

        Args:
            period: One of 'today', 'yesterday', 'week', 'month', 'year'

        Returns:
            Tuple of (start_date, end_date)
        """
        today = timezone.now().date()

        if period == 'today':
            return today, today
        elif period == 'yesterday':
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        elif period == 'week':
            start = today - timedelta(days=today.weekday())
            return start, today
        elif period == 'month':
            start = today.replace(day=1)
            return start, today
        elif period == 'year':
            start = today.replace(month=1, day=1)
            return start, today
        else:
            # Custom range not supported here
            return today, today

    def get_sales_kpi(
        self,
        start_date: date,
        end_date: date,
        compare_previous: bool = True
    ) -> SalesKPI:
        """
        Calculate sales KPIs for a date range.

        Args:
            start_date: Start of period
            end_date: End of period
            compare_previous: Whether to include comparison with previous period

        Returns:
            SalesKPI dataclass with metrics
        """
        # Query completed sales in date range
        sales = self.Sale.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='completed'
        )

        # Aggregate metrics
        metrics = sales.aggregate(
            total_sum=Sum('total'),
            count=Count('id'),
            avg_val=Avg('total'),
            items=Sum('items_count')
        )

        total_sales = metrics['total_sum'] or Decimal('0.00')
        total_transactions = metrics['count'] or 0
        average_ticket = metrics['avg_val'] or Decimal('0.00')
        items_sold = metrics['items'] or 0

        # Get refunds
        refunds = self.Sale.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='refunded'
        ).aggregate(
            total_sum=Sum('total'),
            count=Count('id')
        )

        refunds_total = refunds['total_sum'] or Decimal('0.00')
        refunds_count = refunds['count'] or 0

        # Calculate comparison with previous period
        sales_change_pct = None
        transactions_change_pct = None

        if compare_previous:
            period_days = (end_date - start_date).days + 1
            prev_end = start_date - timedelta(days=1)
            prev_start = prev_end - timedelta(days=period_days - 1)

            prev_sales = self.Sale.objects.filter(
                created_at__date__gte=prev_start,
                created_at__date__lte=prev_end,
                status='completed'
            ).aggregate(
                total_sum=Sum('total'),
                count=Count('id')
            )

            prev_total = prev_sales['total_sum'] or Decimal('0.00')
            prev_count = prev_sales['count'] or 0

            if prev_total > 0:
                sales_change_pct = float(
                    ((total_sales - prev_total) / prev_total) * 100
                )
            if prev_count > 0:
                transactions_change_pct = float(
                    ((total_transactions - prev_count) / prev_count) * 100
                )

        return SalesKPI(
            total_sales=total_sales,
            total_transactions=total_transactions,
            average_ticket=average_ticket,
            items_sold=items_sold,
            sales_change_pct=sales_change_pct,
            transactions_change_pct=transactions_change_pct,
            refunds_total=refunds_total,
            refunds_count=refunds_count,
        )

    def get_top_products(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10,
        order_by: str = 'revenue'
    ) -> List[ProductPerformance]:
        """
        Get top performing products for a date range.

        Args:
            start_date: Start of period
            end_date: End of period
            limit: Number of products to return
            order_by: 'revenue' or 'quantity'

        Returns:
            List of ProductPerformance
        """
        items = self.SaleItem.objects.filter(
            sale__created_at__date__gte=start_date,
            sale__created_at__date__lte=end_date,
            sale__status='completed'
        ).values(
            'product_id',
            'product_name'
        ).annotate(
            qty=Sum('quantity'),
            revenue=Sum('total'),
            avg_price=Avg('unit_price')
        )

        if order_by == 'quantity':
            items = items.order_by('-qty')
        else:
            items = items.order_by('-revenue')

        items = items[:limit]

        return [
            ProductPerformance(
                product_id=str(item['product_id']),
                product_name=item['product_name'],
                quantity_sold=item['qty'] or 0,
                total_revenue=item['revenue'] or Decimal('0.00'),
                average_price=item['avg_price'] or Decimal('0.00')
            )
            for item in items
        ]

    def get_employee_performance(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[EmployeePerformance]:
        """
        Get employee sales performance for a date range.

        Args:
            start_date: Start of period
            end_date: End of period
            limit: Number of employees to return

        Returns:
            List of EmployeePerformance
        """
        employees = self.Sale.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='completed'
        ).values(
            'employee_id',
            'employee_name'
        ).annotate(
            total_sum=Sum('total'),
            count=Count('id'),
            avg_val=Avg('total')
        ).order_by('-total_sum')[:limit]

        return [
            EmployeePerformance(
                employee_id=str(emp['employee_id'] or ''),
                employee_name=emp['employee_name'] or 'Unknown',
                total_sales=emp['total_sum'] or Decimal('0.00'),
                transactions=emp['count'] or 0,
                average_ticket=emp['avg_val'] or Decimal('0.00')
            )
            for emp in employees
        ]

    def get_hourly_sales(
        self,
        target_date: date
    ) -> List[HourlySales]:
        """
        Get hourly sales breakdown for a single day.

        Args:
            target_date: Date to analyze

        Returns:
            List of HourlySales for each hour with sales
        """
        hourly = self.Sale.objects.filter(
            created_at__date=target_date,
            status='completed'
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            total_sum=Sum('total'),
            count=Count('id')
        ).order_by('hour')

        return [
            HourlySales(
                hour=h['hour'].hour,
                total_sales=h['total_sum'] or Decimal('0.00'),
                transactions=h['count'] or 0
            )
            for h in hourly
        ]

    def get_daily_sales(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get daily sales totals for a date range.

        Args:
            start_date: Start of period
            end_date: End of period

        Returns:
            List of dicts with date, total, count
        """
        daily = self.Sale.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='completed'
        ).annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            total_sum=Sum('total'),
            count=Count('id')
        ).order_by('day')

        return [
            {
                'date': d['day'],
                'total': d['total_sum'] or Decimal('0.00'),
                'transactions': d['count'] or 0
            }
            for d in daily
        ]

    def get_payment_method_breakdown(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get sales breakdown by payment method.

        Args:
            start_date: Start of period
            end_date: End of period

        Returns:
            List of dicts with method, total, count, percentage
        """
        methods = self.Sale.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='completed'
        ).values('payment_method').annotate(
            total_sum=Sum('total'),
            count=Count('id')
        ).order_by('-total_sum')

        # Calculate total for percentages
        grand_total = sum(m['total_sum'] or 0 for m in methods)

        return [
            {
                'method': m['payment_method'] or 'Unknown',
                'total': m['total_sum'] or Decimal('0.00'),
                'transactions': m['count'] or 0,
                'percentage': float(
                    (m['total_sum'] or 0) / grand_total * 100
                ) if grand_total > 0 else 0
            }
            for m in methods
        ]


# Module-level singleton
_report_service = None


def get_report_service() -> ReportService:
    """Get the report service singleton."""
    global _report_service
    if _report_service is None:
        _report_service = ReportService()
    return _report_service
