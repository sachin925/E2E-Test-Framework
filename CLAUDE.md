# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

E2E Test Automation Framework for booking.com using Python + Robot Framework with API testing capabilities and Jenkins CI/CD integration.

## Technology Stack

- **Language**: Python 3.11+
- **Test Framework**: Robot Framework
- **Browser Automation**: Selenium WebDriver with Robot Framework SeleniumLibrary
- **API Testing**: Robot Framework RequestsLibrary
- **Reporting**: Robot Framework rebot, Allure
- **CI/CD**: Jenkins with Jenkinsfile

## Commands

All commands use Invoke task runner. Run `invoke --list` to see all available tasks.

### Setup
```bash
# Setup environment (creates venv, installs dependencies)
invoke setup

# Activate virtual environment
source venv/bin/activate
```

### Running Tests
```bash
# Run all tests
invoke test

# Run specific test suite
invoke test --suite ui
invoke test --suite api
invoke test --suite tests/ui/search_tests.robot

# Run with tags
invoke test --tags smoke
invoke test --tags regression
invoke smoke                # Quick smoke test shortcut
invoke regression           # Full regression suite

# Run with specific browser
invoke test --browser chrome
invoke test --browser firefox

# Run in parallel (default for UI tests)
invoke test --parallel
invoke ui-test              # Runs in parallel by default

# Run in specific environment
invoke test --env staging
invoke test --env prod

# Run with headless mode (default: true)
invoke test --headless false
```

### Quick Tasks
```bash
invoke ui-test              # Run UI tests (parallel)
invoke api-test             # Run API tests
invoke smoke                # Run smoke tests
invoke regression           # Run regression suite
```

### Reporting
```bash
# Generate Allure report
invoke report

# Generate report without opening browser
invoke report --open-report false
```

### Code Quality
```bash
# Run linters
invoke lint

# Run linters with auto-fix
invoke lint --fix
```

### Utilities
```bash
# Show environment info
invoke info

# Clean results and reports
invoke clean

# Dry run to validate tests
invoke dry-run

# Create new test file from template
invoke new-test my_test --suite ui
```

## Project Structure

```
E2E-Test-Framework/
├── tests/                    # Test suites
│   ├── ui/                   # UI test cases
│   │   ├── search_tests.robot
│   │   ├── booking_tests.robot
│   │   └── user_account_tests.robot
│   └── api/                  # API test cases
│       ├── auth_api_tests.robot
│       └── booking_api_tests.robot
├── resources/                # Shared resources
│   ├── keywords/             # Custom keywords
│   │   ├── common_keywords.robot
│   │   ├── ui_keywords.robot
│   │   └── api_keywords.robot
│   └── variables/            # Variables and configs
│       ├── common_variables.robot
│       ├── ui_variables.robot
│       └── api_variables.robot
├── libraries/                # Custom Python libraries
│   ├── booking_api.py
│   └── custom_utils.py
├── results/                  # Test output (gitignored)
├── reports/                  # Generated reports (gitignored)
├── config/                   # Environment configurations
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── jenkins/                  # Jenkins configurations
│   └── Jenkinsfile
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
└── README.md
```

## Architecture

### Test Layers
1. **Test Cases** (`tests/`): High-level test scenarios using Gherkin-style syntax
2. **Keywords** (`resources/keywords/`): Reusable test steps and actions
3. **Variables** (`resources/variables/`): Environment-agnostic configuration
4. **Libraries** (`libraries/`): Python code for complex operations

### Key Patterns
- **Page Object Pattern**: UI interactions encapsulated in keyword files
- **Data-Driven Testing**: Test data externalized to variables
- **Environment Isolation**: Config files per environment
- **API/UI Separation**: Clear distinction between API and UI test suites

## Jenkins CI

The Jenkinsfile defines stages:
1. **Setup**: Install dependencies
2. **Lint**: Code quality checks
3. **API Tests**: Run API test suite
4. **UI Tests**: Run UI test suite in parallel
5. **Report**: Generate and publish Allure reports

### Jenkins Configuration
- Requires Allure plugin installed
- Configure browser nodes for parallel UI execution
- Set environment variables via Jenkins credentials

## Environment Variables

Set these for local development or in Jenkins:
- `BASE_URL`: Booking.com base URL (default: https://www.booking.com)
- `API_BASE_URL`: API endpoint base URL
- `BROWSER`: Browser to use (chrome, firefox, edge, safari)
- `HEADLESS`: Run in headless mode (true/false)
- `ENVIRONMENT`: Target environment (dev, staging, prod)
