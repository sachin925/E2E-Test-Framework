*** Settings ***
Documentation    UI tests for booking.com search functionality

Resource    ../../resources/keywords/ui_keywords.robot
Resource    ../../resources/keywords/common_keywords.robot

Test Setup    Open Browser To Booking Homepage
Test Teardown    Close Booking Browser

Force Tags    ui    search

*** Test Cases ***
User Can Search For Hotels By Location
    [Documentation]    Verify user can search for hotels by location
    [Tags]    smoke    regression
    Given User Is On Booking Homepage
    When User Searches For Location    Paris
    And User Clicks Search Button
    Then Search Results Should Be Displayed
    And All Results Should Match Location    Paris

User Can Search With Specific Dates
    [Documentation]    Verify user can search with check-in and check-out dates
    [Tags]    regression
    Given User Is On Booking Homepage
    When User Searches For Location    London
    And User Selects Check-in Date    7
    And User Selects Check-out Date    10
    And User Clicks Search Button
    Then Search Results Should Be Displayed

User Can Search With Multiple Guests
    [Documentation]    Verify user can search with different guest configurations
    [Tags]    regression
    Given User Is On Booking Homepage
    When User Searches For Location    New York
    And User Sets Guests    adults=3    rooms=2
    And User Clicks Search Button
    Then Search Results Should Be Displayed

Search Results Can Be Paginated
    [Documentation]    Verify pagination works on search results
    [Tags]    regression    slow
    Given User Is On Booking Homepage
    When User Searches For Location    Paris
    And User Clicks Search Button
    Then Search Results Should Be Displayed
    When User Navigates To Next Results Page
    Then Search Results Should Be Displayed

No Results Message For Invalid Location
    [Documentation]    Verify appropriate message for invalid location search
    [Tags]    regression
    Given User Is On Booking Homepage
    When User Searches For Location    InvalidLocation12345
    And User Clicks Search Button
    Then Page Should Contain Element    ${SEARCH_NO_RESULTS}

*** Keywords ***
User Is On Booking Homepage
    [Documentation]    Verify user is on homepage
    Page Should Contain Element    ${HOMEPAGE_SEARCH_BOX}
