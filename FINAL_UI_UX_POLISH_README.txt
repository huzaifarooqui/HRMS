GRSJ HRMS — FINAL UI/UX POLISH
================================

Release: v1.1 Final UI/UX Polish
Base: GRSJ-HRMS v1.1 Premium Upgrade

Purpose
-------
This release is a visual/UX finishing pass. Existing business logic, database
schema, routes and HR workflows are intentionally preserved.

Included
--------
1. Consistent premium shell spacing, navigation and active states.
2. Sticky/clean admin header treatment with improved search/date controls.
3. Refined cards, panels, tables, forms, buttons and status pills.
4. Improved hover/focus states and keyboard accessibility cues.
5. Better modal, alert and empty-state presentation.
6. Mobile/tablet spacing and overflow refinements.
7. Reduced-motion support for accessibility.
8. Calendar and table micro-interactions without changing functionality.
9. Added as a separate CSS layer (10-final-ui-polish.css) so existing
   modular CSS remains intact and easy to roll back.

QA NOTE
-------
This is a UI-only polish layer. Functional regression testing should still be
performed on the local environment after deployment, especially login,
attendance/GPS, document generation, file uploads and scheduled automations.
\n\nFINAL NAVIGATION FIX — 30 Aug 2026\n- Sidebar scroll position is now preserved across full-page section navigation for both Admin and Employee navigation.\n- The menu no longer jumps back to the top after selecting a section.\n- Uses sessionStorage only; no backend/database changes.\n