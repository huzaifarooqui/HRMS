# GRSJ HRMS Professional v1.0 RC1

Ready-to-run professional HRMS for Guru Ram Singh Ji Associates.

## Existing installation upgrade
1. Stop the running server.
2. Keep a backup of the old folder and copy its `Server/.env` into this release.
3. Replace the old application folder with this folder.
4. Run `START_GAME_HRMS.bat`.
5. Do **not** run `clean_install.sql` again when retaining existing data.

See `Documentation/RC1_FIXES.md` for the completed acceptance-test list.
