"""
Invoke tasks for E2E Test Automation Framework.
Run tests, manage environments, and generate reports.

Usage:
    invoke --list                    # Show all available tasks
    invoke test                      # Run all tests
    invoke test --suite ui           # Run specific test suite
    invoke test --tags smoke         # Run tests by tags
    invoke api-test                  # Run API tests
    invoke ui-test                   # Run UI tests
    invoke report                    # Generate Allure report
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from invoke import task, Context

# Project paths
PROJECT_ROOT = Path(__file__).parent
TESTS_DIR = PROJECT_ROOT / "tests"
RESULTS_DIR = PROJECT_ROOT / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"
CONFIG_DIR = PROJECT_ROOT / "config"
ALLURE_RESULTS = RESULTS_DIR / "allure"

# Default values
DEFAULT_BROWSER = "chrome"
DEFAULT_ENV = "dev"
DEFAULT_PROCESSES = 4


def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def run_robot(
    ctx: Context,
    test_path: str,
    output_dir: Path,
    include_tags: Optional[str] = None,
    exclude_tags: Optional[str] = None,
    variables: Optional[dict] = None,
    parallel: bool = False,
    processes: int = DEFAULT_PROCESSES,
) -> int:
    """Run Robot Framework tests with common options.

    Args:
        ctx: Invoke context
        test_path: Path to test files
        output_dir: Output directory for results
        include_tags: Tags to include
        exclude_tags: Tags to exclude
        variables: Additional variables
        parallel: Run with pabot for parallel execution
        processes: Number of parallel processes

    Returns:
        Exit code from robot/pabot
    """
    ensure_dir(output_dir)
    ensure_dir(ALLURE_RESULTS)

    # Build command
    if parallel:
        cmd = f"pabot --processes {processes}"
    else:
        cmd = "robot"

    # Common options
    cmd += f" --outputdir {output_dir}"
    cmd += f" --listener allure_robotframework:{ALLURE_RESULTS}"
    cmd += " --logtitle 'Test Log'"
    cmd += " --reporttitle 'Test Report'"
    cmd += " --output output.xml"

    # Tags
    if include_tags:
        cmd += f" --include {include_tags}"
    if exclude_tags:
        cmd += f" --exclude {exclude_tags}"

    # Variables
    if variables:
        for key, value in variables.items():
            cmd += f" --variable {key}:{value}"

    # Test path
    cmd += f" {test_path}"

    # Run command
    result = ctx.run(cmd, warn=True)
    return result.exited


@task
def setup(ctx, upgrade=False):
    """Set up the test environment.

    Creates virtual environment and installs dependencies.

    Args:
        upgrade: Upgrade existing dependencies
    """
    venv_path = PROJECT_ROOT / "venv"

    print("🔧 Setting up test environment...")

    # Create venv if not exists
    if not venv_path.exists():
        print("  Creating virtual environment...")
        ctx.run(f"python3 -m venv {venv_path}")

    # Install dependencies
    pip_cmd = f"{venv_path}/bin/pip"
    if upgrade:
        ctx.run(f"{pip_cmd} install --upgrade pip")
    else:
        ctx.run(f"{pip_cmd} install pip")

    # Install requirements
    print("  Installing dependencies...")
    ctx.run(f"{pip_cmd} install -r CI/requirements.txt")

    # Create directories
    print("  Creating directories...")
    ensure_dir(RESULTS_DIR)
    ensure_dir(REPORTS_DIR)

    print("✅ Setup complete!")
    print(f"\nTo activate virtual environment:\n  source {venv_path}/bin/activate")


@task
def lint(ctx, fix=False, strict=False):
    """Run comprehensive code quality checks.

    Args:
        fix: Automatically fix issues where possible
        strict: Treat warnings as errors
    """
    print("🔍 Running comprehensive linters...\n")

    errors_found = False

    # 1. Framework structure validation
    print("1️⃣  Checking framework structure...")
    result = ctx.run("python libraries/linter.py", warn=True)
    if result.exited != 0:
        errors_found = True

    # 2. Robocop for Robot files
    print("\n2️⃣  Checking Robot files with robocop...")
    result = ctx.run("robocop tests/ resources/ --config .robocop", warn=True)
    if result.exited != 0:
        errors_found = True
        print("  ⚠️  Robot files have issues")
    else:
        print("  ✅ Robot files passed")

    # 3. Robotidy for formatting
    if fix:
        print("\n3️⃣  Formatting Robot files...")
        result = ctx.run("robotidy tests/ resources/ --check", warn=True)
        if result.exited != 0:
            print("  Formatting Robot files...")
            ctx.run("robotidy tests/ resources/", warn=True)
            print("  ✅ Robot files formatted")
        else:
            print("  ✅ Robot files already formatted")

    # 4. Ruff for Python files
    print("\n4️⃣  Checking Python files with ruff...")
    if fix:
        ctx.run("ruff format libraries/ tasks.py --check", warn=True)
        ctx.run("ruff format libraries/ tasks.py", warn=True)
        ctx.run("ruff check libraries/ tasks.py --fix", warn=True)
    else:
        result = ctx.run("ruff check libraries/ tasks.py", warn=True)
        if result.exited != 0:
            errors_found = True

    # 5. Check for common issues
    print("\n5️⃣  Checking for common issues...")
    _check_common_issues(ctx)

    # 6. Validate test tags
    print("\n6️⃣  Validating test tags...")
    _validate_test_tags(ctx)

    # Summary
    print("\n" + "=" * 50)
    if errors_found:
        if strict:
            print("❌ Linting failed with errors")
            sys.exit(1)
        else:
            print("⚠️  Linting completed with issues")
    else:
        print("✅ All linting checks passed!")


def _check_common_issues(ctx: Context) -> None:
    """Check for common issues in the codebase."""
    issues = []

    # Check for TODO/FIXME comments
    result = ctx.run("grep -r 'TODO\\|FIXME' tests/ resources/ libraries/ --include='*.robot' --include='*.py' 2>/dev/null || true", warn=True, hide=True)
    if result.stdout.strip():
        lines = result.stdout.strip().split('\n')
        if len(lines) > 0:
            print(f"  ⚠️  Found {len(lines)} TODO/FIXME comment(s)")
            issues.append("todo_comments")

    # Check for hardcoded credentials
    result = ctx.run("grep -ri 'password\\|secret\\|api_key' resources/variables/ --include='*.robot' 2>/dev/null | grep -v '\\${.*}' | grep '=' || true", warn=True, hide=True)
    if result.stdout.strip():
        lines = result.stdout.strip().split('\n')
        if len(lines) > 0:
            print(f"  ⚠️  Possible hardcoded credentials found")
            issues.append("hardcoded_credentials")

    # Check for empty test files
    for robot_file in Path("tests").rglob("*.robot"):
        content = robot_file.read_text()
        if "*** Test Cases ***" in content:
            # Check if there are actual test cases (not just the section header)
            test_section = content.split("*** Test Cases ***")[-1].split("***")[0]
            if not test_section.strip() or test_section.strip().count('\n') < 2:
                print(f"  ⚠️  Empty test file: {robot_file}")
                issues.append("empty_test_file")

    if not issues:
        print("  ✅ No common issues found")


def _validate_test_tags(ctx: Context) -> None:
    """Validate that all test cases have appropriate tags."""
    from collections import defaultdict

    tag_stats = defaultdict(int)
    test_count = 0
    missing_tags = []

    for robot_file in Path("tests").rglob("*.robot"):
        content = robot_file.read_text()
        lines = content.split('\n')

        in_test_section = False
        current_test = None
        has_tags = False

        for line in lines:
            if "*** Test Cases ***" in line:
                in_test_section = True
                continue

            if in_test_section and line.strip().startswith("***"):
                in_test_section = False
                continue

            if in_test_section:
                # New test case
                if line and not line.startswith(' ') and not line.startswith('\t'):
                    # Save previous test
                    if current_test and not has_tags:
                        missing_tags.append((str(robot_file), current_test))

                    current_test = line.strip()
                    test_count += 1
                    has_tags = False

                # Check for tags
                if '[Tags]' in line:
                    has_tags = True
                    # Extract tags
                    tags = line.split('[Tags]')[-1].strip().split()
                    for tag in tags:
                        tag_stats[tag] += 1

    print(f"  Found {test_count} test cases")

    # Print tag statistics
    if tag_stats:
        print(f"  Tags used:")
        for tag, count in sorted(tag_stats.items(), key=lambda x: -x[1]):
            print(f"    - {tag}: {count} tests")

    # Report missing tags
    if missing_tags:
        print(f"  ⚠️  {len(missing_tags)} test(s) without tags:")
        for file_path, test_name in missing_tags[:5]:  # Show first 5
            print(f"    - {file_path}: {test_name}")
        if len(missing_tags) > 5:
            print(f"    ... and {len(missing_tags) - 5} more")
    else:
        print("  ✅ All test cases have tags")


@task
def validate(ctx):
    """Validate framework structure without running tests."""
    print("🔍 Validating framework structure...\n")

    # Run framework linter
    result = ctx.run("python libraries/linter.py", warn=True)

    if result.exited == 0:
        print("\n✅ Framework structure is valid")
    else:
        print("\n❌ Framework validation failed")
        sys.exit(1)


@task
def check_deps(ctx):
    """Check and report on project dependencies."""
    print("📦 Checking dependencies...\n")

    # Check Python dependencies
    print("Python packages:")
    result = ctx.run("pip list --format=freeze 2>/dev/null | grep -E 'robot|selenium|requests|invoke|ruff|robocop' || echo '  Run \"invoke setup\" first'", warn=True, hide=True)
    if result.stdout.strip():
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('Run'):
                pkg = line.split('==')[0] if '==' in line else line
                version = line.split('==')[1] if '==' in line else 'unknown'
                print(f"  ✅ {pkg}: {version}")

    # Check for outdated packages
    print("\nChecking for outdated packages...")
    ctx.run("pip list --outdated 2>/dev/null | head -10 || echo '  Unable to check'", warn=True)


@task
def test(
    ctx,
    suite=None,
    tags=None,
    exclude="skip",
    browser=DEFAULT_BROWSER,
    env=DEFAULT_ENV,
    headless=True,
    parallel=False,
    processes=DEFAULT_PROCESSES,
):
    """Run all tests.

    Args:
        suite: Test suite to run (ui, api, or specific path)
        tags: Tags to include (comma-separated)
        exclude: Tags to exclude (default: skip)
        browser: Browser for UI tests (chrome, firefox, edge, safari)
        env: Environment (dev, staging, prod)
        headless: Run browser in headless mode
        parallel: Run tests in parallel with pabot
        processes: Number of parallel processes
    """
    # Determine test path
    if suite:
        suite_lower = suite.lower()
        if suite_lower == "ui":
            test_path = TESTS_DIR / "ui"
        elif suite_lower == "api":
            test_path = TESTS_DIR / "api"
        else:
            test_path = Path(suite)
            if not test_path.exists():
                print(f"❌ Test path not found: {test_path}")
                sys.exit(1)
    else:
        test_path = TESTS_DIR

    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = RESULTS_DIR / f"run_{timestamp}"

    print(f"🚀 Running tests...")
    print(f"  Suite: {test_path}")
    print(f"  Environment: {env}")
    print(f"  Browser: {browser} (headless: {headless})")
    print(f"  Parallel: {parallel}")
    print(f"  Output: {output_dir}")
    print()

    # Variables
    variables = {
        "BROWSER": browser,
        "HEADLESS": str(headless).lower(),
        "ENVIRONMENT": env,
    }

    # Run tests
    exit_code = run_robot(
        ctx=ctx,
        test_path=str(test_path),
        output_dir=output_dir,
        include_tags=tags,
        exclude_tags=exclude,
        variables=variables,
        parallel=parallel,
        processes=processes,
    )

    # Print summary
    print()
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")

    print(f"\nResults: {output_dir}")
    print(f"  Report: {output_dir}/report.html")
    print(f"  Log: {output_dir}/log.html")

    return exit_code


@task
def ui_test(
    ctx,
    tags=None,
    exclude="skip",
    browser=DEFAULT_BROWSER,
    env=DEFAULT_ENV,
    headless=True,
    parallel=True,
    processes=DEFAULT_PROCESSES,
):
    """Run UI tests.

    Args:
        tags: Tags to include (comma-separated)
        exclude: Tags to exclude (default: skip)
        browser: Browser for tests (chrome, firefox, edge, safari)
        env: Environment (dev, staging, prod)
        headless: Run browser in headless mode
        parallel: Run tests in parallel with pabot
        processes: Number of parallel processes
    """
    return test(
        ctx,
        suite="ui",
        tags=tags,
        exclude=exclude,
        browser=browser,
        env=env,
        headless=headless,
        parallel=parallel,
        processes=processes,
    )


@task
def api_test(ctx, tags=None, exclude="skip", env=DEFAULT_ENV):
    """Run API tests.

    Args:
        tags: Tags to include (comma-separated)
        exclude: Tags to exclude (default: skip)
        env: Environment (dev, staging, prod)
    """
    return test(
        ctx,
        suite="api",
        tags=tags,
        exclude=exclude,
        env=env,
        headless=True,  # Not needed for API tests
        parallel=False,  # API tests typically don't need parallel
    )


@task
def smoke(ctx, env=DEFAULT_ENV, browser=DEFAULT_BROWSER, headless=True):
    """Run smoke tests.

    Quick validation of critical functionality.

    Args:
        env: Environment (dev, staging, prod)
        browser: Browser for UI tests
        headless: Run browser in headless mode
    """
    print("🔥 Running smoke tests...")
    return test(
        ctx,
        tags="smoke",
        env=env,
        browser=browser,
        headless=headless,
        parallel=True,
    )


@task
def regression(ctx, env=DEFAULT_ENV, browser=DEFAULT_BROWSER, headless=True, parallel=True):
    """Run full regression suite.

    Complete validation of all features.

    Args:
        env: Environment (dev, staging, prod)
        browser: Browser for UI tests
        headless: Run browser in headless mode
        parallel: Run tests in parallel
    """
    print("📋 Running regression tests...")
    return test(
        ctx,
        tags="regression",
        env=env,
        browser=browser,
        headless=headless,
        parallel=parallel,
    )


@task
def report(ctx, results_path=None, open_report=True):
    """Generate Allure report from test results.

    Args:
        results_path: Path to Allure results (default: results/allure)
        open_report: Open report in browser after generation
    """
    results = Path(results_path) if results_path else ALLURE_RESULTS
    report_dir = REPORTS_DIR / "allure"

    if not results.exists():
        print(f"❌ Results not found: {results}")
        print("  Run tests first to generate results.")
        sys.exit(1)

    print(f"📊 Generating Allure report...")

    # Clean old report
    if report_dir.exists():
        shutil.rmtree(report_dir)

    # Generate report
    ctx.run(f"allure generate {results} -o {report_dir} --clean")

    print(f"✅ Report generated: {report_dir}")

    # Open report
    if open_report:
        print("🌐 Opening report in browser...")
        ctx.run(f"allure open {report_dir}")


@task
def clean(ctx, all=False):
    """Clean test results and reports.

    Args:
        all: Also clean virtual environment
    """
    print("🧹 Cleaning...")

    # Clean results
    if RESULTS_DIR.exists():
        print("  Removing results...")
        shutil.rmtree(RESULTS_DIR)

    # Clean reports
    if REPORTS_DIR.exists():
        print("  Removing reports...")
        shutil.rmtree(REPORTS_DIR)

    # Clean venv
    if all:
        venv_path = PROJECT_ROOT / "venv"
        if venv_path.exists():
            print("  Removing virtual environment...")
            shutil.rmtree(venv_path)

    # Recreate directories
    ensure_dir(RESULTS_DIR)
    ensure_dir(REPORTS_DIR)

    print("✅ Clean complete!")


@task
def info(ctx):
    """Show environment and configuration info."""
    print("ℹ️  E2E Test Framework Info")
    print("=" * 40)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Tests directory: {TESTS_DIR}")
    print(f"Results directory: {RESULTS_DIR}")
    print(f"Reports directory: {REPORTS_DIR}")
    print(f"Config directory: {CONFIG_DIR}")
    print()

    # Check dependencies
    print("Dependencies:")
    result = ctx.run("robot --version", warn=True, hide=True)
    if result.ok:
        print(f"  ✅ Robot Framework: {result.stdout.strip()}")
    else:
        print("  ❌ Robot Framework: Not installed")

    result = ctx.run("pabot --version", warn=True, hide=True)
    if result.ok:
        print(f"  ✅ Pabot: {result.stdout.strip()}")
    else:
        print("  ❌ Pabot: Not installed")

    result = ctx.run("allure --version", warn=True, hide=True)
    if result.ok:
        print(f"  ✅ Allure: {result.stdout.strip()}")
    else:
        print("  ❌ Allure: Not installed (optional)")

    print()
    print("Available environments:")
    for config in CONFIG_DIR.glob("*.yaml"):
        print(f"  - {config.stem}")

    print()
    print("Test suites:")
    for suite in TESTS_DIR.iterdir():
        if suite.is_dir():
            count = len(list(suite.glob("*.robot")))
            print(f"  - {suite.name}/ ({count} files)")


@task
def dry_run(ctx, suite=None, env=DEFAULT_ENV):
    """Dry run to validate test cases without execution.

    Args:
        suite: Test suite to validate (ui, api, or path)
        env: Environment for variable resolution
    """
    # Determine test path
    if suite:
        suite_lower = suite.lower()
        if suite_lower == "ui":
            test_path = TESTS_DIR / "ui"
        elif suite_lower == "api":
            test_path = TESTS_DIR / "api"
        else:
            test_path = Path(suite)
    else:
        test_path = TESTS_DIR

    output_dir = RESULTS_DIR / "dry_run"
    ensure_dir(output_dir)

    print(f"🔍 Dry run validation: {test_path}")

    result = ctx.run(
        f"robot --dryrun --outputdir {output_dir} --variable ENVIRONMENT:{env} {test_path}",
        warn=True,
    )

    if result.ok:
        print("✅ All test cases validated successfully")
    else:
        print("❌ Validation failed - check output for errors")

    return result.exited


@task
def new_test(ctx, name, suite="ui"):
    """Create a new test file from template.

    Args:
        name: Test file name (without extension)
        suite: Test suite (ui or api)
    """
    suite_dir = TESTS_DIR / suite
    if not suite_dir.exists():
        print(f"❌ Suite not found: {suite}")
        sys.exit(1)

    test_file = suite_dir / f"{name}.robot"
    if test_file.exists():
        print(f"❌ Test file already exists: {test_file}")
        sys.exit(1)

    # Template
    if suite == "api":
        template = f'''*** Settings ***
Documentation    API tests for {name}

Resource    ../../resources/keywords/api_keywords.robot
Resource    ../../resources/keywords/common_keywords.robot

Suite Setup    Create API Session
Suite Teardown    Destroy API Session

Force Tags    api    {name}

*** Test Cases ***
Example Test Case
    [Documentation]    TODO: Add test description
    [Tags]    smoke
    When I Send GET Request    /endpoint
    Then Response Status Should Be    ${{STATUS_OK}}
'''
    else:
        template = f'''*** Settings ***
Documentation    UI tests for {name}

Resource    ../../resources/keywords/ui_keywords.robot
Resource    ../../resources/keywords/common_keywords.robot

Test Setup    Open Browser To Booking Homepage
Test Teardown    Close Booking Browser

Force Tags    ui    {name}

*** Test Cases ***
Example Test Case
    [Documentation]    TODO: Add test description
    [Tags]    smoke
    Given User Is On Booking Homepage
    When User Performs Action
    Then Expected Result Should Occur
'''

    test_file.write_text(template)
    print(f"✅ Created: {test_file}")
    print(f"\nEdit the file to add your test cases.")


@task(default=True)
def help(ctx):
    """Show available tasks and usage."""
    ctx.run("invoke --list")
    print()
    print("Examples:")
    print("  invoke test                     # Run all tests")
    print("  invoke test --suite ui          # Run UI tests")
    print("  invoke test --suite api         # Run API tests")
    print("  invoke test --tags smoke        # Run smoke tests")
    print("  invoke test --parallel          # Run in parallel")
    print("  invoke ui-test                  # Run UI tests (parallel)")
    print("  invoke api-test                 # Run API tests")
    print("  invoke smoke                    # Run smoke suite")
    print("  invoke regression               # Run full regression")
    print("  invoke report                   # Generate Allure report")
    print("  invoke lint                     # Run code quality checks")
    print("  invoke lint --fix               # Auto-fix linting issues")
    print("  invoke lint --strict            # Treat warnings as errors")
    print("  invoke validate                 # Validate framework structure")
    print("  invoke check-deps               # Check dependencies")
    print("  invoke clean                    # Clean results")
    print("  invoke info                     # Show environment info")


# Namespace configuration
ns = task.__module__
