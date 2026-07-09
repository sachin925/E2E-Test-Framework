*** Settings ***
Documentation    API tests for booking operations

Resource    ../../resources/keywords/api_keywords.robot
Resource    ../../resources/keywords/common_keywords.robot

Suite Setup    Create API Session
Suite Teardown    Destroy API Session

Force Tags    api    booking

*** Test Cases ***
Create New Booking
    [Documentation]    Verify user can create a new booking
    [Tags]    smoke    regression
    [Setup]    Generate Test Booking Data
    When I Create A Booking
    Then Response Status Should Be    ${STATUS_CREATED}
    And Response Should Contain    booking_id
    And Booking Should Have Valid Status
    [Teardown]    Cancel Test Booking

Get Booking By ID
    [Documentation]    Verify user can retrieve booking details
    [Tags]    smoke    regression
    Given A Booking Exists
    When I Get Booking Details
    Then Response Status Should Be    ${STATUS_OK}
    And Response Should Contain    booking_id
    And Response Should Contain    hotel_name

Update Booking
    [Documentation]    Verify user can update booking details
    [Tags]    regression
    Given A Booking Exists
    When I Update Booking With New Dates
    Then Response Status Should Be    ${STATUS_OK}
    And Response Should Contain Value    status    modified

Cancel Booking
    [Documentation]    Verify user can cancel a booking
    [Tags]    smoke    regression
    Given A Booking Exists
    When I Cancel The Booking
    Then Response Status Should Be    ${STATUS_OK}
    And Booking Status Should Be    cancelled

Cannot Get Non-existent Booking
    [Documentation]    Verify 404 for non-existent booking
    [Tags]    regression
    When I Get Booking Details    ${NON_EXISTENT_BOOKING_ID}
    Then Response Status Should Be    ${STATUS_NOT_FOUND}

*** Keywords ***
Generate Test Booking Data
    [Documentation]    Generate test data for booking
    ${checkin}=    Get Date From Today    7
    ${checkout}=    Get Date From Today    10
    ${guest_info}=    Generate Guest Info
    Set Test Variable    ${TEST_CHECKIN}    ${checkin}
    Set Test Variable    ${TEST_CHECKOUT}    ${checkout}
    Set Test Variable    ${TEST_GUEST_INFO}    ${guest_info}

I Create A Booking
    [Documentation]    Create a booking via API
    ${response}=    Create Booking    ${TEST_HOTEL_ID}    ${TEST_CHECKIN}    ${TEST_CHECKOUT}    ${TEST_GUEST_INFO}
    Set Test Variable    ${BOOKING_ID}    ${response.json()}[booking_id]

Booking Should Have Valid Status
    [Documentation]    Verify booking status
    ${status}=    Get Response Field    status
    Should Be True    '${status}' in ['confirmed', 'pending']

A Booking Exists
    [Documentation]    Ensure a test booking exists
    Generate Test Booking Data
    I Create A Booking

I Get Booking Details
    [Arguments]    ${booking_id}=${BOOKING_ID}
    [Documentation]    Get booking details
    ${response}=    Get Booking    ${booking_id}
    Set Test Variable    ${API_RESPONSE}    ${response}

I Update Booking With New Dates
    [Documentation]    Update booking dates
    ${new_checkin}=    Get Date From Today    14
    ${new_checkout}=    Get Date From Today    17
    ${update_data}=    Create Dictionary    checkin=${new_checkin}    checkout=${new_checkout}
    ${response}=    I Send PUT Request    ${ENDPOINT_BOOKINGS}/${BOOKING_ID}    ${update_data}
    Set Test Variable    ${API_RESPONSE}    ${response}

I Cancel The Booking
    [Documentation]    Cancel the booking
    ${response}=    Cancel Booking    ${BOOKING_ID}
    Set Test Variable    ${API_RESPONSE}    ${response}

Booking Status Should Be
    [Arguments]    ${expected_status}
    [Documentation]    Verify booking status
    ${status}=    Get Response Field    status
    Should Be Equal    ${status}    ${expected_status}

Cancel Test Booking
    [Documentation]    Cleanup test booking
    Run Keyword And Ignore Error    Cancel Booking    ${BOOKING_ID}

Get Date From Today
    [Arguments]    ${days}
    [Documentation]    Get future date
    ${date}=    Evaluate    (datetime.date.today() + datetime.timedelta(days=${days})).strftime('%Y-%m-%d')    modules=datetime
    [Return]    ${date}
