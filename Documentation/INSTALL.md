# GAME HRMS Professional — Installation

1. Install Python 3.12–3.14 and MySQL Server.
2. In MySQL Workbench run `Database/clean_install.sql`. To restore old Phase 2 data instead, run `Database/restore_phase2_data.sql`.
3. Copy `Server/.env.example` to `Server/.env` and enter your MySQL password.
4. Double-click `SETUP_AND_START.bat`. The first run creates a local `.venv`, installs packages, safely creates/upgrades tables and launches the server.
5. Open http://127.0.0.1:5000

Default admin: `admin` / `Admin@123`. Change it directly in MySQL after first login until password-change UI is added.

Employee login: use the employee `login_id`; password may be blank if no password has been assigned.
