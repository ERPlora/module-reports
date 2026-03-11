"""
AI context for the Reports module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Reports

### Models

**Report** — a saved report definition with its data source and configuration.
- `name` (str): report title
- `description` (text)
- `report_type` (str, default "table"): presentation format — e.g. "table", "chart", "pivot"
- `data_source` (str, max 100): identifier of the data source powering this report (e.g. "sales", "inventory", "customers")
- `config` (JSON dict): report parameters — filters, columns, grouping, sorting
- `is_favorite` (bool, default False): pinned to the top/favorites section
- `last_run_at` (datetime, nullable): when the report was last executed

### Key flows

1. **Create a report**: specify name, data_source, report_type, and a config dict with filters and column definitions.
2. **Mark as favorite**: set is_favorite=True for quick access.
3. **Run a report**: update last_run_at=now after executing the query.
4. **List reports by source**: filter by data_source to show all reports for a given entity type.

### Notes
- The Reports module is a simpler single-model counterpart to the Analytics module.
- config JSON structure depends on the data_source; typical fields: `{"filters": {}, "columns": [], "group_by": null, "order_by": null}`.
- No FK relations — purely self-contained report definitions.
"""
