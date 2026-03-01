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


@register_tool
class CreateReport(AssistantTool):
    name = "create_report"
    description = "Create a new report definition."
    module_id = "reports"
    required_permission = "reports.add_report"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Report name"},
            "report_type": {"type": "string", "description": "table, chart, summary (default: table)"},
            "data_source": {"type": "string", "description": "Data source (e.g. sales, inventory, customers)"},
            "description": {"type": "string", "description": "Report description"},
            "config": {"type": "object", "description": "Report configuration (filters, grouping, etc.)"},
        },
        "required": ["name", "data_source"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from reports.models import Report
        r = Report.objects.create(
            name=args['name'],
            report_type=args.get('report_type', 'table'),
            data_source=args['data_source'],
            description=args.get('description', ''),
            config=args.get('config', {}),
        )
        return {"id": str(r.id), "name": r.name, "created": True}


@register_tool
class ToggleFavoriteReport(AssistantTool):
    name = "toggle_favorite_report"
    description = "Toggle a report's favorite status."
    module_id = "reports"
    required_permission = "reports.change_report"
    parameters = {
        "type": "object",
        "properties": {"report_id": {"type": "string", "description": "Report ID"}},
        "required": ["report_id"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from reports.models import Report
        r = Report.objects.get(id=args['report_id'])
        r.is_favorite = not r.is_favorite
        r.save(update_fields=['is_favorite'])
        return {"id": str(r.id), "name": r.name, "is_favorite": r.is_favorite}
