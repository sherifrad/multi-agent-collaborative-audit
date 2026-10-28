# Finance, Payments and High-Security Pack

- **Standards:** PCI-DSS (tokenise cards, never store raw card data), SOC 2 controls where relevant.
- **Exact arithmetic:** no binary floating point for currency; use decimal types or integer minor units.
- **Idempotency:** every payment or transfer mutation takes an idempotency key (UUIDv4); a retry must not double-charge.
- **Ledger integrity:** double-entry; debits equal credits at every transaction boundary; corrections are new entries, never edits.
- **Audit:** append-only, tamper-evident logs for every state change; no secrets or card data in logs.
- **Tests to include:** retry/duplicate delivery, rounding at currency boundaries, partial failure mid-transfer.
