"""Scheduled task handlers for reports module."""
import logging

logger = logging.getLogger(__name__)


def generate_daily_summary(payload):
    """Generate daily sales and performance summary."""
    from .services.report_service import ReportService
    logger.info('reports.generate_daily_summary called')
    return {'status': 'not_implemented'}


def generate_weekly_report(payload):
    """Generate weekly business report and email to stakeholders."""
    logger.info('reports.generate_weekly_report called')
    return {'status': 'not_implemented'}
