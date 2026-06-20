"""
Fact-Check Plugin for Hermes Agent.

Hybrid verification framework merging journalism standards (SIFT, IFCN)
with LLM academic research (CoVe, FIRE, FABLE) into a 5-phase pipeline.

Hooks into Hermes lifecycle:
  - pre_llm_call: Phase 0.5 — verify user's factual questions before answering
  - transform_llm_output: Lightweight post-check on dense responses
  - post_llm_call: Background trigger for full Round 1-4 (future)

Tools:
  - verify_claims: Agent-driven factual claim verification via web search

Commands:
  - /factcheck: Manual trigger for full 4-round fact-check
"""

import json
import re
import time
import logging
from pathlib import Path

from . import verify

logger = logging.getLogger("plugins.fact-check")
CACHE_DIR = Path.home() / ".hermes" / "plugins" / "fact-check" / "cache"


# ── Phase 0.5 trigger patterns ─────────────────────────────────

QUESTION_PATTERNS = re.compile(
    r'(多少钱|价格|预算|成本|花了多少|售价|多少钱一个|'
    r'几点|什么时候|营业时间|开门|关门|时间表|时刻表|'
    r'在哪|地址|怎么去|路线|坐标|怎么走|'
    r'是什么牌子|怎么样|好不好|怎么样的|'
    r'几公里|多大面积|多长|多宽|多少|多重|'
    r'哪个好|哪个便宜|哪个性价比|'
    r'参数|配置|规格|尺寸|'
    r'how much|price|cost|how long|how far|how many|'
    r'where is|address|location|hours|schedule|'
    r'open|close|specs|specifications)',
    re.IGNORECASE,
)


def _has_question_marker(text: str) -> bool:
    """Fast pre-check: does text look like a factual question?"""
    return bool(QUESTION_PATTERNS.search(text[:300]))


# ── register() ──────────────────────────────────────────────────

def register(ctx):
    """Register all fact-check hooks, tools, and commands."""

    # ════════════════════════════════════════════════════════════
    # TOOL: verify_claims
    # ════════════════════════════════════════════════════════════
    verify_schema = {
        "name": "verify_claims",
        "description": (
            "Verify factual claims using web search. "
            "Pass a list of claim strings. Returns per-claim status: "
            "✅ confirmed / 🔧 corrected / ⚡ disputed / ❌ unverifiable.\n\n"
            "Call this BEFORE answering time-sensitive questions about "
            "prices, hours, addresses, or specifications. "
            "The agent should always call this when the user asks about costs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claims": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "List of factual claims to verify. "
                        "Example: [\"Nillkin keyboard costs ¥200\", "
                        "\"Correos opens on Sundays\"]"
                    ),
                },
            },
            "required": ["claims"],
        },
    }

    def handle_verify(params, **kwargs):
        claims = params.get("claims", [])
        if not claims:
            return json.dumps(
                {"error": "No claims provided", "results": []}, ensure_ascii=False
            )

        t0 = time.time()
        results = verify.batch_verify(claims, time_sensitive_default=True)
        duration_ms = int((time.time() - t0) * 1000)

        # Log diagnostic report
        report = verify.create_diagnostic_report(claims, results, duration_ms)
        report_path = CACHE_DIR / f"verify-{int(t0)}.json"
        try:
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2, default=str)
            )
        except Exception:
            pass

        output = verify.format_verify_tool_output(results)
        return output

    ctx.register_tool(
        name="verify_claims",
        toolset="fact_check",
        schema=verify_schema,
        handler=handle_verify,
        description=(
            "Verify factual claims using web search. "
            "Call BEFORE answering questions about prices, hours, or addresses."
        ),
    )

    # ════════════════════════════════════════════════════════════
    # HOOK: pre_llm_call — Phase 0.5 (Pre-answer verification)
    # ════════════════════════════════════════════════════════════
    def pre_llm_hook(user_message, is_first_turn, **kwargs):
        """
        Phase 0.5 — Before the agent answers:
        1. Check if user question has factual claims
        2. If yes, do quick pre-verification
        3. Inject verified context into the LLM call
        """
        if not user_message or len(user_message) < 15:
            return None

        # Fast regex pre-check (avoids LLM call for non-factual questions)
        if not _has_question_marker(user_message):
            return None

        # Use LLM to classify the question type
        try:
            classification = ctx.llm.complete(
                "Does this user question ask about any of the following? "
                "1. Prices or costs\n"
                "2. Times, hours, schedules\n"
                "3. Addresses or locations\n"
                "4. Product specifications or parameters\n"
                "5. Numerical values or measurements\n\n"
                "Reply with ONLY 'yes' or 'no'.\n\n"
                f"Question: {user_message[:500]}"
            )
        except Exception as e:
            logger.warning("pre_llm classification failed: %s", e)
            return None

        if classification and classification.strip().lower().startswith("yes"):
            # Extract specific claims for pre-verification
            try:
                claims_raw = ctx.llm.complete(
                    "Extract ALL specific factual claims the user is asking about. "
                    "Include prices, times, addresses, names, and numbers.\n"
                    "Return as a JSON array of strings, e.g.:\n"
                    '["Nillkin keyboard price", "Correos opening hours"]\n'
                    "If no specific claims, return empty array [].\n\n"
                    f"Question: {user_message[:1000]}"
                )
                claims = json.loads(claims_raw)
            except (json.JSONDecodeError, TypeError, Exception):
                claims = []

            if claims:
                # Clean and deduplicate claims
                claims = [c.strip() for c in claims if c.strip() and len(c.strip()) > 3]
                claims = list(dict.fromkeys(claims))  # preserve order, dedup

                if claims:
                    t0 = time.time()
                    # Only time-sensitive claims get web search in pre-answer (fast path)
                    results = []
                    for c in claims:
                        if verify.is_time_sensitive(c):
                            results.append(
                                verify.verify_single(c, force_search=True)
                            )
                        else:
                            results.append(
                                {"claim": c, "status": "⚠️", "correct": "",
                                 "sources": [], "note": "General knowledge — verify if needed"}
                            )

                    duration_ms = int((time.time() - t0) * 1000)
                    logger.info(
                        "Phase 0.5: %d claims pre-verified in %dms",
                        len(claims), duration_ms,
                    )

                    context = verify.format_verification_context(results)
                    if context:
                        return {"context": context}

        return None

    ctx.register_hook("pre_llm_call", pre_llm_hook)

    # ════════════════════════════════════════════════════════════
    # HOOK: transform_llm_output — Post-answer lightweight check
    # ════════════════════════════════════════════════════════════
    def transform_output(response_text, **kwargs):
        """
        Lightweight post-answer check.
        Fires before response is delivered to user.
        Only triggers on dense responses (≥300 chars + factual markers).
        Uses regex patterns ONLY — no LLM call to keep it fast.
        """
        if not response_text or len(response_text) < 300:
            return None

        factual_count = verify.count_factual_markers(response_text)
        if factual_count < 5:
            return None

        errors = verify.fast_post_check(response_text)
        if not errors:
            return None

        correction = verify.format_truth_sandwich(errors)
        return response_text + "\n\n" + correction

    ctx.register_hook("transform_llm_output", transform_output)

    # ════════════════════════════════════════════════════════════
    # COMMAND: /factcheck
    # ════════════════════════════════════════════════════════════
    def handle_factcheck(args):
        """Manually trigger fact-check."""
        return (
            "🔍 **Fact-Check Plugin Active**\n\n"
            "The plugin is running. Factual claims in your questions are "
            "automatically pre-verified before I answer.\n\n"
            "To verify specific claims, tell me:\n"
            '  "verify these claims: [list your claims]"'
        )

    ctx.register_command(
        name="factcheck",
        handler=handle_factcheck,
        description="Show fact-check plugin status and usage",
    )

    logger.info("Fact-Check Plugin v1.1.0 loaded — hooks, tool, and command registered")
