# GAME HRMS v1.0 RC1 – Fix Pack

This release implements the 20-point acceptance-test list:

- Department and holiday deletion
- Company logo upload, preview, persistent settings and overview/edit workflow
- Admin employee View action
- Aligned, scrollable Admin and Employee sidebars
- Organisation copyright footer
- Duplicate employee profile shortcut removed
- Safe GPS handling when office coordinates are missing or browser location fails
- Expanded leave types and custom leave description
- Automatic half-day rule for check-in after 10:30 AM AND check-out before 02:00 PM
- Automatic leave rejection at/after 08:00 AM
- Employee Upcoming Holidays page
- Employee Documents page with Admin upload/delete controls
- Employee dashboard check-in/check-out display and full name
- Employee profile made read-only

## Upgrade

Replace the previous `GAME_HRMS_PROFESSIONAL` application folder with this release, preserve your `Server/.env`, and start the application normally. The startup schema manager creates the new `employee_documents` table and missing seed leave types automatically. Do not rerun `clean_install.sql` when keeping your current data.
