# Custom Reports

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `reports` |
| **Version** | `1.0.0` |
| **Icon** | `document-text-outline` |
| **Dependencies** | None |

## Models

### `Report`

Report(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, name, description, report_type, data_source, config, is_favorite, last_run_at)

| Field | Type | Details |
|-------|------|---------|
| `name` | CharField | max_length=255 |
| `description` | TextField | optional |
| `report_type` | CharField | max_length=30 |
| `data_source` | CharField | max_length=100 |
| `config` | JSONField | optional |
| `is_favorite` | BooleanField |  |
| `last_run_at` | DateTimeField | optional |

## URL Endpoints

Base path: `/m/reports/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `sales/` | `sales` | GET |
| `products/` | `products` | GET |
| `employees/` | `employees` | GET |
| `settings/` | `settings` | GET |
| `api/kpi/` | `api_kpi` | GET |
| `api/hourly/` | `api_hourly` | GET |
| `api/daily/` | `api_daily` | GET |
| `api/top-products/` | `api_top_products` | GET |
| `api/payment-methods/` | `api_payment_methods` | GET |

## Permissions

| Permission | Description |
|------------|-------------|
| `reports.view_report` | View Report |
| `reports.add_report` | Add Report |
| `reports.change_report` | Change Report |
| `reports.delete_report` | Delete Report |
| `reports.run_report` | Run Report |
| `reports.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `add_report`, `change_report`, `run_report`, `view_report`
- **employee**: `add_report`, `view_report`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Dashboard | `speedometer-outline` | `dashboard` | No |
| Reports | `document-text-outline` | `reports` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_reports`

List custom reports.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `report_type` | string | No |  |
| `is_favorite` | boolean | No |  |

### `create_report`

Create a new report definition.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Report name |
| `report_type` | string | No | table, chart, summary (default: table) |
| `data_source` | string | Yes | Data source (e.g. sales, inventory, customers) |
| `description` | string | No | Report description |
| `config` | object | No | Report configuration (filters, grouping, etc.) |

### `toggle_favorite_report`

Toggle a report's favorite status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `report_id` | string | Yes | Report ID |

## File Structure

```
README.md
__init__.py
admin.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
migrations/
  0001_initial.py
  __init__.py
models.py
module.py
services/
  __init__.py
  report_service.py
static/
  icons/
    icon.svg
templates/
  reports/
    pages/
      dashboard.html
      employees.html
      products.html
      reports.html
      sales.html
      settings.html
    partials/
      dashboard_content.html
      employees_content.html
      products_content.html
      reports_content.html
      sales_content.html
      settings_content.html
tests/
  __init__.py
urls.py
views.py
```
