"""AI tools for the Reports module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListReports(AssistantTool):
    name = "list_reports"
    description = "List custom reports."
    module_id = "reports"
    required_permission = "reports.view_report"
    parameters = {"type": "object", "properties": {"report_type": {"type": "string"}, "is_favorite": {"type": "boolean"}}, "required": [], "additionalProperties": False}

    def execute(self, args, request):
        from reports.models import Report
        qs = Report.objects.all()
        if args.get('report_type'):
            qs = qs.filter(report_type=args['report_type'])
        if 'is_favorite' in args:
            qs = qs.filter(is_favorite=args['is_favorite'])
        return {"reports": [{"id": str(r.id), "name": r.name, "report_type": r.report_type, "data_source": r.data_source, "is_favorite": r.is_favorite, "last_run_at": r.last_run_at.isoformat() if r.last_run_at else None} for r in qs]}
