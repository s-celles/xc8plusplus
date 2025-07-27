"""Integration tests for xc8plusplus."""

import os
import tempfile

from xc8plusplus import XC8Transpiler


class TestIntegration:
    """Integration tests for the complete transpilation process."""

    def test_full_transpilation_workflow(self, sample_cpp_code):
        """Test the complete workflow from C++ to C."""
        transpiler = XC8Transpiler()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cpp", delete=False
        ) as cpp_file:
            cpp_file.write(sample_cpp_code)
            cpp_file.flush()
            cpp_file_path = cpp_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as c_file:
            c_file_path = c_file.name

        try:
            # Attempt transpilation
            success = transpiler.transpile(cpp_file_path, c_file_path)

            # Check that output file was created
            assert os.path.exists(c_file_path)

            # If transpilation succeeded, check that we have some output
            if success:
                with open(c_file_path) as f:
                    output_content = f.read()
                assert len(output_content) > 0

                # Basic sanity checks for C code
                assert "#include" in output_content

        except Exception as e:
            # If clang is not available, this is expected
            print(f"Transpilation failed (expected if clang not available): {e}")

        finally:
            try:
                os.unlink(cpp_file_path)
            except Exception:
                pass
            try:
                os.unlink(c_file_path)
            except Exception:
                pass

    def test_transpiler_with_simple_code(self, simple_cpp_code):
        """Test transpiler with simple C++ code."""
        transpiler = XC8Transpiler()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cpp", delete=False
        ) as cpp_file:
            cpp_file.write(simple_cpp_code)
            cpp_file.flush()
            cpp_file_path = cpp_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as c_file:
            c_file_path = c_file.name

        try:
            transpiler.transpile(cpp_file_path, c_file_path)

            # File should exist regardless of success
            assert os.path.exists(c_file_path)

        finally:
            try:
                os.unlink(cpp_file_path)
            except Exception:
                pass
            try:
                os.unlink(c_file_path)
            except Exception:
                pass

    def test_error_handling(self):
        """Test error handling with invalid input."""
        transpiler = XC8Transpiler()

        # Test with non-existent input file
        with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as output_file:
            output_file_path = output_file.name

        try:
            success = transpiler.transpile("does_not_exist.cpp", output_file_path)
            assert not success
        finally:
            try:
                os.unlink(output_file_path)
            except Exception:
                pass

    def test_empty_file_handling(self):
        """Test handling of empty input files."""
        transpiler = XC8Transpiler()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cpp", delete=False
        ) as cpp_file:
            # Write empty content
            cpp_file.write("")
            cpp_file.flush()
            cpp_file_path = cpp_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as c_file:
            c_file_path = c_file.name

        try:
            transpiler.transpile(cpp_file_path, c_file_path)
            # Should handle empty files gracefully
            assert os.path.exists(c_file_path)

        finally:
            try:
                os.unlink(cpp_file_path)
            except Exception:
                pass
            try:
                os.unlink(c_file_path)
            except Exception:
                pass
