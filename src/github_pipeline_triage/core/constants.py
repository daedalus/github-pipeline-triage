"""Heuristic constants for triage classification."""

from __future__ import annotations

import os
import re
from pathlib import Path

REPO = os.environ.get("GITHUB_REPO", "owner/repo")

REPO_ROOT = Path(__file__).parent.parent.parent.parent
CACHE_DIR = REPO_ROOT / ".cache"
DEFAULT_OUTPUT = REPO_ROOT / "ISSUES.md"
CACHE_TTL_MS = 6 * 60 * 60 * 1000  # 6h

MEMPALACE_MODULES = []

MODULE_BARE_NAMES = frozenset(
    m[:-3] for m in MEMPALACE_MODULES if m.endswith(".py")
)

COMMON_WORD_MODULES = frozenset(["version.py", "config.py"])

CRITICAL_KEYWORDS = [
    r"\bsegfault\b", r"\bEXC_BAD_ACCESS\b", r"\bOOM\b",
    r"\bdata loss\b", r"\bdata gone\b", r"\blost data\b",
    r"\bcorrupt\w*\b", r"\bunrecoverable\b", r"\bdestroy\w*\b",
    r"\bfills disk\b", r"\bterabytes?\b", r"\binfinite recursion\b",
    r"\bmalicious\b", r"\bexploit\b", r"\bshell injection\b",
    r"\bpath traversal\b", r"\bapi key exposure\b", r"\brce\b",
    r"\bsingle point of failure\b", r"\bSPOF\b",
    r"\bpalace data gone\b", r"\bbreaks existing\b",
    r"\brelease defect\b", r"\bbroken install\b",
    r"\bfresh install\b.*\bfail",
    r"\bentry point\b.*\bmissing\b",
    r"\bpip install\b.*\bfail",
    r"\bcommand not found\b", r"\bexecutable file not found\b",
    r"v\d+\.\d+\.\d+\b.*\brelease defect\b",
]

HIGH_KEYWORDS = [
    r"\bsilent(ly)? (fail|skip|drop|truncate|return|ingest)\w*\b",
    r"\bmemory exhaustion\b", r"\bdenial of service\b", r"\bDoS\b",
    r"\brace condition\b", r"\brace on\b",
    r"\bsurrogate error\b", r"\bencoding (crash|error|failure)\b",
    r"\bstale (cache|index|results)\b",
    r"\bre-process\w* every\b",
    r"\bplugin\.json\b", r"\bpyproject\.toml\b",
    r"\bconsole script\b", r"\bentry point\b",
    r"\bpipx\b", r"\buv compat\w*\b",
]

NOISE_TITLE_PATTERNS = [
    re.compile(r"^null$", re.IGNORECASE),
    re.compile(r"^TLDR$", re.IGNORECASE),
    re.compile(r"^new issue$", re.IGNORECASE),
    re.compile(r"^test$", re.IGNORECASE),
    re.compile(r"^asdf", re.IGNORECASE),
    re.compile(r"^hello,?( world)?[!?.]?$", re.IGNORECASE),
    re.compile(r"^(thank you|thanks|谢谢|merci|gracias|danke)[!.]?$", re.IGNORECASE),
    re.compile(r"^[^\w\d_]+$", re.UNICODE),
    re.compile(r"^\s*!!.*!!\s*$"),
    re.compile(r"\b(COMPROMISED|HACKED|HIJACKED|POSSESSED|STOLEN)\b"),
]

META_REPORT_TITLE_PATTERNS = [
    re.compile(r"\b\d+\s+(issues?|bugs?(\s*fixes?)?|vulnerabilit|problems?|defects?|reports?)\b", re.IGNORECASE),
    re.compile(r"^\s*(security audit|bug report|code review|audit|review)\s*[:\-—]", re.IGNORECASE),
    re.compile(r"\bunreported (vulnerabilit|bugs|issues)\b", re.IGNORECASE),
    re.compile(r"\b(Executive Summary|Findings|Scope)\b.*\b(vulnerabilit|issues|bugs)\b", re.IGNORECASE),
]

NOISE_BODY_PATTERNS = [
    re.compile(r"^(thank you|thanks|appreciate)", re.IGNORECASE),
    re.compile(r"^(hi|hello)[,!. ]", re.IGNORECASE),
]

SUBSTANTIVE_TITLE_MARKERS = re.compile(
    r"\b(bug|error|crash|fail|broken|segfault|hang|corrupt|data loss|"
    r"regression|cannot|can't|doesn't|does not|unable|timeout|exception|"
    r"v\d+\.\d+|Python \d|Windows|Linux|macOS|[a-z_]+\.py|"
    r"[A-Z]{2,}[a-z]*Error)",
    re.IGNORECASE,
)

FEATURE_TITLE_PREFIX = re.compile(
    r"^\s*(\[?RFC\]?|feat[:(]|feature request|feature proposal|"
    r"\[\feature\]|\[integration idea\]|\[spec\]|\[question\]|"
    r"feature:|proposal:|idea:|discussion:|showcase:|example:|"
    r"clarification:|community feedback)",
    re.IGNORECASE,
)

DEWEIGHT_PHRASES = [
    "prevent data loss", "to prevent", "avoid data loss", "avoid corruption",
    "harm structurally impossible", "no data loss", "backup before",
    "data-loss-prevention", "prevent crash", "avoid crash",
]

BUG_TITLE_PREFIX = re.compile(
    r"^\s*(\[?bug\]?[:\s]|fix[:(]|crash|broken|regression|"
    r"fails?[:\s]|error[:\s]|doesn't work|does not work|"
    r"【bug】)",
    re.IGNORECASE,
)


class SensitivePathRule:
    def __init__(self, pattern: str, reason: str, level: str):
        self.pattern = re.compile(pattern)
        self.reason = reason
        self.level = level


SENSITIVE_PATHS = [
    SensitivePathRule(r"^\.github/workflows/", "modifies CI workflow", "high"),
    SensitivePathRule(r"^\.github/actions/", "modifies CI action", "high"),
    SensitivePathRule(r"^hooks/.*\.(sh|py|bash|zsh|fish|ps1)$", "changes hook scripts (user-facing exec)", "high"),
    SensitivePathRule(r"^\.pre-commit-config\.yaml$", "modifies pre-commit hooks", "high"),
    SensitivePathRule(r"^conftest\.py$", "import-time test hook", "high"),
    SensitivePathRule(r"^pyproject\.toml$", "changes dependencies / build config", "medium"),
    SensitivePathRule(r"^setup\.py$", "changes install script", "medium"),
    SensitivePathRule(r"^setup\.cfg$", "changes install config", "medium"),
    SensitivePathRule(r"^uv\.lock$", "changes locked deps", "medium"),
    SensitivePathRule(r"^LICENSE$", "modifies LICENSE", "medium"),
    SensitivePathRule(r"^\.git(ignore|attributes)$", "modifies git config", "medium"),
]


class DiffRedFlag:
    def __init__(
        self,
        pattern: str,
        reason: str,
        level: str = "critical",
        exclude_if: str | None = None,
    ):
        self.pattern = re.compile(pattern)
        self.reason = reason
        self.level = level
        self.exclude_if = re.compile(exclude_if) if exclude_if else None


DIFF_RED_FLAGS = [
    DiffRedFlag(r"(?<![.\w])eval\s*\(", "eval() call"),
    DiffRedFlag(r"(?<![.\w])exec\s*\(", "exec() call"),
    DiffRedFlag(r"\b__import__\s*\(", "dynamic __import__"),
    DiffRedFlag(r"(?<![.\w])compile\s*\(['\"]", "builtin compile() on a string literal"),
    DiffRedFlag(r"subprocess\.[A-Za-z_]+\([^)]*shell\s*=\s*True", "subprocess shell=True"),
    DiffRedFlag(r"\bos\.system\s*\(", "os.system() call"),
    DiffRedFlag(r"\bos\.popen\s*\(", "os.popen() call"),
    DiffRedFlag(r"curl\s+[^|]*\|\s*(bash|sh|zsh)", "curl pipe to shell"),
    DiffRedFlag(r"wget\s+[^|]*\|\s*(bash|sh|zsh)", "wget pipe to shell"),
    DiffRedFlag(r"[A-Za-z0-9+/]{160,}={0,2}", "long base64-like string"),
    DiffRedFlag(
        r"https?://(?!github\.com|raw\.githubusercontent\.com|pypi\.org|"
        r"files\.pythonhosted\.org|docs\.python\.org|python\.org|"
        r"anthropic\.com|openai\.com|chatgpt\.com|claude\.com|claude\.ai|"
        r"cursor\.com|cursor\.sh|openrouter\.ai|huggingface\.co|"
        r"chromadb|trychroma\.com|"
        r"www\.mempalace|mempalace\.tech|mempalace\.ai|"
        r"readthedocs\.io|sentry\.io|schema\.org|w3\.org|en\.wikipedia\.org|"
        r"microsoft\.com|apple\.com|jetbrains\.com|mozilla\.org|"
        r"ollama\.com|ollama\.ai|lancedb\.com|qdrant\.tech|tidbcloud\.com|"
        r"example\.com|localhost|127\.0\.0\.1)"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        "URL to unfamiliar domain",
    ),
    DiffRedFlag(r"\bnc\s+-e\b|\bnetcat\b.*\b-e\b", "netcat -e (reverse shell marker)"),
]
