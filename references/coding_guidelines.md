# Idiomatic Coding Standards & Architectural Guidelines

This reference codifies standard programming practices, clean code conventions, module structures, and style guidelines across languages used in the project ecosystem. All fleet lanes and models (`Claude Sonnet`, `OpenCode DeepSeek`, `OpenCode GLM`, `Codex`, `Gemini`) **must adhere to these conventions** to ensure code readability, long-term maintainability, and clean architecture.

---

## 1. Kotlin & Android Jetpack Compose Standards

### A. Architectural Layering & Package Structure
Code must follow unidirectional data flow (UDF) and clean layered architecture:
```text
ui/                     # Presentation layer (Compose screens, state holders, components)
├── <feature>/
│   ├── <Feature>Screen.kt        # Pure composables, stateless or state-hoisted
│   ├── <Feature>ViewModel.kt     # State management, coroutine scoping, UI events
│   └── components/               # Feature-specific sub-composables
├── theme/                        # Design tokens, Typography, Color palettes
└── common/                       # Reusable tactile components (Buttons, Steppers, Cards)
data/                   # Data layer (Repositories, Data Sources, Local DB, Network)
├── repository/                   # Repository implementations exposing Flows / suspend fns
├── local/                        # Room DAO, Entities, Encrypted SharedPreferences/Vault
└── remote/                       # Retrofit/Ktor APIs, Firebase/Firestore services
domain/                 # Optional domain layer (UseCases, pure business rules)
└── model/                        # Pure Kotlin business models (zero Android framework deps)
```

### B. Jetpack Compose Best Practices
1. **State Hoisting**:
   - Every Composable must prefer receiving state and emitting events:
     ```kotlin
     // RECOMMENDED: Stateless & testable
     @Composable
     fun ClinicianCard(
         profile: ClinicianProfile,
         onLogoutClick: () -> Unit,
         modifier: Modifier = Modifier
     )
     ```
   - Never pass a `ViewModel` deep down the Composable tree. Only the root screen composable should touch the ViewModel.
2. **Modifier Parameter Convention**:
   - Every custom Composable **must** accept an optional `modifier: Modifier = Modifier` as the first optional parameter and apply it to the root layout element.
3. **Recomposition Hygiene**:
   - Use `remember` and derived states for expensive computations.
   - Use immutable data classes (`@Immutable` / `@Stable` or primitive types) for UI State to avoid unnecessary recompositions.
4. **Layout & Bedside Ergonomics**:
   - **Never hardcode pixel sizes**; use `.dp` and `.sp`.
   - Touch targets must be at least $48\text{dp} \times 48\text{dp}$ (`minimumInteractiveComponentSize`).
   - Support RTL natively using `Start`/`End` padding rather than `Left`/`Right`.

### C. Kotlin Idiomatic Clean Code
1. **Immutability First**:
   - Always prefer `val` over `var`.
   - Prefer read-only collections (`List`, `Map`, `Set`) over mutable counterparts. Expose `StateFlow<T>` as read-only from `MutableStateFlow<T>`.
2. **Null Safety**:
   - Avoid `!!` (force unwrap) completely. Use safe calls `?.`, elvis operator `?:`, or smart casting.
3. **Coroutines & Concurrency**:
   - Never use `GlobalScope`.
   - Always bind coroutines to lifecycle scopes: `viewModelScope` in ViewModels, `rememberCoroutineScope()` in Composables for UI effects.
   - Dispatchers: `Dispatchers.IO` for disk/network, `Dispatchers.Default` for heavy computation, and `Dispatchers.Main` for UI.
4. **Error Handling**:
   - Never swallow exceptions with empty `catch` blocks.
   - If using `runCatching`, explicitly handle both `onSuccess` and `onFailure`.

---

## 2. TypeScript / Web Modern Standards

### A. Modular Structure & Boundaries
```text
src/
├── components/          # Reusable UI components
├── pages/ or app/       # Routes and views
├── services/            # API clients, network requests
├── models/ or types/    # TypeScript interfaces and types
└── utils/               # Pure helper functions
```

### B. TypeScript Clean Code
1. **Strict Type Safety**:
   - `noImplicitAny: true`. Never use `any`; use `unknown` if the type is indeterminate and narrow it with type guards.
2. **Immutability**:
   - Use `readonly` arrays and properties where state should not mutate in-place.
3. **Async / Await**:
   - Prefer `async`/`await` over raw promise `.then()` chains.
   - Always wrap async boundaries in `try/catch` with structured error reporting.

---

## 3. Python Standards (PEP 8 & Type Hints)

1. **Type Annotations**:
   - Every function signature must have explicit type hints (e.g. `def process(path: Path) -> dict:`).
2. **Zero Global Mutations**:
   - Encapsulate logic in classes or pure functions; avoid modifying global state.
3. **Resource Management**:
   - Always use context managers (`with open(...) as f:`, `with socket(...)`) for IO handles.

---

## 4. Enforcement & Review Checklist for All Models

When reviewing or writing code, every lane must check:
- [ ] **Architecture**: Is business logic strictly separated from UI rendering?
- [ ] **Naming**: Are names clear, descriptive, and intention-revealing (no single-letter names except in loop indices)?
- [ ] **Method Length**: Functions should generally not exceed 40–50 lines; extract sub-components.
- [ ] **Idiomatic Language Usage**: Does the code look like native Kotlin/TypeScript rather than transpiled Java/C?
- [ ] **No Dead Code**: Zero commented-out code blocks or unused imports.
