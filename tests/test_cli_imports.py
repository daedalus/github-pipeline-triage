"""Tests for CLI commands module - import tests only."""

from __future__ import annotations


class TestCliImports:
    """Test CLI module can be imported."""

    def test_import_commands(self) -> None:
        """Test commands module imports."""
        from github_pipeline_triage.cli import commands

        assert commands is not None

    def test_import_main(self) -> None:
        """Test main function exists."""
        from github_pipeline_triage.cli import main

        assert callable(main)

    def test_cmd_sync_exists(self) -> None:
        """Test cmd_sync exists."""
        from github_pipeline_triage.cli.commands import cmd_sync

        assert callable(cmd_sync)

    def test_cmd_audit_prs_exists(self) -> None:
        """Test cmd_audit_prs exists."""
        from github_pipeline_triage.cli.commands import cmd_audit_prs

        assert callable(cmd_audit_prs)

    def test_cmd_noise_report_exists(self) -> None:
        """Test cmd_noise_report exists."""
        from github_pipeline_triage.cli.commands import cmd_noise_report

        assert callable(cmd_noise_report)

    def test_cmd_serve_exists(self) -> None:
        """Test cmd_serve exists."""
        from github_pipeline_triage.cli.commands import cmd_serve

        assert callable(cmd_serve)

    def test_constants_import(self) -> None:
        """Test constants can be imported."""
        from github_pipeline_triage.core.constants import DEFAULT_OUTPUT

        assert DEFAULT_OUTPUT is not None
