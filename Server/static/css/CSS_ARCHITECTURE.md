# GRSJ HRMS CSS Architecture (v1.0.29)

`app.css` is now only the stable entrypoint used by existing templates. It imports ordered modules from `parts/`.

1. `01-core-home.css` — global tokens, shared components, login/home.
2. `02-allocation-responsive.css` — Allocation and early responsive rules.
3. `03-shell-digilocker.css` — fixed admin/employee shell and DigiLocker document UI.
4. `04-operations-documents.css` — operations modules, alerts, health, document register, topbar.
5. `05-admin-reports.css` — admin/report controls and CTA/layout rules.
6. `06-digital-id.css` — Digital ID front/back/mobile card design only.
7. `07-verification-responsive.css` — public verification and final responsive corrections.
8. `08-governance.css` — v1.0.28+ governance/operations additions.

## Future rule
Do not append random fixes to `app.css`. Put new selectors in the correct module or create a new numbered module and add one `@import` in `app.css`.

The order intentionally preserves the exact cascade of the previous monolithic stylesheet, so existing screens should remain visually unchanged. File separation improves maintainability; selector scoping still matters, so page-specific additions should use a page/module class rather than generic selectors whenever possible.


## Final UI/UX Polish
- `parts/10-final-ui-polish.css` is the final visual consistency layer.
- Keep business logic and route-specific behavior outside this file.
