"""github-pipeline-triage - Automated GitHub issue and PR triage system."""

__version__ = "0.1.0"
__all__ = ["__version__", "core", "adapters", "services", "cli", "api", "db"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core.classify import classify_severity, detect_noise
    from .core.duplicates import find_duplicates, similarity_ratio
    from .core.pr_suspicion import analyze_pr_suspicion, cross_reference_modules
    from .core.types import PR, DuplicatePair, Issue, Severity, SuspicionLevel
