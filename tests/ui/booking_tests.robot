*** Settings ***
Documentation    UI tests for booking flow

Resource    ../../resources/keywords/ui_keywords.robot
Resource    ../../resources/keywords/common_keywords.robot

Test Setup    Open Browser To Booking Homepage
Test Teardown    Close Booking Browser

Force Tags    ui    booking

*** Test Cases ***
User Can View Hotel Details From Search Results
    [Documentation]    Verify user can view hotel details
    [Tags]    smoke    regression
    Given User Searches For Hotels    Paris
    When User Opens Hotel Details    0
    Then Hotel Details Should Be Displayed
    And Hotel Name Should Be Visible

User Can See Hotel Price
    [Documentation]    Verify hotel price is displayed
    [Tags]    regression
    Given User Searches For Hotels    Paris
    When User Opens Hotel Details    0
    Then Hotel Price Should Be Visible

*** Keywords ***
User Searches For Hotels
    [Arguments]    ${location}
    [Documentation]    Perform hotel search
    User Searches For Location    ${location}
    User Clicks Search Button
    Search Results Should Be Displayed

Hotel Details Should Be Displayed
    [Documentation]    Verify hotel details page is shown
    Page Should Contain Element    ${HOTEL_NAME}
    Page Should Contain Element    ${HOTEL_ADDRESS}

Hotel Name Should Be Visible
    [Documentation]    Verify hotel name is visible
    ${name}=    Get Hotel Name
    Log    Hotel name: ${name}
    Should Not Be Empty    ${name}

Hotel Price Should Be Visible
    [Documentation]    Verify hotel price is shown
    Page Should Contain Element    ${SEARCH_RESULT_PRICE}
