# Spec

## 1. Requirement
* **Objective**: withdraw money from an account without ever going below zero.

### Call-chain map
| Target | Upstream callers | Downstream callees | Contract risks |
| :-- | :-- | :-- | :-- |
| withdraw | none yet (library) | none | amount units are whole cents; balance must stay >= 0 |

## 4. Outcome oracles
- ORACLE-1: withdraw(acct{balance:100}, 30) returns 70
- ORACLE-2: withdraw(acct{balance:50}, 80) throws and acct.balance is still 50
