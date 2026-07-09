*** Settings ***
Documentation    Common keywords used across all test suites

Resource    ../variables/common_variables.robot

*** Keywords ***
Initialize Test Environment
    [Documentation]    Set up the test environment based on configuration
    ${config}=    Load Environment Config
    Set Suite Variable    ${SUITE_CONFIG}    ${config}
    Log    Testing environment: ${config}[environment]    level=INFO

Load Environment Config
    [Documentation]    Load configuration based on ENVIRONMENT variable
    [Return]    ${config}
    ${env}=    Get Environment Variable    ENVIRONMENT    default=dev
    ${config_file}=    Set Variable    ${CURDIR}${/}..${/}..${/}config${/}${env}.yaml
    ${config}=    Load YAML    ${config_file}
    [Return]    ${config}

Get Environment Variable
    [Arguments]    ${name}    ${default}=${EMPTY}
    [Documentation]    Get environment variable with fallback to default
    ${value}=    Get Variable Value    ${%${name}}    ${default}
    [Return]    ${value}

Load YAML
    [Arguments]    ${file_path}
    [Documentation]    Load YAML configuration file
    ${content}=    Get File    ${file_path}
    ${yaml}=    Evaluate    yaml.safe_load($content)    modules=yaml
    [Return]    ${yaml}

Generate Random Email
    [Documentation]    Generate a random email for testing
    ${timestamp}=    Get Time    epoch
    ${email}=    Set Variable    test_${timestamp}@example.com
    [Return]    ${email}

Generate Random String
    [Arguments]    ${length}=10
    [Documentation]    Generate a random alphanumeric string
    ${string}=    Generate Random String    ${length}    chars=[LETTERS][NUMBERS]
    [Return]    ${string}

Wait And Retry
    [Arguments]    ${keyword}    ${max_retries}=${MAX_RETRIES}    ${delay}=${RETRY_DELAY}
    [Documentation]    Execute keyword with retry logic
    FOR    ${i}    IN RANGE    ${max_retries}
        ${status}=    Run Keyword And Return Status    ${keyword}
        Exit For Loop If    ${status}
        Sleep    ${delay}
    END
    Run Keyword If    not ${status}    Fail    Keyword '${keyword}' failed after ${max_retries} retries

Capture Screenshot On Failure
    [Documentation]    Capture screenshot when test fails
    ${status}=    Run Keyword And Return Status    Page Should Contain Element    css=body
    Run Keyword If    ${status}    Capture Page Screenshot    ${SCREENSHOT_DIR}${/}${TEST NAME}.png

Log Test Step
    [Arguments]    ${step}
    [Documentation]    Log a test step for debugging
    Log    [STEP] ${step}    level=INFO    console=yes
