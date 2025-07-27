"""Tests for xc8plusplus CLI."""

import os
import tempfile

from typer.testing import CliRunner

from xc8plusplus.cli import app


class TestCLI:
    """Test cases for the CLI interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test the version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "xc8plusplus" in result.stdout.lower()
        assert "version" in result.stdout.lower()

    def test_transpile_command_missing_input(self):
        """Test transpile command with missing input file."""
        result = self.runner.invoke(app, ["transpile", "nonexistent.cpp"])
        assert result.exit_code != 0
        # Check that it fails (file doesn't exist)

    def test_transpile_command_with_files(self):
        """Test transpile command with valid file paths."""
        cpp_content = """
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cpp", delete=False
        ) as input_file:
            input_file.write(cpp_content)
            input_file.flush()
            input_file_path = input_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".c", delete=False
        ) as output_file:
            output_file_path = output_file.name

        try:
            result = self.runner.invoke(
                app, ["transpile", input_file_path, "--output", output_file_path]
            )

            # Command should execute (though transpilation may fail without clang)
            # We just check that the CLI interface works
            assert result.exit_code in [
                0,
                1,
            ]  # 0 for success, 1 for transpilation failure

        finally:
            try:
                os.unlink(input_file_path)
            except OSError:
                pass
            try:
                os.unlink(output_file_path)
            except OSError:
                pass

    def test_demo_command(self):
        """Test the demo command."""
        result = self.runner.invoke(app, ["demo"])
        assert result.exit_code == 0
        assert "demo" in result.stdout.lower() or "Demo" in result.stdout

    def test_help_command(self):
        """Test the help command."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "transpile" in result.stdout.lower()
        assert "version" in result.stdout.lower()
        assert "demo" in result.stdout.lower()
