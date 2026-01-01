"""
Integration tests for Reports views.

Tests URL routing, API endpoints, and authentication.
"""
import pytest
import json
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import RequestFactory
from django.urls import resolve
from django.utils import timezone

from reports import views
from reports.services.report_service import SalesKPI, ProductPerformance


# ==============================================================================
# URL ROUTING TESTS
# ==============================================================================

@pytest.mark.django_db
class TestURLRouting:
    """Tests for URL routing and resolution."""

    def test_dashboard_url_resolves(self):
        """Test dashboard URL resolves to correct view."""
        resolver = resolve('/modules/reports/')
        assert resolver.func == views.dashboard

    def test_sales_report_url_resolves(self):
        """Test sales report URL resolves."""
        resolver = resolve('/modules/reports/sales/')
        assert resolver.func == views.sales_report

    def test_products_report_url_resolves(self):
        """Test products report URL resolves."""
        resolver = resolve('/modules/reports/products/')
        assert resolver.func == views.products_report

    def test_employees_report_url_resolves(self):
        """Test employees report URL resolves."""
        resolver = resolve('/modules/reports/employees/')
        assert resolver.func == views.employees_report

    def test_api_kpi_url_resolves(self):
        """Test API KPI URL resolves."""
        resolver = resolve('/modules/reports/api/kpi/')
        assert resolver.func == views.api_kpi

    def test_api_hourly_url_resolves(self):
        """Test API hourly URL resolves."""
        resolver = resolve('/modules/reports/api/hourly/')
        assert resolver.func == views.api_hourly

    def test_api_daily_url_resolves(self):
        """Test API daily URL resolves."""
        resolver = resolve('/modules/reports/api/daily/')
        assert resolver.func == views.api_daily

    def test_api_top_products_url_resolves(self):
        """Test API top products URL resolves."""
        resolver = resolve('/modules/reports/api/top-products/')
        assert resolver.func == views.api_top_products

    def test_api_payment_methods_url_resolves(self):
        """Test API payment methods URL resolves."""
        resolver = resolve('/modules/reports/api/payment-methods/')
        assert resolver.func == views.api_payment_methods


# ==============================================================================
# AUTHENTICATION TESTS
# ==============================================================================

@pytest.mark.django_db
class TestAuthentication:
    """Tests for view authentication requirements."""

    def test_dashboard_requires_auth(self, client, store_config):
        """Test dashboard requires authentication."""
        response = client.get('/modules/reports/')

        assert response.status_code == 302
        assert '/login/' in response.url

    def test_sales_report_requires_auth(self, client, store_config):
        """Test sales report requires authentication."""
        response = client.get('/modules/reports/sales/')

        assert response.status_code == 302
        assert '/login/' in response.url

    def test_api_kpi_requires_auth(self, client, store_config):
        """Test API KPI requires authentication."""
        response = client.get('/modules/reports/api/kpi/')

        assert response.status_code == 302
        assert '/login/' in response.url


# ==============================================================================
# API ENDPOINT TESTS
# ==============================================================================

@pytest.mark.django_db
class TestAPIEndpoints:
    """Tests for API endpoints."""

    def test_api_kpi_returns_json(self, auth_client):
        """Test API KPI returns valid JSON."""
        with patch('reports.views.get_report_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_date_range.return_value = (
                timezone.now().date(),
                timezone.now().date()
            )
            mock_instance.get_sales_kpi.return_value = SalesKPI(
                total_sales=Decimal('1000.00'),
                total_transactions=50,
                average_ticket=Decimal('20.00'),
                items_sold=150
            )
            mock_service.return_value = mock_instance

            response = auth_client.get('/modules/reports/api/kpi/')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'total_sales' in data
        assert 'total_transactions' in data

    def test_api_hourly_returns_json(self, auth_client):
        """Test API hourly returns valid JSON."""
        with patch('reports.views.get_report_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_hourly_sales.return_value = []
            mock_service.return_value = mock_instance

            response = auth_client.get('/modules/reports/api/hourly/')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'date' in data
        assert 'data' in data

    def test_api_daily_returns_json(self, auth_client):
        """Test API daily returns valid JSON."""
        with patch('reports.views.get_report_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_date_range.return_value = (
                timezone.now().date(),
                timezone.now().date()
            )
            mock_instance.get_daily_sales.return_value = []
            mock_service.return_value = mock_instance

            response = auth_client.get('/modules/reports/api/daily/')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'start_date' in data
        assert 'end_date' in data
        assert 'data' in data

    def test_api_top_products_returns_json(self, auth_client):
        """Test API top products returns valid JSON."""
        with patch('reports.views.get_report_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_date_range.return_value = (
                timezone.now().date(),
                timezone.now().date()
            )
            mock_instance.get_top_products.return_value = []
            mock_service.return_value = mock_instance

            response = auth_client.get('/modules/reports/api/top-products/')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'data' in data

    def test_api_payment_methods_returns_json(self, auth_client):
        """Test API payment methods returns valid JSON."""
        with patch('reports.views.get_report_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_date_range.return_value = (
                timezone.now().date(),
                timezone.now().date()
            )
            mock_instance.get_payment_method_breakdown.return_value = []
            mock_service.return_value = mock_instance

            response = auth_client.get('/modules/reports/api/payment-methods/')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'data' in data


# ==============================================================================
# DATE PARAMETER PARSING TESTS
# ==============================================================================

@pytest.mark.django_db
class TestDateParsing:
    """Tests for date parameter parsing."""

    def test_parse_period_today(self):
        """Test parsing 'today' period."""
        rf = RequestFactory()
        request = rf.get('/', {'period': 'today'})

        start, end, period = views.parse_date_params(request)

        assert period == 'today'
        assert start == timezone.now().date()
        assert end == timezone.now().date()

    def test_parse_period_week(self):
        """Test parsing 'week' period."""
        rf = RequestFactory()
        request = rf.get('/', {'period': 'week'})

        start, end, period = views.parse_date_params(request)

        assert period == 'week'
        today = timezone.now().date()
        assert start == today - timedelta(days=today.weekday())
        assert end == today

    def test_parse_custom_dates(self):
        """Test parsing custom date range."""
        rf = RequestFactory()
        request = rf.get('/', {
            'period': 'custom',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        })

        start, end, period = views.parse_date_params(request)

        assert period == 'custom'
        assert start == date(2024, 1, 1)
        assert end == date(2024, 1, 31)

    def test_parse_invalid_dates_defaults_to_today(self):
        """Test invalid dates default to today."""
        rf = RequestFactory()
        request = rf.get('/', {
            'period': 'custom',
            'start_date': 'invalid',
            'end_date': 'invalid'
        })

        start, end, period = views.parse_date_params(request)

        assert start == timezone.now().date()
        assert end == timezone.now().date()


# ==============================================================================
# API PARAMETER TESTS
# ==============================================================================

@pytest.mark.django_db
class TestAPIParameters:
    """Tests for API parameter handling."""

    def test_api_hourly_accepts_date_param(self, auth_client):
        """Test API hourly accepts date parameter."""
        with patch('reports.views.get_report_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_hourly_sales.return_value = []
            mock_service.return_value = mock_instance

            response = auth_client.get(
                '/modules/reports/api/hourly/',
                {'date': '2024-12-25'}
            )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['date'] == '2024-12-25'

    def test_api_top_products_accepts_limit(self, auth_client):
        """Test API top products accepts limit parameter."""
        with patch('reports.views.get_report_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_date_range.return_value = (
                timezone.now().date(),
                timezone.now().date()
            )
            mock_instance.get_top_products.return_value = []
            mock_service.return_value = mock_instance

            response = auth_client.get(
                '/modules/reports/api/top-products/',
                {'limit': '5'}
            )

        assert response.status_code == 200
        mock_instance.get_top_products.assert_called_once()
        call_args = mock_instance.get_top_products.call_args
        assert call_args[0][2] == 5  # limit argument

    def test_api_top_products_accepts_order_by(self, auth_client):
        """Test API top products accepts order_by parameter."""
        with patch('reports.views.get_report_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_date_range.return_value = (
                timezone.now().date(),
                timezone.now().date()
            )
            mock_instance.get_top_products.return_value = []
            mock_service.return_value = mock_instance

            response = auth_client.get(
                '/modules/reports/api/top-products/',
                {'order_by': 'quantity'}
            )

        assert response.status_code == 200
        mock_instance.get_top_products.assert_called_once()
        call_args = mock_instance.get_top_products.call_args
        assert call_args[0][3] == 'quantity'  # order_by argument
