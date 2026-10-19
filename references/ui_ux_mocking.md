# UI/UX & Graphic Design Mocking Protocol

> **Governing rule for visual feature development, graphic design, and page mocking within the MACA Framework.**

---

## 1. Role Definition & Model Strengths

The **UI/UX & Graphic Design Lane** is responsible for all visual ergonomics, screen layouts, design systems, vector assets, and page mockups before backend or logic implementation begins.

### Model Routing Cascade:
1. **Default / Preferred Model**: **Claude Agent / Claude 3.5 Sonnet**
   * *Rationale*: Superior spatial awareness, semantic HTML/CSS fidelity, modern typography and color palettes, Jetpack Compose/SwiftUI ergonomics, and WCAG accessibility standards.
2. **Tier-2 Fallback (Claude Unavailable)**: **Gemini / Antigravity Orchestrator**
   * *Capabilities*: Leverages native `generative_ui` artifacts, SVG diagramming, and component mockups.
3. **Tier-3 Fallback (Sandboxed / Offline)**: **Best Available Model / Persona**
   * *Execution*: Single-file standalone HTML/CSS wireframe with native browser rendering.

---

## 2. Phase 1.5: The Visual Mocking & User Approval Gate

Whenever a feature introduces or modifies user-facing interfaces (Mobile, Web, Desktop, or CLI Dashboards), the fleet must pause before task breakdown:

```
[ Phase 1: Zero-Presumption Audit & Spec ]
                    │
                    ▼
[ Phase 1.5: UI/UX & Graphic Mock Creation ]  ◄── Claude Agent (Default)
   • Generates standalone mock: `.agents/mocks/<name>.html` (or SVG/PNG)
   • Presents visual preview & path to the User
                    │
                    ▼
     ┌─────────────────────────────┐
     │ 👤 User Review & Gate Check │
     └──────────────┬──────────────┘
                    │
            ┌───────┴───────┐
       Approved        Revisions Requested
            │               │
            │               └──► Return to Phase 1.5 (Tweak Mock)
            ▼
[ Phase 2: Task Partitioning & Work Breakdown ]
   • Attaches approved mock path into `.agents/PLAN_TASKS.md`
   • Core Logic & Data lanes build to match approved visual contract
```

> [!IMPORTANT]
> **No Logic Coding Before Visual Sign-Off**:
> Core Logic and Data lanes **must not** implement final API routes or state stores until the user explicitly reviews and approves the visual mock. This prevents wasted token expenditure and architectural rework.

---

## 3. Mock Formats & Ponytail Rules for Design

The Ponytail Minimalism Engine applies to UI mocks:

| UI Form Factor | Required Mock Format | Ponytail Principle | Prohibited in Mocks |
| :--- | :--- | :--- | :--- |
| **Web Apps / Dashboards** | Standalone Single-File HTML/CSS (in `.agents/mocks/`) | Native CSS Flexbox/Grid, zero external CDN dependencies, instant double-click preview. | Requiring `npm install` or running a webpack dev server just to see a wireframe. |
| **Mobile (Android / iOS)** | Compose / SwiftUI preview artifact or high-fidelity interactive SVG | Realistic device frame (e.g., 390x844 or 412x915), authentic system bar padding. | Mocking low-res unreadable ascii art when rich HTML/SVG can be rendered. |
| **Graphic Assets / Icons** | Clean Scalable Vector Graphics (`.svg`) | Scalable, dark-mode adaptive (`currentColor`), crisp path definitions. | Heavy uncompressed bitmaps when vectors are appropriate. |

---

## 4. Design Artifact Registration

Once a visual mock is approved by the user:
1. Save the final file to: `.agents/mocks/<feature_slug>_mock.html` (or `.svg`).
2. Record the path and sign-off in `.agents/SPEC_AND_AUDIT.md`:
   ```markdown
   ### Visual Contract & Approved Mock
   * **Mock File Path**: `.agents/mocks/bedside_entry_v2.html`
   * **Design Lead**: Claude 3.5 Sonnet (UI Lane)
   * **User Approval Status**: APPROVED (2026-10-19T07:30:00+03:00)
   ```
3. Reference the mock path in each frontend task in `.agents/PLAN_TASKS.md`.
