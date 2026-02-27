"""
Custom Reports Module Views
"""
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.accounts.decorators import login_required, permission_required
from apps.core.htmx import htmx_view
from apps.modules_runtime.navigation import with_module_nav


@login_required
@with_module_nav('reports', 'dashboard')
@htmx_view('reports/pages/dashboard.html', 'reports/partials/dashboard_content.html')
def dashboard(request):
    """Dashboard view."""
    hub_id = request.session.get('hub_id')
    return {}


@login_required
@with_module_nav('reports', 'reports')
@htmx_view('reports/pages/reports.html', 'reports/partials/reports_content.html')
def reports(request):
    """Reports view."""
    hub_id = request.session.get('hub_id')
    return {}


@login_required
@permission_required('reports.manage_settings')
@with_module_nav('reports', 'settings')
@htmx_view('reports/pages/settings.html', 'reports/partials/settings_content.html')
def settings(request):
    """Settings view."""
    hub_id = request.session.get('hub_id')
    return {}

