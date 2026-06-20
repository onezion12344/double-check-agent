"""
Core verification engine for Hermes Fact-Check Plugin.

Pure functions — no Hermes API dependency. Uses duckduckgo_search (free, no API key)
for web search verification.
"""

import json
import re
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".hermes" / "plugins" / "fact-check" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HAS_DDG = False
try:
    from ddgs import DDGS
    HAS_DDG = True
except ImportError:
    pass

# ── Pattern detection ──────────────────────────────────────────

PRICE_RE = re.compile(r'[¥$€£]\s*\d+(?:[.,]\d+)?')
TIME_RE = re.compile(r'\d{1,2}[:.]\d{2}\s*(?:am|pm|AM|PM)?')
NUM_RE = re.compile(r'\b\d{3,}\b')
URL_RE = re.compile(r'https?://[^\s]+')

TIME_SENSITIVE_PATTERNS = [
    re.compile(r'[¥$€£]'),
    re.compile(r'\d{1,2}[:.]\d{2}'),
    re.compile(r'开[门关]|营[业]|时[间候]'),
    re.compile(r'价[格钱]|售[价]|成[本]|花[费]|多[少钱]'),
    re.compile(r'地[址点]|位[于]|在[哪]|路[线]|怎么去'),
    re.compile(r'hou[rs]|open|close|price|cost|address|location',
               re.IGNORECASE),
    re.compile(r'schedule|timetable|operating|business'),
]

FACTUAL_PATTERNS = [
    (re.compile(r'[¥$€£]\s*\d+'), 'price'),
    (re.compile(r'\d{1,2}[:.]\d{2}'), 'time'),
    (re.compile(r'地[址点]|位[于]|在[哪]|address|location', re.IGNORECASE), 'address'),
    (re.compile(r'\b\d{4,}\b'), 'number'),
    (re.compile(r'价[格钱]|多少[钱]|预算|成本|价格|多少钱|花多少|售价'), 'price_cn'),
    (re.compile(r'几点|什么时候|营业|关门|开门|时间|开门时间'), 'time_cn'),
    (re.compile(r'在哪|怎么去|地址|路线|坐标'), 'address_cn'),
]


def has_factual_content(text: str) -> bool:
    """Quick regex scan: does text contain factual patterns?"""
    if not text or len(text) < 10:
        return False
    return any(p[0].search(text) for p in FACTUAL_PATTERNS)


def count_factual_markers(text: str) -> int:
    """Count number of price + large-number markers in text."""
    if not text:
        return 0
    prices = len(PRICE_RE.findall(text))
    nums = len(NUM_RE.findall(text))
    return prices + nums


def is_time_sensitive(claim: str) -> bool:
    """Does this claim need current/web verification?"""
    return any(p.search(claim.lower()) for p in TIME_SENSITIVE_PATTERNS)


# ── Web search ─────────────────────────────────────────────────

def web_search(query: str, max_results: int = 3) -> list[dict]:
    """Search the web via DuckDuckGo. Returns [{title, url, snippet}]."""
    if not HAS_DDG:
        return []
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
            return results
    except Exception:
        return []


def multi_angle_search(claim: str, max_per_angle: int = 3) -> list[dict]:
    """Search from 2 different angles. Returns deduplicated sources."""
    results = web_search(claim, max_per_angle)
    if results:
        # Second angle: extract main terms
        # Remove price symbols and common words for a cleaner second query
        terms = re.sub(r'[¥$€£,，。]', '', claim)
        terms = re.sub(r'\s+', ' ', terms).strip()[:80]
        results2 = web_search(terms, max_per_angle)
        results.extend(results2)

    # Deduplicate by URL
    seen = set()
    unique = []
    for r in results:
        url = r.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(r)
    return unique[:6]


# ── Claim verification ─────────────────────────────────────────

def verify_single(claim: str, force_search: bool = True) -> dict:
    """Verify a single claim with optional web search.

    Returns:
        {"claim": str, "status": "✅"|"🔧"|"⚡"|"❌",
         "correct": str, "sources": [dict], "note": str}
    """
    needs_search = force_search or is_time_sensitive(claim)

    if not needs_search:
        return {
            "claim": claim,
            "status": "⚠️",
            "correct": "",
            "sources": [],
            "note": "Not time-sensitive. Verify with verify_claims tool if needed.",
        }

    sources = multi_angle_search(claim)

    if not sources:
        return {
            "claim": claim,
            "status": "❌",
            "correct": "",
            "sources": [],
            "note": "No web search results. Cannot verify.",
        }

    # Count independent sources by domain
    domains = set()
    for s in sources:
        try:
            from urllib.parse import urlparse
            domain = urlparse(s.get("url", "")).netloc
            if domain:
                domains.add(domain)
        except Exception:
            pass

    num_domains = len(domains)
    num_results = len(sources)

    if num_domains >= 2:
        status = "✅"
        note = f"Confirmed by {num_domains} independent sources ({num_results} results)"
    elif num_domains == 1 and num_results >= 2:
        status = "⚡"
        note = f"Multiple results from same source ({num_results} results, {num_domains} domain). Needs second independent source."
    else:
        status = "⚡"
        note = f"Only {num_results} result(s) from {num_domains} domain(s). Low confidence."

    return {
        "claim": claim,
        "status": status,
        "correct": "",
        "sources": sources[:5],
        "note": note,
    }


def batch_verify(claims: list[str], time_sensitive_default: bool = True) -> list[dict]:
    """Verify multiple claims in batch."""
    return [
        verify_single(c, force_search=time_sensitive_default or is_time_sensitive(c))
        for c in claims
    ]


# ── Post-check ─────────────────────────────────────────────────

def fast_post_check(text: str) -> list[dict]:
    """Quick regex-based scan of response text for potential issues.

    Returns list of error dicts or empty list.
    No LLM calls — purely pattern-based for speed.
    """
    errors = []
    if not text or len(text) < 200:
        return errors

    # Check for prices without source attribution
    prices = PRICE_RE.findall(text)
    if len(prices) >= 3:
        has_source = any(
            w in text.lower()
            for w in ["source", "according to", "per", "据", "来源", "官网", "查"]
        )
        if not has_source:
            errors.append({
                "what_was_written": f"Multiple prices ({len(prices)} found) without sources",
                "correction": "Add source attribution for each price",
                "severity": "experience",
                "type": "unverified_prices",
            })

    # Check for URLs that look like they contain verification data
    urls = URL_RE.findall(text)
    if len(prices) >= 2 and not urls:
        errors.append({
            "what_was_written": f"{len(prices)} prices mentioned without supporting URLs",
            "correction": "Cite sources for prices",
            "severity": "cosmetic",
            "type": "missing_citations",
        })

    return errors


# ── Formatting ──────────────────────────────────────────────────

def format_verification_context(results: list[dict]) -> str:
    """Format verification results as context injection for the LLM."""
    if not results:
        return ""

    lines = ["【Fact-Check Pre-verification】"]
    for r in results:
        tag = r.get("status", "?")
        claim = r.get("claim", "")
        correct = r.get("correct", "")
        note = r.get("note", "")

        if tag == "✅":
            lines.append(f"✅ {claim} (confirmed: {note})")
        elif tag == "🔧":
            lines.append(f"🔧 {claim} → {correct}")
        elif tag == "⚡":
            lines.append(f"⚡ {claim} — {note}")
        elif tag == "❌":
            lines.append(f"❌ {claim} — {note}")

    lines.append(
        "\nUse the above verified information. "
        "For ⚡ items, acknowledge uncertainty. "
        "For 🔧 items, use the corrected value."
    )
    return "\n".join(lines)


def format_truth_sandwich(errors: list[dict]) -> str:
    """Format as Truth Sandwich correction block."""
    if not errors:
        return ""

    critical = [e for e in errors if e.get("severity") == "critical"]
    experience = [e for e in errors if e.get("severity") == "experience"]
    cosmetic = [e for e in errors if e.get("severity") == "cosmetic"]

    parts = ["📋 **Fact-Check Post-Verification**\n"]

    if critical:
        parts.append("🔴 **May need correction:**")
        for e in critical:
            parts.append(f"• {e.get('what_was_written', '')}")
            if e.get("correction"):
                parts.append(f"  → {e['correction']}")
        parts.append("")

    if experience:
        parts.append("🟡 **Consider reviewing:**")
        for e in experience:
            parts.append(f"• {e.get('what_was_written', '')}")
            if e.get("correction"):
                parts.append(f"  → {e['correction']}")
        parts.append("")

    if cosmetic:
        parts.append("🟢 **Minor:**")
        for e in cosmetic:
            parts.append(f"• {e.get('what_was_written', '')}")
            if e.get("correction"):
                parts.append(f"  → {e['correction']}")

    return "\n".join(parts)


def format_verify_tool_output(results: list[dict]) -> str:
    """Format verification results for the verify_claims tool output."""
    summary = {"✅": 0, "🔧": 0, "⚡": 0, "❌": 0, "⚠️": 0}
    for r in results:
        s = r.get("status", "⚠️")
        summary[s] = summary.get(s, 0) + 1

    lines = [
        "═══════════════════════════════════════",
        "  Fact-Check Verification Results",
        f"  ✅ {summary.get('✅',0)} confirmed  🔧 {summary.get('🔧',0)} corrected  ⚡ {summary.get('⚡',0)} disputed  ❌ {summary.get('❌',0)} unverifiable",
        "═══════════════════════════════════════\n",
    ]

    for r in results:
        tag = r.get("status", "⚠️")
        claim = r.get("claim", "")
        correct = r.get("correct", "")
        note = r.get("note", "")
        sources = r.get("sources", [])

        lines.append(f"{tag} **{claim}**")
        if correct:
            lines.append(f"   → Correct: {correct}")
        if note:
            lines.append(f"   → {note}")
        for s in sources[:2]:
            title = s.get("title", "")
            url = s.get("url", "")
            if url:
                lines.append(f"   → [{title}]({url})")
        lines.append("")

    return "\n".join(lines)


def create_diagnostic_report(
    claims: list[str],
    results: list[dict],
    duration_ms: int,
) -> dict:
    """Create a structured diagnostic report for logging."""
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "claims_count": len(claims),
        "duration_ms": duration_ms,
        "summary": {
            "confirmed": sum(1 for r in results if r.get("status") == "✅"),
            "corrected": sum(1 for r in results if r.get("status") == "🔧"),
            "disputed": sum(1 for r in results if r.get("status") == "⚡"),
            "unverifiable": sum(1 for r in results if r.get("status") == "❌"),
        },
        "results": results,
    }
