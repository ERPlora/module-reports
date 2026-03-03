from django.utils.translation import gettext_lazy as _

MODULE_ID = 'reports'
MODULE_NAME = _('Custom Reports')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'document-text-outline'
MODULE_DESCRIPTION = _('Custom report builder and saved reports')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'analytics'

MENU = {
    'label': _('Custom Reports'),
    'icon': 'document-text-outline',
    'order': 75,
}

NAVIGATION = [
    {'label': _('Dashboard'), 'icon': 'speedometer-outline', 'id': 'dashboard'},
{'label': _('Reports'), 'icon': 'document-text-outline', 'id': 'reports'},
{'label': _('Settings'), 'icon': 'settings-outline', 'id': 'settings'},
]

DEPENDENCIES = []

PERMISSIONS = [
    'reports.view_report',
'reports.add_report',
'reports.change_report',
'reports.delete_report',
'reports.run_report',
'reports.manage_settings',
]

ROLE_PERMISSIONS = {
    "admin": ["*"],
    "manager": [
        "add_report",
        "change_report",
        "run_report",
        "view_report",
    ],
    "employee": [
        "add_report",
        "view_report",
    ],
}
