# The 7-Rung Ponytail Minimalism Engine

The **Ponytail Minimalism Engine** is an architectural decision protocol designed to prevent AI bloat, premature abstraction, dependency creep, and unreadable "clever" code, while strictly upholding validation, safety, accessibility, and domain accuracy.

---

## The 7-Rung Ladder (Ascend from Simplicity to Complexity)

When implementing or auditing any solution, every Fleet Lane must evaluate options starting at **Rung 1** and only ascend to the next rung when strictly necessary:

| Rung | Name | Guiding Principle | Acceptable If | Prohibited Under This Rung |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **YAGNI (You Aren't Gonna Need It)** | Do not write code for hypothetical futures. Solve only the immediate verified requirement. | The simplest path is to eliminate unnecessary fields, flags, or configuration. | Adding speculative parameters, generic interfaces for single implementations. |
| **2** | **Existing Helper / Project Utility** | Reuse existing functions, modules, styles, and patterns in the current repo. | An existing function already achieves >=90% of the intent with minor composition. | Re-implementing formatting, date math, or string utils already present in `utils/`. |
| **3** | **Standard Library Primitive** | Rely on native language standard libraries (`dart:core`, `std`, Python `itertools`, JS `Array.prototype`). | The standard library handles it safely, performantly, and readably. | Pulling in a 3rd party package for basic lodash-style operations. |
| **4** | **Native Platform / OS API** | Utilize native platform capabilities (CSS Grid/Flexbox, Android Insets, iOS UIKit/SwiftUI primitives). | The platform provides an optimized, accessible, OS-maintained solution. | Building custom JS scroll listeners when CSS scroll-driven animations or IntersectionObserver exist. |
| **5** | **Pre-Installed Dependency** | Use an already approved and imported dependency in `package.json`, `pubspec.yaml`, or `build.gradle`. | The existing package is robust, maintained, and avoids reinventing non-trivial algorithms. | Introducing a new library when an installed one already covers the use case. |
| **6** | **Atomic Functional Primitive** | Write clean, self-contained, readable functions focused on single responsibility. | No existing tool fits; custom logic is required. | *Writing obfuscated "one-liners"* (e.g., impenetrable nested regex or dense ternary chains) to look clever. |
| **7** | **Minimum High-Performance Custom Implementation** | Specialized architecture (e.g., custom buffer pooling, SIMD, lock-free queues, bespoke state machines). | Proven profiling bottlenecks, critical latency/throughput needs, or novel domain logic. | Over-engineering boilerplate when simpler standard patterns suffice. |

---

## Inviolable Ponytail Guardrails

> [!CAUTION]
> **Minimalism NEVER means removing safety or correctness.**
> Under no circumstances may a Fleet Lane skip or dilute:
> 1. **Input validation & schema integrity** (type safety, nullability, boundary checks).
> 2. **Defensive error handling & logging** (no swallowed exceptions, no empty catch blocks).
> 3. **Security barriers & authorization** (permission checks, sanitization, CSRF/XSS defense).
> 4. **Accessibility (a11y)** (semantic HTML, contrast, tap targets, screen reader labels).
> 5. **Domain/Clinical correctness** (dosage calculations, financial precision, unit conversions).

---

## Concrete Comparison: Ponytail in Practice

### Anti-Pattern 1: The "Clever One-Liner" Trap
```typescript
// ❌ REJECTED (Misinterpreted Rung 6: Obfuscated, unmaintainable regex one-liner)
const isValidAge = (a: any) => /^(1[0-1][0-9]|120|[1-9]?[0-9])$/.test(String(a));

// ✔️ APPROVED (Rung 6: Readable Atomic Functional Primitive with safe boundaries)
export function isValidAge(value: unknown): boolean {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return false;
  }
  return Number.isInteger(value) && value >= 0 && value <= 125;
}
```

### Anti-Pattern 2: The "Premature Abstraction" Trap
```typescript
// ❌ REJECTED (Violates Rung 1 & 2: Creating a generic AbstractDataTransformerFactory for a simple map)
interface IDataTransformer<T, R> { transform(input: T): R; }
class UserDisplayNameTransformer implements IDataTransformer<User, string> { ... }

// ✔️ APPROVED (Rung 2 & 3: Standard language helper)
export function formatUserDisplayName(user: User): string {
  return `${user.firstName.trim()} ${user.lastName.trim()}`.trim() || user.username;
}
```
