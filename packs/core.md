# Core Pack (all projects)

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
