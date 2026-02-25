# Custom Reports Module

Custom report builder and saved reports.

## Features

- Build custom reports from configurable data sources
- Support multiple report types (e.g., table)
- Store report configuration as JSON for flexible structure
- Mark reports as favorites for quick access
- Track when each report was last run
- Add descriptions to reports for documentation

## Installation

This module is installed automatically via the ERPlora Marketplace.

## Configuration

Access settings via: **Menu > Custom Reports > Settings**

## Usage

Access via: **Menu > Custom Reports**

### Views

| View | URL | Description |
|------|-----|-------------|
| Dashboard | `/m/reports/dashboard/` | Overview of report activity |
| Reports | `/m/reports/reports/` | List, create, and manage custom reports |
| Settings | `/m/reports/settings/` | Module configuration |

## Models

| Model | Description |
|-------|-------------|
| `Report` | Custom report with name, description, type, data source, JSON configuration, favorite flag, and last run timestamp |

## Permissions

| Permission | Description |
|------------|-------------|
| `reports.view_report` | View reports |
| `reports.add_report` | Create new reports |
| `reports.change_report` | Edit existing reports |
| `reports.delete_report` | Delete reports |
| `reports.run_report` | Execute reports |
| `reports.manage_settings` | Manage module settings |

## License

MIT

## Author

ERPlora Team - support@erplora.com
