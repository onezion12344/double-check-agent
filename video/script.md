# Double-Check — Intro Video Script

## Scene 1 — Title (7s)
**Visual:** Gradient title "Double-Check", tagline, team names
**Narration:** "AI agents hallucinate at scale. Even a 5% error rate produces millions of wrong facts every day. We built Double-Check — a verification pipeline that catches what LLMs miss. Our team: Harry Huang and Pan Zhengyu from the University of Hong Kong."

## Scene 2 — Problem (7s)
**Visual:** 4 error-rate cards (Prices 50%, Stats 50%, Schedules 30%, Specs 20%)
**Narration:** "When we tested DeepSeek V4 Flash on 40 factual questions across prices, specs, stats and schedules — it got only 62.5% correct. Prices were wrong half the time. Statistics were wrong half the time. This is not an edge case — it's the default."

## Scene 3 — The Gap (7s)
**Visual:** Two cards side by side — Journalism vs LLM Research
**Narration:** "Existing solutions fall into two camps. Journalism standards like SIFT and IFCN are rigorous, but purely manual. LLM verification research like CoVe and FIRE is automated, but lacks source discipline. Neither works alone."

## Scene 4 — Landscape (7s)
**Visual:** 6-card grid showing all approaches
**Narration:** "The verification landscape actually has six different approaches — training, policy, planning, selection-time, runtime guards, and bias analysis. Each checks something different. But none verifies after the tool is already called. That's the gap Double-Check fills."

## Scene 5 — Pipeline (7s)
**Visual:** 5-phase pipeline diagram
**Narration:** "Double-Check merges both worlds into a 5-phase pipeline. Pre-answer extraction, SIFT source audit, CoVe+FIRE cross-verification with ≥2 sources, FABLE impact grading, and the Truth Sandwich for structured corrections."

## Scene 6 — Architecture (7s)
**Visual:** 3 cards — Plugin, Skill, Sub-agent
**Narration:** "The system has two layers. A Hermes Plugin that auto-detects factual questions every turn and delegates to a sub-agent. And a Hermes Skill for deep audits. The plugin is an orchestrator — just 200 lines — the real work happens in sub-agents."

## Scene 7 — Demo (7s)
**Visual:** Terminal screenshot showing hook firing
**Narration:** "Here's what it looks like in practice. A user asks: how much does a Nillkin keyboard cost? The plugin hook fires instantly, classifies it as a price question, triggers searches from both English and Chinese sources. Verified answer delivered."

## Scene 8 — Results (7s)
**Visual:** Big numbers: 62.5% → 97.5%
**Narration:** "Raw DeepSeek V4 Flash scored 62.5%. With Double-Check, it reaches 97.5% — a 35 point improvement. Every error caught, zero false positives. Every category hit 100%."

## Scene 9 — Team (7s)
**Visual:** Two team cards
**Narration:** "Built at the University of Hong Kong by Harry Huang, studying Business and Engineering, and Pan Zhengyu, studying AI and Data Science. First-year undergraduates who saw a gap in how AI agents handle facts."

## Scene 10 — Closing (7s)
**Visual:** Gradient title, tagline, GitHub link
**Narration:** "AI has bounded rationality. Rather than waiting for better models, we built a system that double-checks every claim. Any model. One command. Verified output. Double-Check for NOVA 2026. MIT open source."
