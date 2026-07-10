# E2E Test Automation Framework

End-to-end test automation framework for booking.com using Python + Robot Framework with API testing capabilities and Jenkins CI/CD integration.

## Features

- UI Testing with Selenium WebDriver
- API Testing with RequestsLibrary
- Parallel test execution with Pabot
- Allure reporting integration
- Data-driven testing support
- Environment-based configuration
- Jenkins CI/CD pipeline ready

## Prerequisites

- Python 3.11+
- Chrome/Firefox browser installed
- Jenkins (for CI/CD)

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd E2E-Test-Framework

# Setup environment (creates venv and installs dependencies)
invoke setup

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Show available tasks
invoke --list

# Run all tests
invoke test

# Run UI tests
invoke ui-test

# Run API tests
invoke api-test

# Run smoke tests
invoke smoke

# Run regression suite
invoke regression

# Generate Allure report
invoke report
```

## Project Structure

```
E2E-Test-Framework/
├── tests/                    # Test suites
│   ├── ui/                   # UI test cases
│   └── api/                  # API test cases
├── resources/                # Shared resources
│   ├── keywords/             # Custom keywords
│   └── variables/            # Variables and configs
├── libraries/                # Custom Python libraries
├── results/                  # Test output
├── config/                   # Environment configurations
└── jenkins/                  # Jenkins CI setup
```

## Configuration

Environment configurations are stored in `config/` directory:

- `dev.yaml` - Development environment
- `staging.yaml` - Staging environment  
- `prod.yaml` - Production environment

Override settings via environment variables:
```bash
export ENVIRONMENT=staging
export BROWSER=chrome
export HEADLESS=true
```

## Test Tags

- `smoke` - Critical smoke tests
- `regression` - Full regression suite
- `ui` - UI tests
- `api` - API tests
- `search` - Search functionality tests
- `booking` - Booking flow tests
- `slow` - Long-running tests

## Reporting

```bash
# Generate default Robot Framework reports
robot --outputdir results tests/

# Generate Allure reports
robot --listener allure_robotframework results/allure tests/
allure generate results/allure -o reports/allure --clean
allure open reports/allure
```

## Jenkins CI

The framework includes a Jenkinsfile for CI/CD integration:

1. Install required Jenkins plugins:
   - Allure Plugin
   - Pipeline
   - Git

2. Create a new Pipeline job
3. Point to the Jenkinsfile in `CI/Jenkinsfile`

## Writing Tests

### UI Test Example
```robotframework
*** Test Cases ***
User Can Search For Hotels
    [Tags]    smoke    ui    search
    Given User Opens Booking Homepage
    When User Searches For Location    Paris
    And User Selects Check-in Date    tomorrow
    And User Selects Check-out Date    7 days from now
    And User Clicks Search Button
    Then Search Results Should Be Displayed
    And All Results Should Match Location    Paris
```

### API Test Example
```robotframework
*** Test Cases ***
Get Hotel Details
    [Tags]    smoke    api
    When I Send GET Request    /hotels/${HOTEL_ID}
    Then Response Status Should Be    200
    And Response Should Contain    hotel_name
```

## License

MIT License
