*** Settings ***
Documentation    Common variables used across all test suites

*** Variables ***
# Environment
${ENVIRONMENT}           ${EMPTY}
${CONFIG_FILE}           ${EMPTY}

# Browser
${BROWSER}               chrome
${HEADLESS}              false

# Timeouts
${IMPLICIT_WAIT}         10s
${EXPLICIT_WAIT}         30s
${PAGE_LOAD_TIMEOUT}     60s

# Test Data Paths
${TEST_DATA_DIR}         ${CURDIR}${/}..${/}..${/}test_data
${SCREENSHOT_DIR}        ${CURDIR}${/}..${/}..${/}results${/}screenshots

# Retry Settings
${MAX_RETRIES}           3
${RETRY_DELAY}           2s
