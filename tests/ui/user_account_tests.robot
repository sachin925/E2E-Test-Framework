*** Settings ***
Documentation    UI tests for user authentication and account

Resource    ../../resources/keywords/ui_keywords.robot
Resource    ../../resources/keywords/common_keywords.robot

Test Setup    Open Browser To Booking Homepage
Test Teardown    Close Booking Browser

Force Tags    ui    auth

*** Test Cases ***
Login Page Is Accessible
    [Documentation]    Verify login page can be accessed
    [Tags]    smoke
    Given User Is On Booking Homepage
    When User Navigates To Login Page
    Then Login Form Should Be Displayed

Login With Invalid Credentials Shows Error
    [Documentation]    Verify error message for invalid login
    [Tags]    regression
    Given User Is On Login Page
    When User Enters Invalid Credentials
    And User Submits Login Form
    Then Error Message Should Be Displayed

User Avatar Visible After Successful Login
    [Documentation]    Verify user avatar is visible after login
    [Tags]    regression
    [Setup]    NONE
    Given User Is Logged In With Valid Credentials
    Then User Avatar Should Be Visible
    [Teardown]    Close Booking Browser

*** Keywords ***
User Navigates To Login Page
    [Documentation]    Navigate to login page
    Go To    ${LOGIN_URL}
    Wait Until Element Is Visible    ${LOGIN_EMAIL}

Login Form Should Be Displayed
    [Documentation]    Verify login form elements
    Page Should Contain Element    ${LOGIN_EMAIL}
    Page Should Contain Element    ${LOGIN_PASSWORD}
    Page Should Contain Element    ${LOGIN_SUBMIT}

User Is On Login Page
    [Documentation]    Ensure user is on login page
    Go To    ${LOGIN_URL}
    Wait Until Element Is Visible    ${LOGIN_EMAIL}

User Enters Invalid Credentials
    [Documentation]    Enter invalid test credentials
    Input Text    ${LOGIN_EMAIL}    invalid@example.com
    Input Password    ${LOGIN_PASSWORD}    invalidpassword123

User Submits Login Form
    [Documentation]    Submit login form
    Click Element    ${LOGIN_SUBMIT}
    Sleep    2s

Error Message Should Be Displayed
    [Documentation]    Verify error message is shown
    Wait Until Page Contains Element    ${ERROR_MESSAGE}

User Is Logged In With Valid Credentials
    [Documentation]    Login with valid test credentials
    [Arguments]    ${email}=${TEST_USER_EMAIL}    ${password}=${TEST_USER_PASSWORD}
    Open Browser To Booking Homepage
    User Logs In    ${email}    ${password}

User Avatar Should Be Visible
    [Documentation]    Verify user avatar is displayed
    Page Should Contain Element    ${USER_AVATAR}
