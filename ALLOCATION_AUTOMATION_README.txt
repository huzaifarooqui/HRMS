GRSJ HRMS Allocation Automation V4

Koofr root:
C:\Users\Lenovo\Koofr

ONLY approved source folders:
Fazil
Harshit Kumar
Heena
Lucky

Always ignored:
Huzaifa
SyncTrash
Any other folder not on the approved list

Source workbook:
Latest file starting with "Master Allocation"
Supported .xlsb / .xlsx / .xlsm / .xls

DATA PRIVACY:
Excel is opened read-only.
ONLY worksheet "Performance" is read.
The automation never reads/imports "Workable".
The workbook is not refreshed, edited, calculated, or saved by HRMS.

Automation:
Scans every 45 seconds.
Waits 8 seconds to confirm Koofr file stability.
Skips unchanged source files.
Keeps the last successful portal snapshot if a new file fails.
Keeps up to 20 successful snapshots per employee.

Mapping:
Exact normalized full name match first.
If not found, unique exact first-name match.
Ambiguous/unmatched employee folders are skipped safely and logged.

For TESTING:
Run START_ALLOCATION_SYNC.bat manually.
Do NOT install the scheduled task until production deployment.

For PRODUCTION:
Run INSTALL_ALLOCATION_AUTOMATION.bat as Administrator once.
