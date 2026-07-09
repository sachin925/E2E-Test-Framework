*** Settings ***
Documentation    API tests for authentication

Resource    ../../resources/keywords/api_keywords.robot
Resource    ../../resources/keywords/common_keywords.robot

Suite Setup    Create API Session
Suite Teardown    Destroy API Session

Force Tags    api    auth

*** Test Cases ***
Authenticate With Valid Credentials
    [Documentation]    Verify successful authentication
    [Tags]    smoke    regression
    When I Authenticate With Valid Credentials
    Then Response Status Should Be    ${STATUS_OK}
    And Response Should Contain    token
    And Token Should Not Be Empty

Authenticate With Invalid Credentials
    [Documentation]    Verify authentication failure with invalid credentials
    [Tags]    smoke    regression
    When I Authenticate With Credentials    invalid_user    invalid_pass
    Then Response Status Should Be    ${STATUS_UNAUTHORIZED}

Authenticate With Missing Credentials
    [Documentation]    Verify authentication failure with missing credentials
    [Tags]    regression
    When I Authenticate With Credentials    ${EMPTY}    ${EMPTY}
    Then Response Status Should Be    ${STATUS_BAD_REQUEST}

Authenticated User Can Access Protected Endpoint
    [Documentation]    Verify authenticated user can access protected resources
    [Tags]    smoke    regression
    Given I Have A Valid Auth Token
    When I Access Protected Endpoint
    Then Response Status Should Be    ${STATUS_OK}

Unauthenticated User Cannot Access Protected Endpoint
    [Documentation]    Verify unauthenticated user cannot access protected resources
    [Tags]    regression
    Given I Have No Auth Token
    When I Access Protected Endpoint
    Then Response Status Should Be    ${STATUS_UNAUTHORIZED}

Token Refresh
    [Documentation]    Verify token can be refreshed
    [Tags]    regression
    Given I Have A Valid Auth Token
    When I Refresh The Token
    Then Response Status Should Be    ${STATUS_OK}
    And Response Should Contain    token
    And New Token Should Be Different

*** Keywords ***
I Authenticate With Valid Credentials
    [Documentation]    Authenticate with test credentials
    ${response}=    Authenticate API User
    Set Test Variable    ${API_RESPONSE}    ${response}

I Authenticate With Credentials
    [Arguments]    ${username}    ${password}
    [Documentation]    Authenticate with specified credentials
    ${credentials}=    Create Dictionary    username=${username}    password=${password}
    ${response}=    POST On Session    booking_api    ${ENDPOINT_AUTH}    json=${credentials}    expected_status=any
    Set Test Variable    ${API_RESPONSE}    ${response}

Token Should Not Be Empty
    [Documentation]    Verify token is present
    ${token}=    Get Response Field    token
    Should Not Be Empty    ${token}

I Have A Valid Auth Token
    [Documentation]    Get valid authentication token
    Authenticate API User

I Have No Auth Token
    [Documentation]    Ensure no auth token is set
    Set Suite Variable    ${API_TOKEN}    ${EMPTY}

I Access Protected Endpoint
    [Documentation]    Access a protected API endpoint
    ${response}=    I Send GET Request    ${ENDPOINT_BOOKINGS}

I Refresh The Token
    [Documentation]    Refresh authentication token
    ${old_token}=    Get Variable Value    ${API_TOKEN}
    ${response}=    POST On Session    booking_api    /auth/refresh    expected_status=any
    Set Test Variable    ${API_RESPONSE}    ${response}

New Token Should Be Different
    [Documentation]    Verify new token differs from old
    ${new_token}=    Get Response Field    token
    Should Not Be Equal    ${API_TOKEN}    ${new_token}
