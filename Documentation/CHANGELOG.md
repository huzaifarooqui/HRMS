# Changelog

## v1.0 RC1
- Completed the 20 requested bug fixes, business rules and UI improvements.
- Added persistent company logo/settings overview.
- Added view-only employee profile and Admin employee view page.
- Added employee document management and upcoming holiday portal.
- Added sidebar alignment, scrolling and copyright footer.
- Added safe GPS attendance handling, leave cutoff and half-day policy.


## v1.0.1 Leave Form Hotfix
- Added safe validation for the contact-during-leave field.
- Prevented database errors from values longer than 20 characters.
- Added frontend length limits for contact, custom leave type, and reason.

## v1.0 Stable Document Hotfix
- Added automatic migration for legacy employee_documents tables.
- Added missing title, document_type, file_name, original_name and uploaded_at columns at startup.
- Added legacy data backfill and orphan-file cleanup on failed uploads.
