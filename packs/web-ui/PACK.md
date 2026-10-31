# UI pack (web, mobile, desktop screens)
*Load when the profile lists a UI domain (ui, web-app, mobile, android, ios, frontend, compose).*

Adds: the UI mock approval gate (S6, `references/ui_ux_mocking.md`) and the design/UX linter gate (S8).
The referee finds this pack through `pack.json`; a pack adds a gate by listing it under `gates` with a script that
prints JSON containing `files_scanned`.
