# Domain Checklists

`SKILL.md` loads the section matching the work named in `.agents/PROJECT_PROFILE.md` (`Domains / packs`). For clinical and other safety-critical software, load `packs/clinical/PACK.md` (and `packs/clinical/DIAGNOSTICS.md`).

## Core (all projects)

- **Logic:** avoid O(N^2) in hot paths; guard shared state (locks, cancellation); check every caller of a
  changed function, not only the one in front of you.
- **Data:** strict types, non-null defaults, backward-compatible migrations, validated inputs, round-trip
  persistence (save, reload, compare).
- **Security:** OWASP basics (injection, XSS, SSRF, broken access control); identity and permission checks
  rely on verified claims, never on user-chosen strings.
- **Testing:** boundary values, invalid inputs, sequential user journeys; assert exact outcomes, not "no error".
- **UI (when there is one):** keyboard focus and screen-reader labels, contrast >= 4.5:1, no layout shift,
  empty/loading/error/large-font states, RTL mirroring where the audience needs it.
- **Internationalisation:** UTF-8 normalisation; look-alike characters in identifiers are a spoofing risk.

## Finance, Payments and High-Security (`fintech`)

- **Standards:** PCI-DSS (tokenise cards, never store raw card data), SOC 2 controls where relevant.
- **Exact arithmetic:** no binary floating point for currency; use decimal types or integer minor units.
- **Idempotency:** every payment or transfer mutation takes an idempotency key (UUIDv4); a retry must not double-charge.
- **Ledger integrity:** double-entry; debits equal credits at every transaction boundary; corrections are new entries, never edits.
- **Audit:** append-only, tamper-evident logs for every state change; no secrets or card data in logs.
- **Tests to include:** retry/duplicate delivery, rounding at currency boundaries, partial failure mid-transfer.

## Systems, Embedded and High-Performance (`systems`)

- **Memory:** no leaks, double-free or use-after-free; deterministic cleanup (RAII or equivalent).
- **Hot paths:** no heap allocation in audio/render loops; bound every queue.
- **Concurrency:** lock-ordering to avoid deadlock; graceful shutdown on SIGTERM/SIGINT via atomic flags.
- **Tests to include:** sanitizer builds (ASan/TSan/UBSan), stress and soak runs, fault injection on allocation/IO.

## Data / ETL (`data-etl`)

- **Idempotent runs:** re-running a job on the same input must give the same output and not duplicate rows.
- **Schema drift:** validate column names/types on read; fail loudly on unexpected shapes instead of coercing.
- **Reconciliation:** row counts and key totals match between source and destination; log the reconciliation.
- **Safe changes:** write to a new table/file, verify, then swap; keep the original until verified.
- **Reusable steps:** a cleaning/transform step needed twice belongs in the harness library (`scripts/harness.py`).
- **Tests to include:** empty input, one-row input, malformed rows, duplicate keys, encoding problems.
