from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import HubBaseModel

class Report(HubBaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    report_type = models.CharField(max_length=30, default='table', verbose_name=_('Report Type'))
    data_source = models.CharField(max_length=100, verbose_name=_('Data Source'))
    config = models.JSONField(default=dict, blank=True, verbose_name=_('Config'))
    is_favorite = models.BooleanField(default=False, verbose_name=_('Is Favorite'))
    last_run_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Run At'))

    class Meta(HubBaseModel.Meta):
        db_table = 'reports_report'

    def __str__(self):
        return self.name

