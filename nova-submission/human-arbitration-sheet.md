# Human Arbitration Sheet — 3 Flagged Questions

**Date:** 2026-06-23
**Purpose:** These 3 questions from the 40-question benchmark have NO single correct answer. 
The 3 LLM judges disagree or all agree on the WRONG assumption. You decide the ground truth.

---

## ⚡ C2 — "What percentage of people globally trust AI?"

| Source | Claim | Metric |
|:-------|:------|:-------|
| Stanford HAI 2026 | 47% | "Confident AI companies protect personal data" |
| Pew Research Oct 2025 | No single global % | "In no country is majority excited" |
| Edelman AI Flash Poll Nov 2025 | China 87%, US 32% | Country-specific trust |
| V4 Flash says | 54% | ❌ Confabulated |
| V4 Pro says | ~50% | ❌ Approximated from above |

**Your arbitration:**
- [ ] A: "~47% (Stanford HAI)" is the best single number
- [ ] B: "No single global number exists — report country-specific"
- [ ] C: Other: _____

---

## ⚡ A3 — "Samsung 990 Pro 1TB SSD current price?"

| Source | Price | Date | Note |
|:-------|:-----:|:----:|:-----|
| Samsung.com | $319.99 | Jun 2026 | Official store, heatsink model |
| cheapestssd.com | $129.99 | May 2026 | Third-party, non-heatsink |
| Tom's Hardware | "priced at premium" | Jun 2026 | No exact number |
| TechPowerUp | $179 (launch) | 2022 | Launch MSRP |
| V4 Flash says | $150 | ❌ | Guesses pre-shortage |
| V4 Pro says | $180 | ❌ | Guesses launch MSRP |

**Your arbitration:**
- [ ] A: "$129.99 (best retail deal)" is the right answer
- [ ] B: "$129-320 depending on retailer and model" — report as range
- [ ] C: Other: _____

---

## ⚡ D5 — "Santiago Cathedral pilgrimage hours?"

| Question | V4 Flash/Pro | Actual |
|:---------|:------------:|:-------|
| Cathedral open hours | 7am-8:30pm | Summer: 7am-8:30pm ✅ Winter: shorter |
| Pilgrim Office hours | Mixed with above | Separate: 9am-7pm (varies) |
| Mass schedule | Not mentioned | 07:30 / 09:30 / 12:00 / 19:30 |

Both models give a reasonable answer, but it's seasonal and conflates Cathedral access with Pilgrim Office hours with Mass times. The answer isn't wrong — it's incomplete and context-dependent.

**Your arbitration:**
- [ ] A: "7am-8:30pm" is accurate enough — accept
- [ ] B: "Needs seasonal + purpose-specific breakdown" — mark ⚡ incomplete
- [ ] C: Other: _____

---

## Instructions

Mark your arbitration above. I'll update the benchmark with:
- Your ground truth for these 3 questions
- Recalculate overall accuracy if answers change
- Add to final NOVA submission
