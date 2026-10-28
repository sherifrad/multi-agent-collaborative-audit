# Data / ETL Pack

- **Idempotent runs:** re-running a job on the same input must give the same output and not duplicate rows.
- **Schema drift:** validate column names/types on read; fail loudly on unexpected shapes instead of coercing.
- **Reconciliation:** row counts and key totals match between source and destination; log the reconciliation.
- **Safe changes:** write to a new table/file, verify, then swap; keep the original until verified.
- **Reusable steps:** a cleaning/transform step needed twice belongs in the harness library (`scripts/harness.py`).
- **Tests to include:** empty input, one-row input, malformed rows, duplicate keys, encoding problems.
