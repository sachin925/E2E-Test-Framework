*** Settings ***
Documentation    API tests for hotel search and details

Resource    ../../resources/keywords/api_keywords.robot
Resource    ../../resources/keywords/common_keywords.robot

Suite Setup    Create API Session
Suite Teardown    Destroy API Session

Force Tags    api    hotels

*** Test Cases ***
Search Hotels By Location
    [Documentation]    Verify hotel search by location returns results
    [Tags]    smoke    regression
    When I Search For Hotels    location=Paris    checkin=2024-12-01    checkout=2024-12-05
    Then Response Status Should Be    ${STATUS_OK}
    And Response Should Contain    hotels
    And Hotels List Should Not Be Empty

Search Hotels With Filters
    [Documentation]    Verify hotel search with filters
    [Tags]    regression
    When I Search For Hotels    location=London    checkin=2024-12-01    checkout=2024-12-05    adults=2
    Then Response Status Should Be    ${STATUS_OK}
    And Response Should Contain    hotels

Get Hotel Details By ID
    [Documentation]    Verify retrieving hotel details
    [Tags]    smoke    regression
    When I Get Hotel Details    ${TEST_HOTEL_ID}
    Then Response Status Should Be    ${STATUS_OK}
    And Response Should Contain    hotel_name
    And Response Should Contain    location
    And Hotel Schema Should Be Valid

Search Returns Empty For Invalid Location
    [Documentation]    Verify empty results for invalid location
    [Tags]    regression
    When I Search For Hotels    location=InvalidCityXYZ123    checkin=2024-12-01    checkout=2024-12-05
    Then Response Status Should Be    ${STATUS_OK}
    And Response Should Contain    hotels
    And Hotels List Should Be Empty

Search Requires Valid Dates
    [Documentation]    Verify error for invalid date range
    [Tags]    regression
    When I Search For Hotels    location=Paris    checkin=2024-12-10    checkout=2024-12-05
    Then Response Status Should Be    ${STATUS_BAD_REQUEST}

*** Keywords ***
I Search For Hotels
    [Arguments]    &{params}
    [Documentation]    Search hotels with parameters
    ${response}=    Search Hotels    ${params}[location]    ${params}[checkin]    ${params}[checkout]    ${params.get('adults', 2)}
    Set Test Variable    ${API_RESPONSE}    ${response}

Hotels List Should Not Be Empty
    [Documentation]    Verify hotels list is not empty
    ${hotels}=    Get Response Field    hotels
    ${count}=    Get Length    ${hotels}
    Should Be True    ${count} > 0    Hotels list is empty

Hotels List Should Be Empty
    [Documentation]    Verify hotels list is empty
    ${hotels}=    Get Response Field    hotels
    ${count}=    Get Length    ${hotels}
    Should Be Equal As Integers    ${count}    0

Hotel Schema Should Be Valid
    [Documentation]    Validate hotel response schema
    ${hotel_data}=    Get Response JSON
    Validate Hotel Schema    ${hotel_data}
