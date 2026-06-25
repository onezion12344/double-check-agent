# Double-Check — AI Fact Verification Pipeline

[![Version](https://img.shields.io/badge/version-2.0.0-6c5ce7)]()
[![Frameworks](https://img.shields.io/badge/frameworks-31-00c853)]()
[![Catch Rate](https://img.shields.io/badge/catch_rate-100%25-448aff)]()
[![MIT](https://img.shields.io/badge/license-MIT-86868b)]()

A 5-phase verification pipeline that catches what LLMs miss. Merges 12 academic papers + 10 journalism standards into a production-grade agent plugin. Embeds directly into Hermes Agent as a native skill + plugin.

**🔴 Live: [factcheck.onezion.top](https://factcheck.onezion.top)** (Touch ID required due to sensitive attestation)

---

## Why

LLMs hallucinate. Even at 5% error rate, AI agents produce millions of incorrect facts daily. Existing solutions fall into two camps:

| | Journalism Standards | LLM Verification |
|:-|:--------------------|:-----------------|
| **Rigor** | ✅ IFCN 5 Principles, multi-source | ❌ Single-pass classification |
| **Speed** | ❌ Human-speed | ✅ LLM-speed |
| **Our approach** | Keep the rigor | Add the speed |

---

## Benchmark Results

40 questions × 3 judges (DeepSeek V4 Flash / V4 Pro / verified sources).

| Metric | Raw V4 Flash | + Double-Check |
|:-------|:------------:|:--------------:|
| Overall | 62.5% | **97.5%** |
| Prices | 50% → | 100% |
| Specs | 80% → | 100% |
| Stats | 50% → | 100% |
| Schedules | 70% → | 100% |
| Errors caught | — | **15/15 (100%)** |
| False positives | — | 0 |

Full methodology: [`benchmark-report-v4-3judge.md`](https://github.com/onezion12344/nova-competition/blob/main/submissions/benchmark-report-v4-3judge.md)

---

## Pipeline

```
User Query
  ↓
[Phase 0] Dedup Gate — emergency skip + content check
  ↓
[Phase 0.5] Pre-answer — extract claims, time-sensitive = force search
  ↓
LLM Response
  ↓
[Phase 1] SIFT — source attribution (✅ source / ⚠️ guessed / ❌ contradiction)
  ↓
[Phase 2] CoVe + FIRE — independent cross-verification, ≥2 sources
  ↓
[Phase 3] FABLE — impact grading (🔴 Critical / 🟡 Experience / 🟢 Cosmetic)
  ↓
[Phase 4] Truth Sandwich — structured correction delivery
```

Key design rules:
- Each phase does ONE thing. Never search AND judge in the same round.
- Time-sensitive items (prices, hours, schedules) force external search.
- Emergency bypass for time-sensitive user scenarios.
- Multi-agent parallel execution when ≥15 claims need verification.

---

## Cases Studies

### Camino de Santiago Planning
- Round 1: 23 ⚠️ (guessed addresses/prices), 55 ✅ (source confirmed)
- Round 2: 4 wrong addresses + 6 wrong prices/times found
- Round 3: 1 🔴 (Correos Sunday closure → break Madrid plans), 6 🟡, 3 🟢
- **9% → 0% error rate**

### AI Foldable Phone Research
- 44 claims verified across 6 rounds
- Price errors: Nillkin ¥200→¥500, Poetic $23→$59
- Feature hallucination: BOW HB199 touchpad (doesn't exist)
- **9% → 3% → 0% error rate**

---

## Academic Foundations

### Journalism Standards (10)
| Framework | Core | Used In |
|:----------|:-----|:--------|
| **SIFT** | Stop → Investigate → Find Better → Trace | Phase 1 |
| **IFCN** | ≥2 independent sources, nonpartisan transparency | Phase 2 |
| **Truth Sandwich** | Claim → Error → Correction → Source | Phase 4 |
| **IMVAIN** | Independent / Multiple / Verifies / Authoritative / Named | Phase 1 |

### LLM Verification Research (12)
| Framework | Core Insight | Used In | Source |
|:----------|:-------------|:--------|:-------|
| **CoVe** | Draft → Plan questions → Answer independently → Revise | Phase 2 | Meta, 2023 |
| **FIRE** | Atomic claims → Iterative retrieval → Verify → Refine | Phase 2 | ACL 2025 |
| **FABLE** | Functional / Actionable / Blocking / Likelihood / Effort | Phase 3 | HCI 2025 |
| **VeriChain** | Decompose + Verifier Agent + dynamic loop | Architecture | OpenReview 2026 |
| **FLICC** | Fake experts / Logical fallacies / Cherry picking | Logic check | Nature Sci Rep 2024 |

Full framework reference: [`verification-frameworks.md`](references/verification-frameworks.md)

---

## Trade-offs: Journalism vs Academia

Researched against actual papers (June 2026).

| Dimension | 📰 Journalism | 🧠 LLM Academic | Our Hybrid |
|:----------|:------------:|:--------------:|:--:|
| **Core mechanism** | Lateral reading > close reading | Independent answering > self-Q&A | Both |
| **Automation** | ❌ Manual | ✅ Agent-native | Agent-native |
| **Adversarial adapt.** | ❌ Public frameworks targeted | ✅ Doesn't rely on single method | ✅ 2 sources minimum |
| **Motivated reasoning** | ⚠️ Aware, can't solve | ❌ Not studied | ⚠️ Ceiling — unsolved |
| **Empirical base** | Classroom/community | Benchmark datasets | Both + production data |

---

## Pitfalls

### 🐙 Don't Fabricate Numbers
"Reasonable" guesses are almost always wrong. Octopus protein: guessed 15g, actual 29.8g (USDA).

### ⚠️ Dual-Source Contamination
Tour brochure ≠ user's actual booking. Round 1 must tag *intended* source (user vs document), not just *literal* source.

### 💰 1688 Wholesale ≠ Retail
Same item: 1688 ¥15-30 / Taobao ¥50-80 / Amazon $23-60. Always check ≥3 platforms.

### 📊 Don't Mix GPU Benchmarks
Community scores vary by thermals, firmware, ambient temp. Use GSMArena review page 4 or Notebookcheck.

### ⏰ Yesterday's Source May Be Wrong
Time-sensitive items always need current verification. Correos Santiago: opened 7 days in 2024, but 2025 sources still say "closed Sundays."

---

## Quick Start

```bash
# Hermes Agent users
cp -r skill/ ~/.hermes/skills/double-check/
cp -r plugin/ ~/.hermes/plugins/double-check/
hermes skill enable double-check
hermes plugin enable double-check

# Any LLM framework
# Load skill as system prompt + plugin as function call
```

---

## NOVA 2026

Submitted to **HKUST × Tencent Research Institute NOVA Competition**, Social Impact track.

- Abstract → [`nova-competition/submissions/abstract.md`](https://github.com/onezion12344/nova-competition/blob/main/submissions/abstract.md)
- Benchmark → [`nova-competition/submissions/benchmark-report-v4-3judge.md`](https://github.com/onezion12344/nova-competition/blob/main/submissions/benchmark-report-v4-3judge.md)
- Landing page → [factcheck.onezion.top](https://factcheck.onezion.top)

---

## License

MIT © 2026 Harry (Onezion)
