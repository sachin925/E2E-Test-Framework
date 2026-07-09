"""
Framework structure validator and linter.
Validates Robot Framework files, Python files, and project structure.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class FrameworkLinter:
    """Validates E2E test framework structure and code quality."""

    # Required directories
    REQUIRED_DIRS = [
        "tests",
        "tests/ui",
        "tests/api",
        "resources",
        "resources/keywords",
        "resources/variables",
        "libraries",
        "config",
    ]

    # Required files
    REQUIRED_FILES = [
        "requirements.txt",
        "README.md",
        ".gitignore",
        "tasks.py",
    ]

    # Robot Framework file patterns
    ROBOT_SETTINGS = [
        "*** Settings ***",
        "*** settings ***",
    ]
    ROBOT_TEST_CASES = [
        "*** Test Cases ***",
        "*** test cases ***",
    ]
    ROBOT_KEYWORDS = [
        "*** Keywords ***",
        "*** keywords ***",
    ]
    ROBOT_VARIABLES = [
        "*** Variables ***",
        "*** variables ***",
    ]

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Running framework validation...\n")

        # Run all checks
        self.check_directory_structure()
        self.check_required_files()
        self.check_robot_files()
        self.check_python_files()
        self.check_config_files()

        # Print summary
        self._print_summary()

        return len(self.errors) == 0

    def check_directory_structure(self) -> None:
        """Validate required directories exist."""
        print("  Checking directory structure...")

        for dir_path in self.REQUIRED_DIRS:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                self.errors.append({
                    "type": "missing_directory",
                    "message": f"Missing required directory: {dir_path}",
                    "path": str(full_path),
                })

    def check_required_files(self) -> None:
        """Validate required files exist."""
        print("  Checking required files...")

        for file_path in self.REQUIRED_FILES:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.errors.append({
                    "type": "missing_file",
                    "message": f"Missing required file: {file_path}",
                    "path": str(full_path),
                })

    def check_robot_files(self) -> None:
        """Validate all Robot Framework files."""
        print("  Checking Robot Framework files...")

        robot_files = list(self.project_root.rglob("*.robot"))

        for file_path in robot_files:
            # Skip results/reports directories
            if any(part in ["results", "reports", "venv"] for part in file_path.parts):
                continue

            self._validate_robot_file(file_path)

    def check_python_files(self) -> None:
        """Validate all Python files."""
        print("  Checking Python files...")

        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # Skip venv and cache
            if any(part in ["venv", "__pycache__", "results", "reports"] for part in file_path.parts):
                continue

            self._validate_python_file(file_path)

    def check_config_files(self) -> None:
        """Validate configuration files."""
        print("  Checking configuration files...")

        config_dir = self.project_root / "config"
        if not config_dir.exists():
            return

        for config_file in config_dir.glob("*.yaml"):
            self._validate_yaml_file(config_file)

    def _validate_robot_file(self, file_path: Path) -> None:
        """Validate a single Robot Framework file."""
        try:
            content = file_path.read_text()
            lines = content.split("\n")

            # Check for required sections based on file location
            is_test_file = "tests" in file_path.parts
            is_keyword_file = "keywords" in file_path.parts
            is_variable_file = "variables" in file_path.parts

            # All Robot files should have Settings section
            has_settings = any(section in content for section in self.ROBOT_SETTINGS)

            if not has_settings:
                self.errors.append({
                    "type": "robot_missing_settings",
                    "message": f"Missing *** Settings *** section",
                    "path": str(file_path),
                    "line": 1,
                })

            # Test files should have Test Cases section
            if is_test_file:
                has_test_cases = any(section in content for section in self.ROBOT_TEST_CASES)
                if not has_test_cases:
                    self.errors.append({
                        "type": "robot_missing_test_cases",
                        "message": f"Test file missing *** Test Cases *** section",
                        "path": str(file_path),
                        "line": 1,
                    })

                # Check test cases have Documentation
                self._check_robot_documentation(file_path, lines, "test")

            # Keyword files should have Keywords section
            if is_keyword_file:
                has_keywords = any(section in content for section in self.ROBOT_KEYWORDS)
                if not has_keywords:
                    self.errors.append({
                        "type": "robot_missing_keywords",
                        "message": f"Keyword file missing *** Keywords *** section",
                        "path": str(file_path),
                        "line": 1,
                    })

            # Variable files should have Variables section
            if is_variable_file:
                has_variables = any(section in content for section in self.ROBOT_VARIABLES)
                if not has_variables:
                    self.errors.append({
                        "type": "robot_missing_variables",
                        "message": f"Variable file missing *** Variables *** section",
                        "path": str(file_path),
                        "line": 1,
                    })

            # Check for common issues
            self._check_robot_common_issues(file_path, lines)

        except Exception as e:
            self.errors.append({
                "type": "robot_read_error",
                "message": f"Failed to read file: {e}",
                "path": str(file_path),
            })

    def _check_robot_documentation(self, file_path: Path, lines: List[str], file_type: str) -> None:
        """Check for documentation in Robot files."""
        has_suite_doc = False
        in_settings = False

        for i, line in enumerate(lines, 1):
            if "*** Settings ***" in line:
                in_settings = True
                continue

            if in_settings and line.strip().startswith("***"):
                break

            if in_settings and "Documentation" in line:
                has_suite_doc = True
                break

        if not has_suite_doc and file_type == "test":
            self.warnings.append({
                "type": "robot_missing_suite_doc",
                "message": f"Test file missing Documentation in Settings",
                "path": str(file_path),
                "line": 1,
            })

    def _check_robot_common_issues(self, file_path: Path, lines: List[str]) -> None:
        """Check for common Robot Framework issues."""
        in_test_case = False
        test_case_name = None
        test_case_line = 0

        for i, line in enumerate(lines, 1):
            # Track test case sections
            if "*** Test Cases ***" in line:
                in_test_case = True
                continue

            if in_test_case and line.strip().startswith("***"):
                in_test_case = False
                test_case_name = None
                continue

            # Check for test case without tags
            if in_test_case and line and not line.startswith(" "):
                # This is a test case name
                test_case_name = line.strip()
                test_case_line = i
                has_tags = False

                # Look ahead for tags
                for j in range(i, min(i + 10, len(lines))):
                    if "[Tags]" in lines[j]:
                        has_tags = True
                        break
                    if lines[j] and not lines[j].startswith(" ") and j > i:
                        break

                if not has_tags and test_case_name:
                    self.warnings.append({
                        "type": "robot_missing_tags",
                        "message": f"Test case '{test_case_name}' has no tags",
                        "path": str(file_path),
                        "line": test_case_line,
                    })

            # Check for hardcoded values (simple heuristic)
            if "password" in line.lower() and "=" in line and not line.strip().startswith("#"):
                # Check if it's a variable assignment with a value
                if re.search(r'\$\{.*password.*\}\s*=\s*[^\s$]', line, re.IGNORECASE):
                    self.warnings.append({
                        "type": "robot_hardcoded_password",
                        "message": f"Possible hardcoded password",
                        "path": str(file_path),
                        "line": i,
                    })

    def _validate_python_file(self, file_path: Path) -> None:
        """Validate a single Python file."""
        try:
            content = file_path.read_text()

            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                self.errors.append({
                    "type": "python_syntax_error",
                    "message": f"Syntax error: {e.msg}",
                    "path": str(file_path),
                    "line": e.lineno or 1,
                })
                return

            # Check for module docstring
            if not ast.get_docstring(tree):
                # Only warn for library files, not tasks.py
                if "libraries" in file_path.parts:
                    self.warnings.append({
                        "type": "python_missing_docstring",
                        "message": f"Module missing docstring",
                        "path": str(file_path),
                        "line": 1,
                    })

            # Check function/class docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not ast.get_docstring(node) and not node.name.startswith("_"):
                        self.warnings.append({
                            "type": "python_missing_function_docstring",
                            "message": f"Function '{node.name}' missing docstring",
                            "path": str(file_path),
                            "line": node.lineno,
                        })

                elif isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        self.warnings.append({
                            "type": "python_missing_class_docstring",
                            "message": f"Class '{node.name}' missing docstring",
                            "path": str(file_path),
                            "line": node.lineno,
                        })

            # Check for TODO/FIXME comments
            for i, line in enumerate(content.split("\n"), 1):
                if "TODO" in line or "FIXME" in line:
                    self.warnings.append({
                        "type": "python_todo_comment",
                        "message": f"TODO/FIXME comment found",
                        "path": str(file_path),
                        "line": i,
                    })

            # Check for bare except
            if "except:" in content:
                self.warnings.append({
                    "type": "python_bare_except",
                    "message": f"Bare 'except:' clause found",
                    "path": str(file_path),
                    "line": 1,
                })

        except Exception as e:
            self.errors.append({
                "type": "python_read_error",
                "message": f"Failed to read file: {e}",
                "path": str(file_path),
            })

    def _validate_yaml_file(self, file_path: Path) -> None:
        """Validate a YAML configuration file."""
        try:
            import yaml

            content = file_path.read_text()

            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self.errors.append({
                    "type": "yaml_parse_error",
                    "message": f"YAML parse error: {e}",
                    "path": str(file_path),
                    "line": 1,
                })
                return

            # Check for required top-level keys
            if not isinstance(data, dict):
                self.errors.append({
                    "type": "yaml_invalid_structure",
                    "message": f"Config should be a dictionary",
                    "path": str(file_path),
                })
                return

            required_keys = ["environment", "ui", "api"]
            for key in required_keys:
                if key not in data:
                    self.errors.append({
                        "type": "yaml_missing_key",
                        "message": f"Missing required key: {key}",
                        "path": str(file_path),
                    })

        except ImportError:
            self.warnings.append({
                "type": "yaml_module_missing",
                "message": f"PyYAML not installed, skipping YAML validation",
                "path": str(file_path),
            })
        except Exception as e:
            self.errors.append({
                "type": "yaml_read_error",
                "message": f"Failed to read file: {e}",
                "path": str(file_path),
            })

    def _print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)

        if self.errors:
            print(f"\n❌ Found {len(self.errors)} error(s):\n")
            for error in self.errors:
                print(f"  [{error['type']}] {error['path']}")
                print(f"    {error['message']}")
                if 'line' in error:
                    print(f"    Line: {error['line']}")
                print()

        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} warning(s):\n")
            for warning in self.warnings:
                print(f"  [{warning['type']}] {warning['path']}")
                print(f"    {warning['message']}")
                if 'line' in warning:
                    print(f"    Line: {warning['line']}")
                print()

        if not self.errors and not self.warnings:
            print("\n✅ All checks passed!\n")
        elif not self.errors:
            print(f"\n✅ No errors found (but {len(self.warnings)} warnings)\n")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s)\n")


def main():
    """Main entry point for linter."""
    project_root = Path.cwd()

    # Allow specifying project root via argument
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])

    linter = FrameworkLinter(project_root)
    success = linter.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
