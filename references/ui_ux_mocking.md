# 🎨 Phase 1.5 Visual Mocking & Phase 4.4 Design, Graphic, UI & UX Verification Protocol (`references/ui_ux_mocking.md`)

To prevent "blind text-based coding", visual regressions, broken vector graphics, and high-friction clinical UX, MACA v2 enforces a **Two-Stage Design & UX Contract**:
1. **Stage A — Phase 1.5 Pre-Coding Visual Mock & Approval Gate** (before any UI logic is written).
2. **Stage B — Phase 4.4 Four-Pillar Design, Graphic, UI & UX Verification Gate** (automated via `python3 scripts/lint_design_and_ux.py` before any task can be marked `[x]`).

---

## Stage A: Phase 1.5 Pre-Coding Visual Mock Gate

1. **Generate Standalone Visual Artifacts First**:
   - Before writing production UI code (Jetpack Compose, React/Next.js, Tailwind, SwiftUI, Flutter), the **UI/UX & Graphic Design Lane** (`claude-delegate` or active UI subagent) MUST generate a standalone, interactive `.html` or crisp `.svg` prototype inside `.agents/mocks/<feature_name>.html`.
   - The prototype must preview both **LTR (English)** and **RTL (Arabic)** layouts, light/dark semantic CSS variables (`--color-surface`, `--color-text`, `--color-alert`), and narrow mobile viewports (`360px` width).
2. **Mandatory Human Sign-Off**:
   - Present the mock path and visual summary to the User/Consultant for explicit approval before Phase 2 implementation begins.

---

## Stage B: The 4 Pillars of Automated Design, Graphic, UI & UX Testing (Phase 4.4)

Passing unit tests and semantic tree checks (`assertExists()`) is **insufficient** to approve a UI feature. Every UI/UX implementation must pass the four automated pillars enforced by `scripts/lint_design_and_ux.py` and `scripts/scenario_and_callchain_engine.py --geometric-oracle`:

### Pillar 1: Graphic, Vector & Design-Token Integrity (`DESIGN-TOKEN` / `SVG` / `RTL-ICON`)
* **Zero Hardcoded Hex Leaks in UI Components**: Production screens (`*Screen.kt`, `*.tsx`, `*.css`) must never hardcode raw hex literals (`Color(0xFF...)` or `#RRGGBB`) outside designated theme/palette files (`Theme.kt`, `Color.kt`, `tokens.css`). All colors must resolve through semantic tokens (`MaterialTheme.colorScheme.*`) so Dark Mode and High-Contrast clinical themes never break.
* **Crisp Vector & SVG Geometry**: Every `.svg` file must define an explicit `viewBox="0 0 W H"`, and every Android VectorDrawable (`<vector>`) must define `android:viewportWidth` and `android:viewportHeight` with `currentColor` or semantic tinting.
* **Arabic RTL Directional Icon Mirroring**: Every directional icon (`arrow`, `chevron`, `back`, `forward`, `send`, `next`, `prev`, `transfer`) must enable `android:autoMirrored="true"` (or CSS `[dir="rtl"] transform: scaleX(-1)`) so navigation flows naturally in Arabic.

### Pillar 2: WCAG 2.1 AA Luminance Contrast & Mock-to-Code Visual Fidelity (`WCAG-CONTRAST`)
* **Mathematical Contrast Verification**: Normal body text and clinical labels must maintain a relative luminance contrast ratio $\ge 4.5:1$ against their surface background ($\ge 3.0:1$ for large $\ge 18\text{pt}$ headers and active controls). Verify token pairs via:
  ```bash
  python3 scripts/lint_design_and_ux.py --check-contrast "#0F172A" "#FFFFFF"
  ```
* **Mock-to-Code Structural & Visual Diffing**: In Phase 4, compare the rendered screen against the approved `.agents/mocks/<feature>.html` prototype (using Compose screenshot testing / Roborazzi, Playwright `toHaveScreenshot()`, or side-by-side structural token inspection) to confirm zero visual drift.

### Pillar 3: The 5-State UI Stress Matrix (`UI-5-STATES`)
Every new screen or card component must be explicitly designed and tested across all **Five UI States**:
1. **`Empty State`**: Clean, informative zero-data view with a clear primary action (never a blank white screen).
2. **`Loading / Skeleton State`**: Non-blocking shimmer or progress indicator that preserves layout height (`CLS = 0`).
3. **`Populated (Normal) State`**: Standard clinical/operational data density.
4. **`Warning / Critical Alert State`**: High-contrast visual escalation (e.g., WHO Labour Care Guide action-line alert badge) with both color and icon/shape cues (colorblind-safe).
5. **`Extreme Text & Viewport Stress State`**: Tested at **200% OS font scaling** (`fontScale = 2.0f`) and narrow `$320\text{dp}/360\text{dp}$` width with long bilingual Arabic/English strings, asserting via `getUnclippedBoundsInRoot()` that titles keep $\ge 120\text{dp}$ width and zero text clips or overlaps adjacent action icons.

### Pillar 4: Quantitative UX & Ergonomic Flow Audit (`UX-TAP-BUDGET` & `IME-OCCLUSION`)
* **Bedside Tap & Time Budget**: High-frequency clinical actions (such as logging an hourly partogram observation or acknowledging an alert) must complete in **$\le 3$ taps** and **$< 15\text{ seconds}$**. Verify via:
  ```bash
  python3 scripts/lint_design_and_ux.py --check-ux-budget "Bedside Observation Entry" 3 12.0
  ```
* **Touch Target Ergonomics**: Every interactive control must maintain a minimum hit target of **$48\text{dp} \times 48\text{dp}$** (`44px × 44px` on Web).
* **Zero On-Screen Keyboard (`IME`) Occlusion**: Forms and bottom sheets must apply `WindowInsets.ime` / `imePadding()` so opening the numeric or text keyboard never covers the active input field or the primary `Save` button.
* **Zero Dead-End Navigation**: Every modal, sheet, or sub-screen must provide a deterministic back/cancel affordance and preserve unsaved clinical input against accidental dismissal.
