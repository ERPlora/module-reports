"""
Reports Module Configuration

Sales dashboard, analytics, and reporting for POS.
Used by the @module_view decorator to automatically render navigation tabs.
"""
from django.utils.translation import gettext_lazy as _

# Module Identification
MODULE_ID = "reports"
MODULE_NAME = _("Reports")
MODULE_ICON = "bar-chart-outline"
MODULE_VERSION = "1.0.0"
MODULE_CATEGORY = "reporting"

# Target Industries (business verticals this module is designed for)
MODULE_INDUSTRIES = [
    "retail",       # Retail stores
    "wholesale",    # Wholesale distributors
    "restaurant",   # Restaurants
    "bar",          # Bars & pubs
    "cafe",         # Cafes & bakeries
    "salon",        # Beauty & wellness
    "professional", # Professional services
    "ecommerce",    # E-commerce
]

# Sidebar Menu Configuration
MENU = {
    "label": _("Reports"),
    "icon": "bar-chart-outline",
    "order": 80,
    "show": True,
}

# Internal Navigation (Tabs)
NAVIGATION = [
    {
        "id": "dashboard",
        "label": _("Dashboard"),
        "icon": "grid-outline",
        "view": "",
    },
    {
        "id": "sales",
        "label": _("Sales"),
        "icon": "cart-outline",
        "view": "sales/",
    },
    {
        "id": "products",
        "label": _("Products"),
        "icon": "cube-outline",
        "view": "products/",
    },
    {
        "id": "employees",
        "label": _("Employees"),
        "icon": "people-outline",
        "view": "employees/",
    },
]

# Module Dependencies
DEPENDENCIES = ["sales"]

# Default Settings
SETTINGS = {
    "default_period": "today",
    "refresh_interval": 300,  # 5 minutes
}

# Permissions
PERMISSIONS = [
    ("view_reports", _("Can view reports")),
    ("export_reports", _("Can export reports")),
    ("view_employee_reports", _("Can view employee performance")),
]
