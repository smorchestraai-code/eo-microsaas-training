#!/usr/bin/env python3
"""
eo-brain-ingester/parse.py — resilient EO-Brain input parser

Takes an EO-Brain root directory and returns a single JSON BrainStructure
that captures everything /1-eo-dev-start needs to scaffold a project.

Design contract (Postel's law):
- Be liberal in what we accept: drifted headers, missing files, partial
  content, alt phrasings, Arabic + English mixed.
- Be strict in what we produce: a single canonical JSON shape.
- Hard-refuse only on TWO conditions:
    (a) EO-Brain directory does not exist
    (b) BRD has zero AC-N.N tags (genuine emptiness)
  Everything else: parse, normalize, surface warnings, proceed.

Usage:
    python3 parse.py <eo_brain_path> [--pretty] [--strict]
    python3 parse.py <eo_brain_path> --self-test

Exit codes:
    0 — parse succeeded (BrainStructure printed to stdout as JSON)
    1 — invalid arguments
    2 — refused (refuse reason in stderr; partial JSON to stdout if --strict not set)

Tested against:
- 9 fixture EO-Brain folders in fixtures/
- The canonical EO Oasis MENA BRD at 10-EO-Brain-Starter-Kit Final/
"""

import sys
import os
import re
import json
import glob
import hashlib
import argparse
from pathlib import Path
from datetime import datetime


# ----------------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------------

# Loop keywords for inference (Step 8b). Per loop, a list of strings to grep for.
LOOP_KEYWORDS = {
    "auth": [
        "registration", "register", "signup", "sign-up", "sign up",
        "login", "log in", "logout", "log out", "session", "auth",
        "OTP", "2FA", "password", "reset password", "verify email",
        "تسجيل", "دخول", "كلمة المرور", "OTP",
    ],
    "domain": [
        "dashboard", "submit", "submission", "list", "create", "edit",
        "view", "search", "filter", "browse", "directory", "catalog",
        "feed", "form", "wizard", "moderation", "queue",
        "لوحة", "إرسال", "بحث", "فلترة",
    ],
    "money": [
        "pricing", "tier", "checkout", "payment", "subscribe", "subscription",
        "Tap", "HyperPay", "Stripe", "Moyasar", "PayTabs", "Mada",
        "webhook", "billing", "invoice", "refund", "discount",
        "دفع", "اشتراك", "فاتورة",
    ],
    "notify": [
        "email", "WhatsApp", "SMS", "notification", "Resend", "Unifonic",
        "Twilio", "GHL", "send", "notify", "message", "alert",
        "بريد", "واتساب", "إشعار",
    ],
    "deploy": [
        "deploy", "subdomain", "SSL", "DNS", "/api/health", "production",
        "Contabo", "VPS", "Vercel", "Hetzner", "Railway",
    ],
    "observability": [
        "Sentry", "PostHog", "uptime", "monitor", "monitoring",
        "analytics", "logging", "metric", "trace",
    ],
    "compliance": [
        "RLS", "row-level security", "row level security", "policy",
        "PDPL", "GDPR", "data residency", "audit log", "audit",
        "secret", "encrypt", "rate limit",
    ],
}

# Story header patterns, tried in order. First match wins per story number.
# Each pattern uses {N} placeholder for story number.
STORY_HEADER_PATTERNS = [
    (r"^###\s+Story\s+{N}\b[:\s]*(.+?)\s*$", "h3-header"),
    (r"^##\s+Story\s+{N}\b[:\s]*(.+?)\s*$", "h2-header"),
    (r"^####+\s*Story\s+{N}\b[:\s]*(.+?)\s*$", "deeper-header"),
    (r"^Story\s+{N}\b[:\s]*(.+?)\s*$", "no-header"),
    (r"^User Story\s+{N}\b[:\s]*(.+?)\s*$", "user-story-prefix"),
    (r"^قصَّة\s+{N}\b[:\s]*(.+?)\s*$", "arabic-title"),
    (r"^القصَّة\s+{N}\b[:\s]*(.+?)\s*$", "arabic-alt"),
]

# MENA + ICP keywords used by language detection + identity heuristics
MENA_KEYWORDS_AR = ["العربية", "خليجي", "MENA", "السعودية", "الإمارات", "مصر",
                    "الأردن", "الكويت", "قطر", "البحرين", "عُمان"]
MENA_KEYWORDS_EN = ["MENA", "Saudi", "Arabia", "UAE", "Egypt", "Jordan",
                    "Kuwait", "Qatar", "Bahrain", "Oman", "Arabic", "Gulf"]

# Country detection: maps explicit country mentions in profile-settings.md
# to ISO codes. Used to pick the right payment provider default.
COUNTRY_MARKERS = [
    # ISO, English markers, Arabic markers
    ("AE", ["UAE", "United Arab Emirates", "Dubai", "Abu Dhabi", "Sharjah"], ["الإمارات", "دبي", "أبوظبي"]),
    ("SA", ["Saudi Arabia", "KSA", "Riyadh", "Jeddah", "Saudi"], ["السعودية", "الرياض", "جدة"]),
    ("BH", ["Bahrain", "Manama"], ["البحرين", "المنامة"]),
    ("KW", ["Kuwait"], ["الكويت"]),
    ("QA", ["Qatar", "Doha"], ["قطر", "الدوحة"]),
    ("OM", ["Oman", "Muscat"], ["عُمان", "عمان", "مسقط"]),
    ("EG", ["Egypt", "Cairo", "Alexandria"], ["مصر", "القاهرة"]),
    ("JO", ["Jordan", "Amman"], ["الأردن", "عمّان"]),
]

# Stripe support map (verified 2024-Q4).
# When founder_country is supported and BRD doesn't explicitly name another
# provider as primary, default to Stripe (it's part of SaaSfast natively,
# handles subscriptions natively, no MADA needed for these markets).
STRIPE_SUPPORTED_COUNTRIES = {"AE", "SA", "BH", "KW", "US", "GB", "DE", "FR", "CA", "AU", "IE", "NL", "SE", "DK", "FI", "NO", "ES", "IT"}

# Country → preferred-fallback-when-Stripe-unavailable map
# Egypt: PayTabs/Fawry. Jordan/Qatar/Oman: Tap.
NON_STRIPE_FALLBACK = {
    "EG": "PayTabs",
    "JO": "Tap",
    "QA": "Tap",
    "OM": "Tap",
}

# Banned buzzwords (used in voice extraction)
BANNED_BUZZWORDS = [
    "leverage", "synergy", "ecosystem", "holistic", "digital transformation",
    "innovative", "cutting-edge", "world-class", "best-in-class",
]


# ----------------------------------------------------------------------------
# UTILITIES
# ----------------------------------------------------------------------------

def read_text(path):
    """Read a file's text, return None if missing."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        return None


def file_checksum(path):
    """SHA256 of file content. Used to verify EO-Brain source untouched."""
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except (FileNotFoundError, IsADirectoryError):
        return None


def first_match(patterns, text):
    """Return first regex pattern that matches in text, with .group(1) extracted."""
    for pat in patterns:
        m = re.search(pat, text, re.MULTILINE)
        if m:
            return m.group(1).strip()
    return None


def glob_first(eo_brain, *globs):
    """Return first existing file matching any glob (relative to eo_brain)."""
    for g in globs:
        for p in sorted(glob.glob(os.path.join(eo_brain, g), recursive=True)):
            if os.path.isfile(p):
                return p
    return None


# ----------------------------------------------------------------------------
# REFUSAL
# ----------------------------------------------------------------------------

class Refused(Exception):
    def __init__(self, reason, remediation):
        self.reason = reason
        self.remediation = remediation
        super().__init__(reason)


def refuse(reason, remediation):
    raise Refused(reason, remediation)


# ----------------------------------------------------------------------------
# PHASE 0-3 + 5 NORMALIZERS
# ----------------------------------------------------------------------------

def parse_language(eo_brain, brd_text, warnings):
    """Read _language-pref.md or detect from BRD content."""
    lang_file = os.path.join(eo_brain, "_language-pref.md")
    txt = read_text(lang_file)
    if txt:
        m = re.search(r"^\s*(?:lang|language)\s*[:=]\s*(\w+)", txt, re.I | re.M)
        if m:
            return {"lang": m.group(1).lower(), "source": "_language-pref.md"}
        # Fall through: file exists but no parseable lang line
        warnings.append("_language-pref.md present but no parseable lang: line — falling back to BRD content detection")

    # Detect from BRD content
    if brd_text:
        ar_hits = sum(1 for kw in MENA_KEYWORDS_AR if kw in brd_text)
        if ar_hits >= 2 or re.search(r"[؀-ۿ]", brd_text):  # Arabic Unicode
            warnings.append("_language-pref.md missing — inferred lang=ar from Arabic content in BRD")
            return {"lang": "ar", "source": "inferred-from-brd"}
    warnings.append("_language-pref.md missing — defaulted to lang=en")
    return {"lang": "en", "source": "default"}


def parse_identity(eo_brain, warnings, questions):
    """Extract founder + project identity. Multi-source with graceful fallback.
    Pushes blocking questions to `questions[]` when critical inputs unresolved."""
    identity = {
        "project_name": None,
        "project_name_source": None,
        "founder_name": None,
        "founder_name_source": None,
        "founder_email": None,
        "icp_summary": None,
        "voice_notes": [],
    }

    # ─── Source 1: profile-settings.md ──────────────────────────────────────
    # Format varies wildly: YAML, key:value, prose paragraphs under section headers
    profile_path = glob_first(eo_brain, "1-ProjectBrain/profile-settings.md",
                                "1-ProjectBrain/**/profile-settings.md")
    if profile_path:
        txt = read_text(profile_path) or ""

        # 1a — YAML frontmatter
        ym = re.match(r"^---\s*\n(.+?)\n---", txt, re.S)
        if ym:
            for key, slot in [("founder", "founder_name"), ("name", "founder_name"),
                              ("email", "founder_email"), ("project", "project_name"),
                              ("product", "project_name")]:
                m = re.search(rf"^\s*{key}\s*:\s*(.+?)\s*$", ym.group(1), re.I | re.M)
                if m and not identity[slot]:
                    identity[slot] = m.group(1).strip().strip('"\'')
                    identity[slot + "_source"] = "profile-settings.md (yaml)" if slot.endswith("_name") else None

        # 1b — Inline key:value (works on flat key:value style)
        for key, slot in [("founder", "founder_name"), ("name", "founder_name"),
                          ("email", "founder_email"), ("project", "project_name"),
                          ("product", "project_name")]:
            if not identity[slot]:
                m = re.search(rf"^\s*{key}\s*[:=]\s*(.+?)\s*$", txt, re.I | re.M)
                if m:
                    identity[slot] = m.group(1).strip()
                    if slot.endswith("_name"):
                        identity[slot + "_source"] = "profile-settings.md (key:value)"

        # 1c — Prose under section headers (IDENTITY / WHO I AM / ABOUT ME)
        # Pattern: a line that's just "IDENTITY" or "## IDENTITY" or "Identity",
        # followed by paragraphs. First paragraph's first sentence usually = "Name. Role of Project (...)"
        for marker in ["IDENTITY", "Identity", "WHO I AM", "About Me", "ABOUT ME"]:
            m = re.search(rf"^#*\s*{marker}\s*$\n+(.+?)(?:\n\n|$)", txt, re.M | re.S)
            if m:
                first_para = m.group(1).strip()
                # First sentence usually = "Name. Role of Project (...)" or "Name, Role at Project."
                # Extract the name = first 1-4 words ending at first period
                name_m = re.match(r"^([A-Z][\w'\-]+(?:\s+[A-Z][\w'\-]+){0,3})[\.\,]", first_para)
                if name_m and not identity["founder_name"]:
                    identity["founder_name"] = name_m.group(1).strip()
                    identity["founder_name_source"] = f"profile-settings.md (prose under {marker})"
                # Extract project = "Founder of <PROJECT>" / "Founder of <PROJECT> (..."
                proj_patterns = [
                    r"[Ff]ounder of ([A-Z][\w\.\- ]+?)(?:\s*\(|\s*[\.,;]|\s+and\s|$)",
                    r"[Bb]uilding ([A-Z][\w\.\- ]+?)(?:\s*\(|\s*[\.,;]|$)",
                    r"[Cc]reator of ([A-Z][\w\.\- ]+?)(?:\s*\(|\s*[\.,;]|$)",
                ]
                for pat in proj_patterns:
                    pm = re.search(pat, first_para)
                    if pm and not identity["project_name"]:
                        candidate = pm.group(1).strip()
                        # Filter out generic words
                        if candidate.lower() not in ("a", "the", "an", "their", "his", "her"):
                            identity["project_name"] = candidate
                            identity["project_name_source"] = f"profile-settings.md (prose: 'Founder of {candidate}')"
                            break
                break  # first matched marker wins

    # ─── Source 2: bootstrap-prompt.md (Phase 5) ─────────────────────────────
    bootstrap_path = glob_first(eo_brain, "5-CodeHandover/references/bootstrap-prompt.md",
                                  "5-CodeHandover/bootstrap-prompt.md",
                                  "5-CodeHandover/README.md")
    if bootstrap_path:
        txt = read_text(bootstrap_path) or ""
        for key, slot, source_label in [
            ("Name", "project_name", "bootstrap-prompt.md (Name:)"),
            ("Product", "project_name", "bootstrap-prompt.md (Product:)"),
            ("Founder", "founder_name", "bootstrap-prompt.md (Founder:)"),
            ("ICP", "icp_summary", None),
        ]:
            m = re.search(rf"^[\*\-\s]*{key}\s*[:\*]+\s*\[?(.+?)\]?\s*$", txt, re.M)
            if m and not identity[slot]:
                v = m.group(1).strip().rstrip("*").strip()
                if not (v.startswith("[") and v.endswith("]")) and v.lower() not in ("tbd", "todo", "n/a"):
                    identity[slot] = v
                    if slot.endswith("_name") and source_label:
                        identity[slot + "_source"] = source_label

    # ─── Source 3: companyprofile.md / founderprofile.md ─────────────────────
    if not identity["project_name"]:
        company_path = glob_first(eo_brain, "1-ProjectBrain/**/companyprofile.md",
                                    "1-ProjectBrain/companyprofile.md")
        if company_path:
            txt = read_text(company_path) or ""
            # First H1 that isn't a generic doc title
            for m in re.finditer(r"^#\s+(.+?)\s*$", txt, re.M):
                title = m.group(1).strip()
                if title.lower() not in ("company profile", "companyprofile", "company"):
                    # Strip "X — " prefix if present (e.g. "Company Profile — EO Oasis")
                    title = re.sub(r"^[A-Z][\w\s]+[—\-:]\s*", "", title).strip()
                    identity["project_name"] = title
                    identity["project_name_source"] = "companyprofile.md (h1)"
                    break

    # ─── Source 4: BRD product line ──────────────────────────────────────────
    if not identity["project_name"]:
        brd_path = os.path.join(eo_brain, "4-Architecture/brd.md")
        txt = read_text(brd_path) or ""
        m = re.search(r"^\*\*Product:\*\*\s*(.+?)\s*$", txt, re.M)
        if m:
            identity["project_name"] = m.group(1).strip()
            identity["project_name_source"] = "brd.md (Product:)"

    # ─── Source 5: positioning.md (last resort, strip prefix) ────────────────
    if not identity["project_name"]:
        pos_path = glob_first(eo_brain, "1-ProjectBrain/**/positioning.md",
                                "1-ProjectBrain/positioning.md")
        if pos_path:
            txt = read_text(pos_path) or ""
            m = re.search(r"^#\s+(.+?)\s*$", txt, re.M)
            if m:
                title = m.group(1).strip()
                # Strip "Positioning — ", "Positioning: ", etc. prefixes
                title = re.sub(r"^[Pp]ositioning\s*[—\-:]\s*", "", title).strip()
                if title.lower() not in ("positioning", "brd", "icp"):
                    identity["project_name"] = title
                    identity["project_name_source"] = "positioning.md (h1, prefix stripped)"

    # ─── ICP extraction ──────────────────────────────────────────────────────
    icp_path = glob_first(eo_brain, "1-ProjectBrain/icp.md",
                            "1-ProjectBrain/**/icp.md")
    if icp_path and not identity["icp_summary"]:
        txt = read_text(icp_path) or ""
        bullets = re.findall(r"^[\-\*]\s+(.+?)\s*$", txt, re.M)
        if bullets:
            # Strip markdown bold/italic from bullets
            cleaned = [re.sub(r"\*\*(.+?)\*\*", r"\1", b) for b in bullets[:3]]
            cleaned = [re.sub(r"\*(.+?)\*", r"\1", b) for b in cleaned]
            identity["icp_summary"] = " · ".join(cleaned)
        else:
            paras = [p.strip() for p in txt.split("\n\n") if p.strip() and not p.strip().startswith("#")]
            if paras:
                identity["icp_summary"] = paras[0][:200]

    # ─── Brand voice ─────────────────────────────────────────────────────────
    voice_path = glob_first(eo_brain, "1-ProjectBrain/**/brandvoice.md",
                              "1-ProjectBrain/brandvoice.md")
    if voice_path:
        txt = read_text(voice_path) or ""
        if "Gulf" in txt or "خليجي" in txt or "Khaleeji" in txt.lower():
            identity["voice_notes"].append("Gulf conversational tone")
        if "MSA" in txt and "not MSA" in txt:
            identity["voice_notes"].append("Avoid MSA in Arabic output")
        for buzz in BANNED_BUZZWORDS:
            if buzz in txt.lower():
                identity["voice_notes"].append(f"Banned buzzword: {buzz}")

    # ─── Email fallback (always try git config) ──────────────────────────────
    if not identity["founder_email"]:
        try:
            import subprocess
            r = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                identity["founder_email"] = r.stdout.strip()
        except Exception:
            pass

    # ─── Generate blocking questions for unresolved critical inputs ──────────
    if not identity["founder_name"]:
        # Try git config one more time
        try:
            import subprocess
            r = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
            git_name = r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            git_name = ""
        questions.append({
            "key": "founder_name",
            "blocking": True,
            "prompt": "What's the founder name? (No profile-settings.md found with an extractable name.)",
            "default_suggestion": git_name or os.environ.get("USER", ""),
            "default_source": "git config user.name" if git_name else ("$USER" if os.environ.get("USER") else None),
        })

    if not identity["project_name"]:
        questions.append({
            "key": "project_name",
            "blocking": True,
            "prompt": "What's the project name? (Couldn't extract from profile-settings.md, companyprofile.md, brd.md Product:, or positioning.md.)",
            "default_suggestion": None,
            "default_source": None,
        })

    if not identity["icp_summary"]:
        # Soft warning — proceed with empty
        warnings.append("icp_summary not found — UX hat will cap at 8 until populated. Consider running 1-eo-template-factory in Cowork to fill icp.md.")
        identity["icp_summary"] = ""

    return identity


def parse_founder_country(eo_brain, warnings):
    """Extract founder country (ISO code) from profile-settings.md / founderprofile.md.
    Pattern: 'Based in Dubai' / 'located in Riyadh' / 'from Jordan' / Arabic equivalents.
    Returns ISO code (AE/SA/BH/KW/QA/OM/EG/JO) or None."""
    paths = []
    p1 = glob_first(eo_brain, "1-ProjectBrain/profile-settings.md",
                     "1-ProjectBrain/**/profile-settings.md")
    if p1:
        paths.append(p1)
    p2 = glob_first(eo_brain, "1-ProjectBrain/Project/founderprofile.md",
                     "1-ProjectBrain/**/founderprofile.md")
    if p2:
        paths.append(p2)
    if not paths:
        return None
    txt = "\n".join(read_text(p) or "" for p in paths)

    # Score by marker hits across ALL country markers; highest score wins
    scores = {}
    for iso, en_markers, ar_markers in COUNTRY_MARKERS:
        score = 0
        for kw in en_markers:
            score += len(re.findall(rf"\b{re.escape(kw)}\b", txt))
        for kw in ar_markers:
            score += txt.count(kw)
        if score > 0:
            scores[iso] = score
    if not scores:
        return None
    # Pick highest. Tiebreak: prefer current-residence markers ("Based in" / "located in")
    # by giving them double weight.
    for marker_pattern in [r"[Bb]ased in\s+(\w+)", r"[Ll]ocated in\s+(\w+)",
                           r"[Ll]iving in\s+(\w+)", r"[Hh]eadquartered in\s+(\w+)"]:
        m = re.search(marker_pattern, txt)
        if m:
            location_word = m.group(1)
            for iso, en_markers, _ in COUNTRY_MARKERS:
                if any(location_word.lower() == kw.lower() or location_word in kw for kw in en_markers):
                    scores[iso] = scores.get(iso, 0) + 10  # heavy tiebreak
    return max(scores, key=scores.get)


def pick_payment_default(country_iso, brd_text, warnings):
    """Country-aware payment provider default.

    Rule (v1.4.4):
    1. BRD explicitly names ONE provider → use it
    2. BRD names MULTIPLE providers → primary = Stripe IF Stripe-supported
       in founder country, else first non-Stripe in BRD order
    3. BRD silent + Stripe-supported country → Stripe (SaaSfast-native, best
       for subscriptions)
    4. BRD silent + non-Stripe country → fallback per NON_STRIPE_FALLBACK
    5. BRD silent + country unknown → Stripe (safest global default)

    Returns (primary_provider, fallback_providers, rationale).
    """
    brd_text = brd_text or ""
    # All providers mentioned in BRD
    in_brd = []
    for prov in ["Stripe", "Tap", "HyperPay", "Moyasar", "PayTabs", "Fawry"]:
        if re.search(rf"\b{prov}\b", brd_text):
            in_brd.append(prov)

    # Rule 1: single provider in BRD
    if len(in_brd) == 1:
        return (in_brd[0], [], f"BRD explicitly names {in_brd[0]}")

    # Rule 2: multiple in BRD
    if len(in_brd) > 1:
        if country_iso in STRIPE_SUPPORTED_COUNTRIES and "Stripe" in in_brd:
            others = [p for p in in_brd if p != "Stripe"]
            return ("Stripe", others,
                    f"BRD names {in_brd}; founder in {country_iso} (Stripe-supported); "
                    f"Stripe primary (SaaSfast-native, best subscriptions); "
                    f"{', '.join(others)} configured as fallbacks")
        # Country isn't Stripe-supported, or BRD doesn't mention Stripe
        return (in_brd[0], in_brd[1:],
                f"BRD names {in_brd}; primary={in_brd[0]} (BRD order); "
                f"{', '.join(in_brd[1:])} configured as fallbacks")

    # Rule 3-5: BRD silent
    if country_iso in STRIPE_SUPPORTED_COUNTRIES:
        return ("Stripe", [],
                f"founder in {country_iso} (Stripe-supported); "
                f"Stripe is SaaSfast-native default for subscriptions")
    fallback = NON_STRIPE_FALLBACK.get(country_iso, "Tap")
    if country_iso:
        return (fallback, [],
                f"founder in {country_iso} (Stripe not supported there); "
                f"{fallback} default for that market")
    warnings.append("founder country unknown — defaulted payment to Stripe (safest global)")
    return ("Stripe", [], "country unknown; Stripe global default")


def parse_stack(eo_brain, warnings, founder_country):
    """Extract tech stack + deploy lane + payment provider.
    v1.4.4: payment default is country-aware, NOT hardcoded Tap-for-MENA."""
    stack = {
        "frontend": "Next.js 14 + TypeScript + Tailwind",
        "backend": "Next.js API Routes",
        "db": "Postgres (Supabase managed)",
        "auth": "Supabase Auth",
        "payment_primary": None,
        "payment_fallbacks": [],
        "payment_rationale": None,
        "deploy_lane": "Contabo VPS",
        "mena": False,
        "rtl": False,
        "source": "default",
    }
    p = glob_first(eo_brain, "4-Architecture/tech-stack-decision.md")
    txt = ""
    if not p:
        warnings.append("tech-stack-decision.md missing — using MENA-safe defaults")
    else:
        txt = read_text(p) or ""
        stack["source"] = p

    # MENA flag detection
    if any(kw in txt for kw in MENA_KEYWORDS_EN + MENA_KEYWORDS_AR):
        stack["mena"] = True
        stack["rtl"] = True
    elif founder_country in {"AE", "SA", "BH", "KW", "QA", "OM", "EG", "JO"}:
        stack["mena"] = True
        stack["rtl"] = True

    # Stack fields (Frontend / Backend / DB / Auth)
    for key, slot in [("Frontend", "frontend"), ("Backend", "backend"),
                       ("Database", "db"), ("DB", "db"), ("Auth", "auth")]:
        m = re.search(rf"^[\-\*\s]*(?:{key}|{key.lower()})\s*[:=]\s*(.+?)\s*$", txt, re.M)
        if m:
            stack[slot] = m.group(1).strip()

    # Deploy lane
    for lane in ["Contabo", "Hetzner", "Railway", "Vercel", "Netlify", "AWS", "Oracle", "Azure"]:
        if re.search(rf"\b{lane}\b", txt):
            stack["deploy_lane"] = lane
            break

    # Payment: country-aware (the v1.4.4 fix)
    # Read BOTH tech-stack and BRD for explicit provider mentions
    brd_text = read_text(os.path.join(eo_brain, "4-Architecture", "brd.md")) or ""
    primary, fallbacks, rationale = pick_payment_default(
        founder_country, txt + "\n" + brd_text, warnings)
    stack["payment_primary"] = primary
    stack["payment_fallbacks"] = fallbacks
    stack["payment_rationale"] = rationale

    return stack


def parse_ux_artifacts(eo_brain, warnings):
    """Discover UX artifact files by glob. Never refuse on missing."""
    candidates = []
    for ext in ["html", "jsx", "tsx", "png", "jpg", "jpeg", "pdf", "svg"]:
        candidates.extend(sorted(glob.glob(os.path.join(eo_brain, f"5-CodeHandover/artifacts/*.{ext}"))))
        candidates.extend(sorted(glob.glob(os.path.join(eo_brain, f"5-CodeHandover/**/artifacts/*.{ext}"), recursive=True)))
    candidates = sorted(set(candidates))
    if not candidates:
        warnings.append("No UX artifacts found in 5-CodeHandover/artifacts/ — UX hat will cap at 8 until populated")
    return {"paths": candidates, "count": len(candidates)}


# ----------------------------------------------------------------------------
# MULTI-HAT INPUT SCORING (the v1.4.4 fix)
# ----------------------------------------------------------------------------

def score_inputs(brain):
    """5-hat score of the EO-Brain input quality. Each hat 0-10. Composite = sum × 2 (0-100).
    Founder sees this in the plan-mode preview. The plugin auto-bridges gaps where
    safe (e.g. infer carve tags) and surfaces remaining gaps as actionable founder
    items. Goal is 10/10 against what the input allows — never block, always surface."""
    hats = {
        "identity": 0,
        "stack": 0,
        "brd": 0,
        "ux": 0,
        "compliance": 0,
    }
    gaps = []  # list of {hat, gap, fix, severity, auto_bridgeable}

    # ─── Identity hat (0-10) ─────────────────────────────────────────────────
    s = 0
    if brain["identity"]["project_name"]:
        s += 2
    else:
        gaps.append({"hat": "identity", "gap": "project_name unresolved", "fix": "blocking question already in questions[]", "severity": "high", "auto_bridgeable": False})
    if brain["identity"]["founder_name"]:
        s += 2
    else:
        gaps.append({"hat": "identity", "gap": "founder_name unresolved", "fix": "blocking question already in questions[]", "severity": "high", "auto_bridgeable": False})
    if brain["identity"]["founder_email"]:
        s += 1
    else:
        gaps.append({"hat": "identity", "gap": "founder_email missing", "fix": "git config user.email or ask founder", "severity": "low", "auto_bridgeable": True})
    if brain["identity"]["icp_summary"]:
        s += 2
    else:
        gaps.append({"hat": "identity", "gap": "icp_summary empty", "fix": "run 1-eo-template-factory in Cowork to fill icp.md", "severity": "medium", "auto_bridgeable": False})
    if brain["identity"].get("founder_country"):
        s += 2
    else:
        gaps.append({"hat": "identity", "gap": "founder_country unresolved (affects payment default)", "fix": "add 'Based in {City}' to profile-settings.md, or accept Stripe global default", "severity": "low", "auto_bridgeable": True})
    if brain["identity"]["voice_notes"]:
        s += 1
    else:
        gaps.append({"hat": "identity", "gap": "no voice rules extracted from brandvoice.md", "fix": "fill brandvoice.md or accept global voice rules", "severity": "low", "auto_bridgeable": True})
    hats["identity"] = min(s, 10)

    # ─── Stack hat (0-10) ────────────────────────────────────────────────────
    s = 0
    st = brain["stack"]
    if st["frontend"] != "Next.js 14 + TypeScript + Tailwind" or "tech-stack-decision.md" in (st["source"] or ""):
        s += 2  # explicitly named or kept default
    else:
        gaps.append({"hat": "stack", "gap": "frontend = generic default (no tech-stack-decision.md detected)", "fix": "fill 4-Architecture/tech-stack-decision.md or accept default", "severity": "medium", "auto_bridgeable": False})
    if "tech-stack-decision.md" in (st["source"] or ""):
        s += 2
    else:
        gaps.append({"hat": "stack", "gap": "tech-stack-decision.md missing entirely", "fix": "run 4-eo-tech-architect in Cowork", "severity": "high", "auto_bridgeable": False})
    if st["payment_primary"]:
        s += 2
    if st["mena"] or st["payment_primary"] in ("Tap", "HyperPay", "Moyasar", "PayTabs", "Stripe"):
        s += 2
    if st["deploy_lane"] != "default":
        s += 2
    hats["stack"] = min(s, 10)

    # ─── BRD hat (0-10) ──────────────────────────────────────────────────────
    s = 0
    b = brain["brd"]
    if b["story_count"] >= 4:
        s += 2
    elif b["story_count"] >= 1:
        s += 1
        gaps.append({"hat": "brd", "gap": f"only {b['story_count']} story (Weekend MVP needs ≥4)", "fix": "expand BRD in Cowork via 4-eo-tech-architect", "severity": "high", "auto_bridgeable": False})
    if b["total_acs"] >= b["story_count"] * 3:
        s += 2
    if b["scope_shape"] == "canonical":
        s += 1
    elif b["scope_shape"] == "binary":
        s += 0  # will be normalized
        gaps.append({"hat": "brd", "gap": "SCOPE block is binary (no v2 Roadmap subsection)", "fix": "normalizer will inject canonical 3-block SCOPE — auto", "severity": "low", "auto_bridgeable": True})
    else:
        gaps.append({"hat": "brd", "gap": "no SCOPE block at all", "fix": "normalizer will inject canonical 3-block SCOPE — auto", "severity": "medium", "auto_bridgeable": True})
    if b["carve_state"] == "canonical":
        s += 1
    else:
        gaps.append({"hat": "brd", "gap": f"carve_state={b['carve_state']} (no [@WeekendMVP]/[@Phase2] tags)", "fix": f"normalizer will tag stories {b['proposed_carve']['weekend_mvp']}=MVP, {b['proposed_carve']['phase_2']}=Phase2 — founder approves", "severity": "medium", "auto_bridgeable": True})
    if b["loop_state"] == "canonical":
        s += 1
    else:
        gaps.append({"hat": "brd", "gap": f"loop_state={b['loop_state']} (no [loop:X] tags)", "fix": "normalizer infers loops from content via keyword scoring — founder approves", "severity": "medium", "auto_bridgeable": True})
    if b["loop_coverage"]["complete"]:
        s += 3
    else:
        missing = b["loop_coverage"]["missing"]
        gaps.append({
            "hat": "brd",
            "gap": f"Weekend MVP slice missing loops: {missing}",
            "fix": f"promote a Phase2 story up (mvp_loop_gap question in questions[]), or accept partial MVP",
            "severity": "high",
            "auto_bridgeable": False,
        })
    hats["brd"] = min(s, 10)

    # ─── UX hat (0-10) ───────────────────────────────────────────────────────
    s = 0
    n = brain["ux_artifacts"]["count"]
    if n >= 3:
        s += 6
    elif n >= 1:
        s += 4
        gaps.append({"hat": "ux", "gap": f"only {n} UX artifact(s) — founder may want product-demo + onboarding-flow + admin-dashboard for full coverage", "fix": "run 4-eo-code-handover Phase 4 in Cowork to generate the missing artifacts", "severity": "low", "auto_bridgeable": False})
    else:
        gaps.append({"hat": "ux", "gap": "no UX artifacts found — UX hat caps at 8 until populated", "fix": "run 4-eo-code-handover in Cowork", "severity": "medium", "auto_bridgeable": False})
    if brain["bootstrap_prompt"]:
        s += 2
    else:
        gaps.append({"hat": "ux", "gap": "no 5-CodeHandover/README.md (bootstrap prompt source)", "fix": "run 4-eo-code-handover in Cowork", "severity": "low", "auto_bridgeable": False})
    if brain["language"]["lang"] == "ar" and brain["stack"]["rtl"]:
        s += 2  # MENA project with RTL flag = correctly identified
    elif brain["language"]["lang"] == "en":
        s += 2  # English-only also fine
    hats["ux"] = min(s, 10)

    # ─── Compliance hat (0-10) ───────────────────────────────────────────────
    s = 0
    if brain["stack"]["mena"]:
        s += 3  # MENA flag set → arabic-rtl-checker + mena-mobile-check will run
    if brain["stack"]["rtl"]:
        s += 2
    if any("Supabase" in x for x in [brain["stack"]["db"], brain["stack"]["auth"]]):
        s += 2  # RLS available
    else:
        gaps.append({"hat": "compliance", "gap": "no Supabase in stack → RLS not auto-enforced", "fix": "if multi-tenant, switch to Supabase or add manual RLS layer", "severity": "medium", "auto_bridgeable": False})
    if brain["stack"]["payment_primary"]:
        s += 2  # webhook-signature-verification scaffold ships with the lib
    if brain["stack"]["deploy_lane"] not in ("Vercel",):
        s += 1  # not Vercel (per Mamoun's global rule)
    else:
        gaps.append({"hat": "compliance", "gap": "deploy lane = Vercel (banned per global rules — owned-infra only)", "fix": "switch to Contabo / Hetzner / Railway in tech-stack-decision.md", "severity": "high", "auto_bridgeable": False})
    hats["compliance"] = min(s, 10)

    composite = (hats["identity"] + hats["stack"] + hats["brd"] +
                 hats["ux"] + hats["compliance"]) * 2  # 0-100

    # Bridge plan: list gaps grouped by auto-bridgeable vs founder-action
    auto_bridges = [g for g in gaps if g.get("auto_bridgeable")]
    founder_actions = [g for g in gaps if not g.get("auto_bridgeable")]

    # Decision banner
    if composite >= 90:
        verdict = "✅ Ship-grade input. Plan-mode preview proceeds."
    elif composite >= 80:
        verdict = "🟡 Bridge-grade input. Apply auto-bridges + surface founder actions in plan-mode preview."
    elif composite >= 70:
        verdict = "🟠 Below ship gate. Auto-bridges will lift composite; founder actions surface in plan-mode preview."
    else:
        verdict = "🔴 Input has serious gaps. Surface ALL gaps as actionable items; bootstrap proceeds with what's available."

    return {
        "hats": hats,
        "composite": composite,
        "max_possible": 100,
        "auto_bridges": auto_bridges,
        "founder_actions": founder_actions,
        "verdict": verdict,
    }


def parse_bootstrap_prompt(eo_brain, warnings):
    """Read 5-CodeHandover/README.md or bootstrap-prompt.md if present."""
    p = (glob_first(eo_brain, "5-CodeHandover/README.md") or
         glob_first(eo_brain, "5-CodeHandover/references/bootstrap-prompt.md") or
         glob_first(eo_brain, "5-CodeHandover/bootstrap-prompt.md"))
    if not p:
        warnings.append("5-CodeHandover/README.md and bootstrap-prompt.md both missing — falling back to phase-by-phase identity extraction")
        return None
    txt = read_text(p) or ""
    return {"path": p, "length_bytes": len(txt)}


# ----------------------------------------------------------------------------
# BRD PARSER (the heart of resilient input)
# ----------------------------------------------------------------------------

def parse_brd(eo_brain, warnings):
    """Parse BRD into canonical structure. Hard-refuses on missing or empty BRD."""
    brd_path = os.path.join(eo_brain, "4-Architecture", "brd.md")
    if not os.path.exists(brd_path):
        refuse(
            reason="brd-missing",
            remediation=f"BRD not found at {brd_path}. Run /4-eo-tech-architect in Cowork to generate it.",
        )
    txt = read_text(brd_path)

    # Step 2 — extract AC tags
    ac_tags = sorted(set(re.findall(r"AC-(\d+)\.(\d+)", txt)))
    if not ac_tags:
        refuse(
            reason="brd-empty",
            remediation=f"BRD at {brd_path} has zero AC-N.N tags. Finish the BRD in Cowork (Phase 4) before bootstrapping.",
        )
    story_numbers = sorted(set(int(s) for s, _ in ac_tags))

    # Per-story AC count
    per_story_acs = {}
    for s, c in ac_tags:
        per_story_acs.setdefault(int(s), []).append(f"AC-{s}.{c}")

    # Step 3 — extract titles per story
    stories = []
    for n in story_numbers:
        title = None
        title_source = "inferred"
        for pat_template, source_label in STORY_HEADER_PATTERNS:
            pat = pat_template.format(N=n)
            m = re.search(pat, txt, re.MULTILINE)
            if m:
                title = m.group(1).strip()
                # Strip carve + loop tags from title (we'll re-extract them in Step 5/6)
                title = re.sub(r"\[@(WeekendMVP|Phase2)\]", "", title).strip()
                title = re.sub(r"\[loop:[a-z]+\]", "", title).strip()
                # Also strip a leading colon if the template left one
                title = title.lstrip(":").strip()
                title_source = source_label
                break
        if not title:
            title = f"Story {n}"
            warnings.append(f"Story {n} has no recognizable header — title defaulted to 'Story {n}'")

        ac_count = len(per_story_acs[n])
        if ac_count < 3:
            warnings.append(f"Story {n} has only {ac_count} AC(s) — canonical contract is ≥3. Founder should review.")

        # Step 5 — extract carve tag (search the line WITH the header + a few following lines)
        carve_tag = None
        carve_source = "missing"
        # Re-search the header line itself for tags
        for pat_template, _ in STORY_HEADER_PATTERNS:
            pat = pat_template.format(N=n).replace(r"(.+?)", r".+?")
            line_match = re.search(pat, txt, re.MULTILINE)
            if line_match:
                # Look at the entire matching line (including before .group(1))
                line_start = line_match.start()
                line_end = txt.find("\n", line_start)
                line = txt[line_start:line_end if line_end >= 0 else None]
                cm = re.search(r"\[@(WeekendMVP|Phase2)\]", line)
                if cm:
                    carve_tag = f"[@{cm.group(1)}]"
                    carve_source = "parsed"
                break

        # Step 6 — extract loop tags from the same header line
        loop_tags = []
        if carve_source == "parsed":
            line_match = re.search(STORY_HEADER_PATTERNS[0][0].format(N=n).replace(r"(.+?)", r".+?"),
                                    txt, re.MULTILINE)
            if not line_match:
                for pat_template, _ in STORY_HEADER_PATTERNS:
                    line_match = re.search(pat_template.format(N=n).replace(r"(.+?)", r".+?"),
                                            txt, re.MULTILINE)
                    if line_match:
                        break
            if line_match:
                line_start = line_match.start()
                line_end = txt.find("\n", line_start)
                line = txt[line_start:line_end if line_end >= 0 else None]
                loop_tags = [f"[loop:{m}]" for m in re.findall(r"\[loop:([a-z]+)\]", line)]

        # Step 8b — loop inference (only when missing)
        # Score each loop by (a) keyword hits in TITLE (weight 3) + (b) hits in ACs (weight 1).
        # Threshold: a loop needs total score ≥3 to be assigned.
        # This keeps inference tight: a story whose TITLE matches a loop almost always wins;
        # ACs alone need 3+ keyword hits before they trigger a loop tag.
        loop_source = "parsed" if loop_tags else "inferred"
        if not loop_tags:
            ac_pat = rf"AC-{n}\.\d+\s*\*?\*?\s*(.+?)\s*$"
            ac_lines = "\n".join(re.findall(ac_pat, txt, re.MULTILINE))
            title_lower = title.lower()
            ac_lower = ac_lines.lower()

            for loop_name, keywords in LOOP_KEYWORDS.items():
                # Use word boundaries to avoid substring false positives
                title_hits = sum(1 for kw in keywords
                                  if re.search(rf"\b{re.escape(kw.lower())}\b", title_lower))
                ac_hits = sum(1 for kw in keywords
                               if re.search(rf"\b{re.escape(kw.lower())}\b", ac_lower))
                # Score: title hits weighted 3x, AC hits 1x
                score = title_hits * 3 + ac_hits
                if score >= 3:
                    loop_tags.append(f"[loop:{loop_name}]")

        stories.append({
            "number": n,
            "title": title,
            "title_source": title_source,
            "ac_count": ac_count,
            "ac_tags": per_story_acs[n],
            "carve_tag": carve_tag,
            "carve_source": carve_source,
            "loop_tags": loop_tags,
            "loop_source": loop_source,
        })

    # Step 7 — detect SCOPE block
    has_scope_h2 = bool(re.search(r"^##\s+SCOPE", txt, re.M | re.I))
    has_canonical_weekend = bool(re.search(r"^###\s+Weekend MVP", txt, re.M))
    has_canonical_v2 = bool(re.search(r"^###\s+v2 Roadmap", txt, re.M))
    if has_canonical_weekend and has_canonical_v2:
        scope_shape = "canonical"
    elif has_scope_h2:
        scope_shape = "binary"
    else:
        scope_shape = "none"

    # Carve state across all stories
    has_any_carve = any(s["carve_source"] == "parsed" for s in stories)
    has_all_carve = all(s["carve_source"] == "parsed" for s in stories)
    if has_all_carve:
        carve_state = "canonical"
    elif has_any_carve:
        carve_state = "partial"
    else:
        carve_state = "untagged"

    # Loop state across all stories
    has_any_loop = any(s["loop_source"] == "parsed" for s in stories)
    has_all_loop = all(s["loop_source"] == "parsed" for s in stories)
    if has_all_loop:
        loop_state = "canonical"
    elif has_any_loop:
        loop_state = "partial"
    else:
        loop_state = "untagged"

    # Step 8a — carve inference
    proposed_carve = {"weekend_mvp": [], "phase_2": []}
    sc = len(stories)
    if carve_state == "canonical":
        proposed_carve["weekend_mvp"] = [s["number"] for s in stories if s["carve_tag"] == "[@WeekendMVP]"]
        proposed_carve["phase_2"] = [s["number"] for s in stories if s["carve_tag"] == "[@Phase2]"]
    elif sc <= 4:
        proposed_carve["weekend_mvp"] = [s["number"] for s in stories]
    elif sc <= 7:
        proposed_carve["weekend_mvp"] = [s["number"] for s in stories[:4]]
        proposed_carve["phase_2"] = [s["number"] for s in stories[4:]]
    else:
        proposed_carve["weekend_mvp"] = [s["number"] for s in stories[:4]]
        proposed_carve["phase_2"] = [s["number"] for s in stories[4:]]
        warnings.append(f"Story count ({sc}) > 7 — confirm Weekend MVP is really stories 1-4 in plan-mode preview")

    # Step 8c — loop coverage check (only over MVP stories per the proposed carve)
    mvp_loops = set()
    for s in stories:
        if s["number"] in proposed_carve["weekend_mvp"]:
            for t in s["loop_tags"]:
                m = re.match(r"\[loop:([a-z]+)\]", t)
                if m:
                    mvp_loops.add(m.group(1))
    required_loops = set(LOOP_KEYWORDS.keys())
    missing_loops = required_loops - mvp_loops
    loop_coverage = {
        "covered": sorted(mvp_loops),
        "missing": sorted(missing_loops),
        "complete": len(missing_loops) == 0,
    }
    if missing_loops:
        warnings.append(f"Weekend MVP slice missing loops: {sorted(missing_loops)} — founder must address in plan-mode preview")

    # Build normalization plan (what normalize() will do, surfaced to founder)
    normalization_plan = []
    if any(s["title_source"] not in ("h3-header",) for s in stories):
        # Some headers are not canonical h3
        non_h3 = [s["number"] for s in stories if s["title_source"] != "h3-header"]
        normalization_plan.append(f"Will rewrite story headers to canonical h3 (currently: {[stories[i-1]['title_source'] for i in non_h3]})")
    if carve_state != "canonical":
        normalization_plan.append(f"Will add carve tags ([@WeekendMVP] for stories {proposed_carve['weekend_mvp']}, [@Phase2] for stories {proposed_carve['phase_2']})")
    if loop_state != "canonical":
        loops_inferred = {s["number"]: s["loop_tags"] for s in stories if s["loop_source"] == "inferred"}
        normalization_plan.append(f"Will add loop tags inferred from content for {len(loops_inferred)} stories")
    if scope_shape != "canonical":
        normalization_plan.append(f"Will inject canonical SCOPE block (current shape: {scope_shape})")
    if not normalization_plan:
        normalization_plan.append("BRD already canonical — no normalization needed")

    return {
        "source_path": brd_path,
        "source_checksum_sha256": file_checksum(brd_path),
        "total_acs": sum(len(per_story_acs[n]) for n in story_numbers),
        "story_count": len(story_numbers),
        "stories": stories,
        "scope_shape": scope_shape,
        "carve_state": carve_state,
        "loop_state": loop_state,
        "proposed_carve": proposed_carve,
        "loop_coverage": loop_coverage,
        "normalization_plan": normalization_plan,
    }


# ----------------------------------------------------------------------------
# TOP-LEVEL INGESTER
# ----------------------------------------------------------------------------

def ingest(eo_brain):
    """Orchestrate all parsing. Returns BrainStructure dict or raises Refused.
    BrainStructure includes a `questions[]` array — every blocking gap the
    bootstrap MUST resolve with the founder before scaffold can proceed."""
    if not os.path.isdir(eo_brain):
        refuse(
            reason="eo-brain-missing",
            remediation=f"EO-Brain directory not found at {eo_brain}. Run EO-Brain phases 0-4 in Cowork first.",
        )

    warnings = []
    questions = []  # blocking gaps that need founder input before scaffold

    # ─── v1.4.6: SaaSfast yes/no question ALWAYS fires, ALWAYS first ─────
    # This regressed in v1.4.3 when Step 7 was rewritten to use parse.py;
    # the markdown Step 8a still describes it but it wasn't in the
    # questions[] array, so Claude's iteration over questions[] never
    # surfaced it to the founder. v1.4.6 makes this question the FIRST
    # blocking item every founder sees in plan-mode preview.
    questions.append({
        "key": "saasfast_used",
        "blocking": True,
        "prompt": (
            "🧰 Will this project use SaaSfast (the EO MicroSaaS starter kit)?\n"
            "  yes — clone SaaSfast-ar to your project repo, pull in the right "
            "subset (auth/payment/landing/dashboard) for your BRD. "
            "GitHub repo will be created at start.\n"
            "  no  — fully custom build, no SaaSfast pieces. "
            "GitHub stays optional (4-option question follows)."
        ),
        "default_suggestion": "yes",
        "default_source": "Weekend MVP default — most projects benefit from SaaSfast",
    })

    # Read BRD raw text once for use by language detector + identity ICP fallback
    brd_path = os.path.join(eo_brain, "4-Architecture", "brd.md")
    brd_text_raw = read_text(brd_path)

    language = parse_language(eo_brain, brd_text_raw, warnings)
    identity = parse_identity(eo_brain, warnings, questions)
    founder_country = parse_founder_country(eo_brain, warnings)
    identity["founder_country"] = founder_country
    stack = parse_stack(eo_brain, warnings, founder_country)
    bootstrap_prompt = parse_bootstrap_prompt(eo_brain, warnings)
    ux_artifacts = parse_ux_artifacts(eo_brain, warnings)
    brd = parse_brd(eo_brain, warnings)

    # Generate questions for BRD gaps that need founder approval
    if brd["carve_state"] != "canonical":
        questions.append({
            "key": "carve_approval",
            "blocking": True,
            "prompt": (
                f"BRD has {brd['story_count']} stories with no [@WeekendMVP]/[@Phase2] tags. "
                f"I propose: stories {brd['proposed_carve']['weekend_mvp']} = Weekend MVP, "
                f"stories {brd['proposed_carve']['phase_2']} = v2 (frozen). "
                f"Approve? (y / override / skip-mvp-rule)"
            ),
            "default_suggestion": "y",
            "default_source": "first 4 stories = MVP, rest = Phase2",
            "proposed_carve": brd["proposed_carve"],
        })

    if brd["loop_state"] != "canonical":
        loop_summary = {s["number"]: s["loop_tags"] for s in brd["stories"] if s["loop_source"] == "inferred"}
        questions.append({
            "key": "loop_approval",
            "blocking": True,
            "prompt": (
                f"Inferred loop tags for {len(loop_summary)} stories from content keywords. "
                f"Review proposed loops per story; approve all (y), or override specific stories."
            ),
            "default_suggestion": "y",
            "default_source": "keyword-based content inference",
            "proposed_loops": loop_summary,
        })

    if not brd["loop_coverage"]["complete"]:
        missing = brd["loop_coverage"]["missing"]
        # Find which Phase2 stories have the missing loops (for "move story up" suggestion)
        candidates_to_promote = []
        for s in brd["stories"]:
            if s["number"] in brd["proposed_carve"]["phase_2"]:
                story_loops = [re.match(r"\[loop:([a-z]+)\]", t).group(1) for t in s["loop_tags"]
                                if re.match(r"\[loop:([a-z]+)\]", t)]
                covers = [l for l in missing if l in story_loops]
                if covers:
                    candidates_to_promote.append({
                        "story_number": s["number"],
                        "title": s["title"],
                        "covers_loops": covers,
                    })
        questions.append({
            "key": "mvp_loop_gap",
            "blocking": True,
            "prompt": (
                f"Weekend MVP slice missing loops: {missing}. The 7-loop contract requires "
                f"all of auth/domain/money/notify/deploy/observability/compliance shipped end-to-end. "
                f"Options: (A) move a Phase2 story into MVP that covers the gap "
                f"(B) accept gap and ship a partial MVP "
                f"(C) return to Cowork to add a new MVP story."
            ),
            "default_suggestion": "A" if candidates_to_promote else "C",
            "default_source": (
                f"Phase2 stories that could fill the gap: {candidates_to_promote}"
                if candidates_to_promote else "no obvious candidate to promote"
            ),
            "missing_loops": missing,
            "promote_candidates": candidates_to_promote,
        })

    # Phase presence summary
    phases_present = {
        "phase_0_scorecards": bool(glob.glob(os.path.join(eo_brain, "0-Scorecards/*.md"))),
        "phase_1_project_brain": os.path.isdir(os.path.join(eo_brain, "1-ProjectBrain")),
        "phase_2_gtm": os.path.isdir(os.path.join(eo_brain, "2-GTM")),
        "phase_3_newskills": os.path.isdir(os.path.join(eo_brain, "3-Newskills")),
        "phase_4_architecture": os.path.isdir(os.path.join(eo_brain, "4-Architecture")),
        "phase_5_handover": os.path.isdir(os.path.join(eo_brain, "5-CodeHandover")),
    }

    result = {
        "schema_version": "1.1",
        "ingester_version": "1.1",
        "ingested_at": datetime.utcnow().isoformat() + "Z",
        "eo_brain_path": os.path.abspath(eo_brain),
        "language": language,
        "identity": identity,
        "stack": stack,
        "bootstrap_prompt": bootstrap_prompt,
        "ux_artifacts": ux_artifacts,
        "brd": brd,
        "phases_present": phases_present,
        "warnings": warnings,
        "questions": questions,
        "refused": False,
    }
    # v1.4.4: multi-hat input score + bridge plan
    result["score"] = score_inputs(result)
    return result


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="EO-Brain resilient input parser")
    p.add_argument("eo_brain_path", nargs="?", help="Path to EO-Brain directory")
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    p.add_argument("--strict", action="store_true", help="Exit non-zero on any warning (for CI)")
    p.add_argument("--self-test", action="store_true",
                    help="Run smoke tests against fixtures/ and exit")
    args = p.parse_args()

    if args.self_test:
        return self_test()

    if not args.eo_brain_path:
        p.print_help()
        sys.exit(1)

    try:
        result = ingest(args.eo_brain_path)
    except Refused as e:
        print(json.dumps({
            "refused": True,
            "reason": e.reason,
            "remediation": e.remediation,
            "warnings": [],
        }, ensure_ascii=False, indent=2 if args.pretty else None))
        sys.exit(2)

    if args.strict and result["warnings"]:
        sys.stderr.write(f"Strict mode: {len(result['warnings'])} warnings — failing\n")
        for w in result["warnings"]:
            sys.stderr.write(f"  - {w}\n")
        sys.exit(2)

    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    sys.exit(0)


def self_test():
    """Run parser against every fixture in fixtures/ and the user's EO-Brain."""
    here = os.path.dirname(os.path.abspath(__file__))
    fixtures_dir = os.path.join(here, "fixtures")
    results = []

    if os.path.isdir(fixtures_dir):
        for fname in sorted(os.listdir(fixtures_dir)):
            fpath = os.path.join(fixtures_dir, fname)
            if not os.path.isdir(fpath):
                continue
            try:
                r = ingest(fpath)
                # Genuinely-empty fixtures should refuse
                if "empty" in fname:
                    results.append((fname, "UNEXPECTED-PASS", f"refused was expected for fixture '{fname}'"))
                else:
                    results.append((fname, "PASS",
                                     f"{r['brd']['story_count']} stories, {r['brd']['total_acs']} ACs, "
                                     f"{len(r['warnings'])} warnings"))
            except Refused as e:
                if "empty" in fname or "missing" in fname:
                    results.append((fname, "PASS-REFUSE", f"refused as expected: {e.reason}"))
                else:
                    results.append((fname, "FAIL", f"refused unexpectedly: {e.reason}"))
            except Exception as e:
                results.append((fname, "ERROR", str(e)))

    # Print results table
    print(f"{'Fixture':<45} {'Status':<14} Detail")
    print("-" * 100)
    for name, status, detail in results:
        print(f"{name:<45} {status:<14} {detail}")
    fail = sum(1 for _, s, _ in results if s in ("FAIL", "ERROR", "UNEXPECTED-PASS"))
    print("-" * 100)
    print(f"Total: {len(results)} · Pass: {len(results) - fail} · Fail: {fail}")
    sys.exit(0 if fail == 0 else 2)


if __name__ == "__main__":
    main()
