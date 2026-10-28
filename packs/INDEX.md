# Domain Packs

A pack is a short list of extra rules and checks for one kind of project. The project profile
(`.agents/PROJECT_PROFILE.md`, see `references/intake.md`) names which packs apply. Load only those; a pack
adds checks, it never replaces the core workflow. Several packs can apply at once.

| Pack | Load when the profile says | File |
|---|---|---|
| Core | always (every project) | `packs/core.md` |
| Web / mobile app | UI, accessibility, responsive or RTL work | `packs/core.md` (UI section) + `references/ui_ux_mocking.md` |
| Finance / payments | money, ledgers, invoices, PCI, crypto | `packs/fintech.md` |
| Systems / performance | C/C++/Rust/Go runtimes, embedded, audio/graphics, concurrency | `packs/systems.md` |
| Data / ETL | pipelines, migrations, reports, scripts over data | `packs/data-etl.md` |
| Health / safety-critical (directions only) | patient data, decision rules, medical device software | `packs/clinical/PACK.md` |

If the profile is silent, infer from the repo (file names, dependencies, keywords) and write the guess in
the profile marked `(inferred - confirm)`. Do not load the clinical pack on keywords alone when the stated
purpose says otherwise.
