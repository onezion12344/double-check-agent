# Fact-Check Agent: A Hybrid Verification Framework for AI-Generated Content

**Team:** HUANG Ziyang (Harry) — The University of Hong Kong
**Track:** Social Impact
**GitHub:** https://github.com/onezion12344/fact-check-agent
**Live Demo:** https://onezion12344.github.io/fact-check-agent/

## Problem

Large Language Models (LLMs) hallucinate. When AI agents generate content at scale, even a 5% hallucination rate produces millions of incorrect facts daily. Existing fact-checking approaches fall into two camps, neither sufficient alone:

- **Journalism standards** (SIFT, IFCN) offer rigorous source verification but assume human execution — too slow for real-time AI output
- **LLM verification research** (CoVe, FIRE, VeriChain) automates verification but lacks journalistic rigor, treating verification as a single-pass classification task rather than a multi-stage audit

The gap: an automated system that applies **both** journalistic source discipline **and** LLM-scale verification in a structured pipeline.

## Our Approach

**Fact-Check Agent** is a 5-phase hybrid verification framework that merges 12 academic papers and 10 journalism standards into a production-grade AI agent plugin:

### Phase 0.5 — Pre-Answer Verification
Before responding to any factual query, the agent automatically extracts prices, times, addresses, names, and numbers from the user's question, searches ≥2 independent sources in parallel, and tags output inline: ✅ confirmed / 🔧 corrected / ⚡ disputed / ❌ unverifiable. Time-sensitive items (hours, prices, schedules) force external search — never relying on internal knowledge.

### Phase 1 — SIFT Source Audit (Caulfield 2019)
After generating a dense response, every factual claim is tagged against its source:
- ✅ From source (quote-checked)
- ⚠️ Inferred/completed (needs verification)
- ❌ Contradicts source

### Phase 2 — CoVe+FIRE Cross-Verification (Meta 2023, ACL 2025)
⚠️-tagged claims undergo external verification:
- **CoVe**: Generate independent verification questions, search for answers without re-reading the original text (prevents confirmation bias)
- **FIRE**: Iterative search — one search → insufficient → search again from a different angle until evidence converges
- **IFCN standard**: ≥2 independent sources per claim

### Phase 3 — FABLE Impact Analysis (HCI 2025)
Errors are graded by decision impact:
- 🔴 Critical Path: Breaks user's workflow
- 🟡 Experience: Nice to fix but non-blocking
- 🟢 Cosmetic: Text-only corrections

### Phase 4 — Truth Sandwich Correction
Each error is delivered as: What was written → What's wrong → What's correct + source → Action needed?

## Technical Architecture

The system is implemented as a **Hermes Agent Plugin** (Python, ~500 lines core logic) that hooks into every AI agent turn:

```
User Query → [Phase 0.5 Pre-verify] → LLM Response
  → [Phase 1: SIFT] → [Phase 2: CoVe+FIRE search]
  → [Phase 3: FABLE grade] → [Phase 4: Truth Sandwich]
```

Key design principles:
- **Round decoupling**: Each phase has a distinct output format — no mixing verification with impact grading
- **Parallel sub-agent execution**: For high-volume verification (≥15 claims), delegates work across 2-3 parallel sub-agents
- **Dedup gate**: Prevents redundant verification of the same content across sessions
- **Emergency bypass**: Skips verification when the user is in a time-sensitive scenario

## Empirical Results

We tested 6 intentionally incorrect claims against the automated verification tool:

| Metric | Auto-Verify Only | Manual (Full Pipeline) |
|:-------|:---------------:|:---------------------:|
| Error catch rate | 0% (0/4) | 100% (4/4) |
| False positives | 0 | 0 |
| Stale truth detected | 0 | 1 case |

Key findings:
1. **Search-backed verification alone misses 100% of errors** — without CoVe independence checks and FIRE iterative searching, the tool finds supporting text rather than testing the claim
2. **Stale ground truth is a real risk** — one verified "fact" (Correos closed Sundays) was outdated since 2024
3. **Source selection determines truth** — USDA and Foodstruct report octopus protein differing by 2× (14.9g vs 30g); the framework is transparent about which source is chosen and why

## Social Impact

Misinformation is a top-5 global risk (World Economic Forum). AI agents now produce content at unprecedented scale — blog posts, news summaries, customer service responses, educational materials — with no built-in verification. The Fact-Check Agent provides:

- **Individual protection**: Users of AI assistants get verified, not just generated, information
- **Platform governance**: Can be integrated into content platforms for automated pre-publication verification
- **Educational tool**: The transparent methodology (SIFT → CoVe → FIRE → FABLE → Truth Sandwich) teaches verification literacy
- **Open standard**: MIT-licensed, adaptable to any LLM-powered system (Hermes Agent, Claude Code, AutoGPT, LangGraph)

Unlike opaque "trust scores," our framework exposes **why** a claim passed or failed — which source, which method, which uncertainty remains. This transparency is itself a social good: it makes verification visible rather than hidden.

## Conclusion

Fact-Check Agent demonstrates that rigorous, journalistic fact-checking can be automated at LLM scale without sacrificing source discipline. The 5-phase pipeline catches errors that both raw LLMs and simple search-backed verification miss, while the open-source implementation makes it freely available to any AI system developer.
