# ComplySight Evaluation Results

## Overview

ComplySight was evaluated against a fixed 50-case test set spanning multiple corporate policy domains, including:

- Access Control
- Data Protection
- Device Usage
- Employee Conduct
- Expense Reimbursement
- Incident Response
- Information Security
- Password Authentication
- Remote Work
- Vendor Management

Each test case contains an employee request and a human-labeled expected verdict.

The evaluation covers the five verdict categories supported by ComplySight:

- `COMPLIANT`
- `PARTIALLY_COMPLIANT`
- `NON_COMPLIANT`
- `INSUFFICIENT_EVIDENCE`
- `IRRELEVANT`

The purpose of the evaluation is to measure the behavior of the complete compliance pipeline rather than evaluating individual components in isolation.

---

## Overall Result

**Overall Accuracy: 68% (34/50)**

| Metric | Result |
|---|---:|
| Total Test Cases | 50 |
| Correct | 34 |
| Incorrect | 16 |
| Overall Accuracy | **68%** |

---

## Results by Verdict

| Expected Verdict | Correct | Total | Accuracy |
|---|---:|---:|---:|
| `COMPLIANT` | 10 | 11 | 90.9% |
| `PARTIALLY_COMPLIANT` | 5 | 10 | 50.0% |
| `NON_COMPLIANT` | 8 | 10 | 80.0% |
| `INSUFFICIENT_EVIDENCE` | 8 | 16 | 50.0% |
| `IRRELEVANT` | 3 | 3 | 100.0% |
| **Overall** | **34** | **50** | **68.0%** |

The per-category results should be interpreted as directional because the number of test cases varies between categories.

---

## Key Failure Patterns

1. **`INSUFFICIENT_EVIDENCE` vs. `PARTIALLY_COMPLIANT` Boundary**:
   - In requests where some conditions are clearly met but critical verification facts are omitted, the pipeline occasionally flags the omission as a failure or extracts additional unfulfilled conditions rather than holding the verdict at `INSUFFICIENT_EVIDENCE`.
2. **Multi-Condition Requirement Splitting**:
   - Compound rules (e.g., *"Approval AND VPN required"*) are occasionally parsed as separate obligations rather than a single atomic requirement, shifting verdicts toward `PARTIALLY_COMPLIANT`.
3. **Implicit vs. Explicit Omission**:
   - Unstated contextual facts in terse employee requests are sometimes interpreted as implicit compliance rather than missing evidence.

---

## Evaluation Pipeline

Each test case is processed through the complete ComplySight pipeline:

```text
Employee Request
       ↓
Qdrant Dense Retrieval
       ↓
Jina Reranking
       ↓
Evidence Selection
       ↓
Gemini Requirement Analysis
       ↓
Deterministic Verdict Calculation
       ↓
Final Compliance Result
```
