# Spec

## 1. Requirement
* **Objective**: add and list todos in memory.

### Call-chain map
| Target | Upstream callers | Downstream callees | Contract risks |
| :-- | :-- | :-- | :-- |
| add, list | none (library) | none | list must not expose internal state; empty input rejected |

## 4. Outcome oracles
- ORACLE-1: after add('x'), list() equals [{t:'x',done:false}]
- ORACLE-2: add('  ') throws and nothing is stored
- ORACLE-3: mutating a listed item does not change the stored item
