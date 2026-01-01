"""
Unit tests for Reports Service.

Tests the ReportService for generating sales analytics and KPIs.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.utils import timezone

from reports.services.report_service import (
    ReportService,
    SalesKPI,
    ProductPerformance,
    EmployeePerformance,
    HourlySales,
    get_report_service,
)


# ==============================================================================
# DATACLASS TESTS
# ==============================================================================

class TestSalesKPI:
    """Tests for SalesKPI dataclass."""

    def test_kpi_creation(self):
        """Test creating a SalesKPI instance."""
        kpi = SalesKPI(
            total_sales=Decimal('1000.00'),
            total_transactions=50,
            average_ticket=Decimal('20.00'),
            items_sold=150
        )

        assert kpi.total_sales == Decimal('1000.00')
        assert kpi.total_transactions == 50
        assert kpi.average_ticket == Decimal('20.00')
        assert kpi.items_sold == 150

    def test_kpi_net_sales_calculated(self):
        """Test net sales is automatically calculated."""
        kpi = SalesKPI(
            total_sales=Decimal('1000.00'),
            total_transactions=50,
            average_ticket=Decimal('20.00'),
            items_sold=150,
            refunds_total=Decimal('50.00'),
            refunds_count=2
        )

        assert kpi.net_sales == Decimal('950.00')

    def test_kpi_with_change_percentages(self):
        """Test KPI with comparison percentages."""
        kpi = SalesKPI(
            total_sales=Decimal('1100.00'),
            total_transactions=55,
            average_ticket=Decimal('20.00'),
            items_sold=165,
            sales_change_pct=10.0,
            transactions_change_pct=10.0
        )

        assert kpi.sales_change_pct == 10.0
        assert kpi.transactions_change_pct == 10.0


class TestProductPerformance:
    """Tests for ProductPerformance dataclass."""

    def test_product_performance_creation(self):
        """Test creating a ProductPerformance instance."""
        product = ProductPerformance(
            product_id='prod-123',
            product_name='Test Product',
            quantity_sold=100,
            total_revenue=Decimal('500.00'),
            average_price=Decimal('5.00')
        )

        assert product.product_id == 'prod-123'
        assert product.product_name == 'Test Product'
        assert product.quantity_sold == 100
        assert product.total_revenue == Decimal('500.00')


class TestEmployeePerformance:
    """Tests for EmployeePerformance dataclass."""

    def test_employee_performance_creation(self):
        """Test creating an EmployeePerformance instance."""
        employee = EmployeePerformance(
            employee_id='emp-123',
            employee_name='John Doe',
            total_sales=Decimal('2000.00'),
            transactions=100,
            average_ticket=Decimal('20.00')
        )

        assert employee.employee_id == 'emp-123'
        assert employee.employee_name == 'John Doe'
        assert employee.total_sales == Decimal('2000.00')


class TestHourlySales:
    """Tests for HourlySales dataclass."""

    def test_hourly_sales_creation(self):
        """Test creating an HourlySales instance."""
        hourly = HourlySales(
            hour=14,
            total_sales=Decimal('250.00'),
            transactions=12
        )

        assert hourly.hour == 14
        assert hourly.total_sales == Decimal('250.00')
        assert hourly.transactions == 12


# ==============================================================================
# REPORT SERVICE TESTS
# ==============================================================================

class TestReportServiceDateRanges:
    """Tests for date range calculations."""

    def test_get_date_range_today(self):
        """Test today date range."""
        service = ReportService()
        today = timezone.now().date()

        start, end = service.get_date_range('today')

        assert start == today
        assert end == today

    def test_get_date_range_yesterday(self):
        """Test yesterday date range."""
        service = ReportService()
        yesterday = timezone.now().date() - timedelta(days=1)

        start, end = service.get_date_range('yesterday')

        assert start == yesterday
        assert end == yesterday

    def test_get_date_range_week(self):
        """Test week date range starts on Monday."""
        service = ReportService()
        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())

        start, end = service.get_date_range('week')

        assert start == monday
        assert end == today

    def test_get_date_range_month(self):
        """Test month date range starts on 1st."""
        service = ReportService()
        today = timezone.now().date()
        first_of_month = today.replace(day=1)

        start, end = service.get_date_range('month')

        assert start == first_of_month
        assert end == today

    def test_get_date_range_year(self):
        """Test year date range starts on Jan 1."""
        service = ReportService()
        today = timezone.now().date()
        jan_first = today.replace(month=1, day=1)

        start, end = service.get_date_range('year')

        assert start == jan_first
        assert end == today

    def test_get_date_range_unknown_defaults_to_today(self):
        """Test unknown period defaults to today."""
        service = ReportService()
        today = timezone.now().date()

        start, end = service.get_date_range('unknown')

        assert start == today
        assert end == today


class TestReportServiceSingleton:
    """Tests for the service singleton."""

    def test_get_report_service_returns_instance(self):
        """Test get_report_service returns a ReportService."""
        service = get_report_service()

        assert isinstance(service, ReportService)

    def test_get_report_service_singleton(self):
        """Test get_report_service returns same instance."""
        service1 = get_report_service()
        service2 = get_report_service()

        assert service1 is service2


# ==============================================================================
# ADDITIONAL SERVICE TESTS
# ==============================================================================

class TestReportServiceInternal:
    """Tests for ReportService internal behavior."""

    def test_service_starts_with_no_models_cached(self):
        """Test that service starts with no models cached."""
        service = ReportService()

        assert service._sale_model is None
        assert service._sale_item_model is None

    def test_kpi_defaults_are_correct(self):
        """Test KPI dataclass defaults."""
        kpi = SalesKPI(
            total_sales=Decimal('0.00'),
            total_transactions=0,
            average_ticket=Decimal('0.00'),
            items_sold=0
        )

        assert kpi.refunds_total == Decimal('0.00')
        assert kpi.refunds_count == 0
        assert kpi.net_sales == Decimal('0.00')
        assert kpi.sales_change_pct is None
        assert kpi.transactions_change_pct is None

    def test_kpi_net_sales_calculation(self):
        """Test net sales is calculated correctly."""
        kpi = SalesKPI(
            total_sales=Decimal('1000.00'),
            total_transactions=50,
            average_ticket=Decimal('20.00'),
            items_sold=100,
            refunds_total=Decimal('100.00'),
            refunds_count=5
        )

        assert kpi.net_sales == Decimal('900.00')

    def test_product_performance_has_all_fields(self):
        """Test ProductPerformance has all expected fields."""
        product = ProductPerformance(
            product_id='prod-123',
            product_name='Test Product',
            quantity_sold=50,
            total_revenue=Decimal('500.00'),
            average_price=Decimal('10.00')
        )

        assert product.product_id == 'prod-123'
        assert product.product_name == 'Test Product'
        assert product.quantity_sold == 50
        assert product.total_revenue == Decimal('500.00')
        assert product.average_price == Decimal('10.00')

    def test_employee_performance_has_all_fields(self):
        """Test EmployeePerformance has all expected fields."""
        emp = EmployeePerformance(
            employee_id='emp-456',
            employee_name='Jane Doe',
            total_sales=Decimal('2000.00'),
            transactions=100,
            average_ticket=Decimal('20.00')
        )

        assert emp.employee_id == 'emp-456'
        assert emp.employee_name == 'Jane Doe'
        assert emp.total_sales == Decimal('2000.00')
        assert emp.transactions == 100
        assert emp.average_ticket == Decimal('20.00')

    def test_hourly_sales_has_all_fields(self):
        """Test HourlySales has all expected fields."""
        hourly = HourlySales(
            hour=15,
            total_sales=Decimal('300.00'),
            transactions=15
        )

        assert hourly.hour == 15
        assert hourly.total_sales == Decimal('300.00')
        assert hourly.transactions == 15
