*** Settings ***
Documentation    Keywords for API testing with RequestsLibrary

Library    RequestsLibrary
Library    Collections
Library    JSONLibrary
Resource    ../variables/api_variables.robot
Resource    common_keywords.robot

*** Keywords ***
Create API Session
    [Documentation]    Create HTTP session for API testing
    ${headers}=    Create Dictionary    Content-Type=application/json    Accept=application/json

    # Add authentication if available
    ${api_token}=    Get Variable Value    ${API_TOKEN}
    Run Keyword If    '${api_token}'    Set To Dictionary    ${headers}    Authorization=Bearer ${api_token}

    Create Session    booking_api    ${API_BASE_URL}    headers=${headers}    timeout=${API_TIMEOUT}    verify=True

Destroy API Session
    [Documentation]    Close all HTTP sessions
    Delete All Sessions

# Authentication
Authenticate API User
    [Arguments]    ${username}=${API_USERNAME}    ${password}=${API_PASSWORD}
    [Documentation]    Authenticate and get API token
    ${credentials}=    Create Dictionary    username=${username}    password=${password}
    ${response}=    POST On Session    booking_api    ${ENDPOINT_AUTH}    json=${credentials}
    Should Be Equal As Integers    ${response.status_code}    ${STATUS_OK}
    ${token}=    Get Value From JSON    ${response.json()}    $.token
    Set Suite Variable    ${API_TOKEN}    ${token}
    [Return]    ${token}

# Generic Request Keywords
I Send GET Request
    [Arguments]    ${endpoint}    ${params}=${EMPTY}
    [Documentation]    Send GET request to endpoint
    ${response}=    GET On Session    booking_api    ${endpoint}    params=${params}
    Set Test Variable    ${API_RESPONSE}    ${response}
    [Return]    ${response}

I Send POST Request
    [Arguments]    ${endpoint}    ${body}=${EMPTY}
    [Documentation]    Send POST request to endpoint
    ${response}=    POST On Session    booking_api    ${endpoint}    json=${body}
    Set Test Variable    ${API_RESPONSE}    ${response}
    [Return]    ${response}

I Send PUT Request
    [Arguments]    ${endpoint}    ${body}=${EMPTY}
    [Documentation]    Send PUT request to endpoint
    ${response}=    PUT On Session    booking_api    ${endpoint}    json=${body}
    Set Test Variable    ${API_RESPONSE}    ${response}
    [Return]    ${response}

I Send DELETE Request
    [Arguments]    ${endpoint}
    [Documentation]    Send DELETE request to endpoint
    ${response}=    DELETE On Session    booking_api    ${endpoint}
    Set Test Variable    ${API_RESPONSE}    ${response}
    [Return]    ${response}

# Response Verification Keywords
Response Status Should Be
    [Arguments]    ${expected_status}
    [Documentation]    Verify response status code
    Should Be Equal As Integers    ${API_RESPONSE.status_code}    ${expected_status}
    ...    msg=Expected status ${expected_status} but got ${API_RESPONSE.status_code}

Response Should Contain
    [Arguments]    ${field}
    [Documentation]    Verify response contains specific field
    ${json}=    Set Variable    ${API_RESPONSE.json()}
    Dictionary Should Contain Key    ${json}    ${field}
    ...    msg=Response does not contain field '${field}'

Response Should Contain Value
    [Arguments]    ${field}    ${expected_value}
    [Documentation]    Verify response field has expected value
    ${json}=    Set Variable    ${API_RESPONSE.json()}
    ${actual_value}=    Get From Dictionary    ${json}    ${field}
    Should Be Equal    ${actual_value}    ${expected_value}
    ...    msg=Field '${field}' expected '${expected_value}' but got '${actual_value}'

Response Should Be JSON
    [Documentation]    Verify response is valid JSON
    ${content_type}=    Get From Dictionary    ${API_RESPONSE.headers}    Content-Type
    Should Contain    ${content_type}    application/json

Get Response Field
    [Arguments]    ${field}
    [Documentation]    Get value of field from response
    ${json}=    Set Variable    ${API_RESPONSE.json()}
    ${value}=    Get From Dictionary    ${json}    ${field}
    [Return]    ${value}

Get Response JSON
    [Documentation]    Get full JSON response
    ${json}=    Set Variable    ${API_RESPONSE.json()}
    [Return]    ${json}

# Hotel API Keywords
Search Hotels
    [Arguments]    ${location}    ${checkin}    ${checkout}    ${adults}=2
    [Documentation]    Search for hotels with parameters
    ${params}=    Create Dictionary
    ...    location=${location}
    ...    checkin=${checkin}
    ...    checkout=${checkout}
    ...    adults=${adults}
    ${response}=    I Send GET Request    ${ENDPOINT_SEARCH}    ${params}
    [Return]    ${response}

Get Hotel Details
    [Arguments]    ${hotel_id}
    [Documentation]    Get details for a specific hotel
    ${endpoint}=    Set Variable    ${ENDPOINT_HOTELS}/${hotel_id}
    ${response}=    I Send GET Request    ${endpoint}
    [Return]    ${response}

Create Booking
    [Arguments]    ${hotel_id}    ${checkin}    ${checkout}    ${guest_info}
    [Documentation]    Create a new booking
    ${booking_data}=    Create Dictionary
    ...    hotel_id=${hotel_id}
    ...    checkin=${checkin}
    ...    checkout=${checkout}
    ...    guest=${guest_info}
    ${response}=    I Send POST Request    ${ENDPOINT_BOOKINGS}    ${booking_data}
    [Return]    ${response}

Get Booking
    [Arguments]    ${booking_id}
    [Documentation]    Get booking details by ID
    ${endpoint}=    Set Variable    ${ENDPOINT_BOOKINGS}/${booking_id}
    ${response}=    I Send GET Request    ${endpoint}
    [Return]    ${response}

Cancel Booking
    [Arguments]    ${booking_id}
    [Documentation]    Cancel a booking
    ${endpoint}=    Set Variable    ${ENDPOINT_BOOKINGS}/${booking_id}
    ${response}=    I Send DELETE Request    ${endpoint}
    [Return]    ${response}

# Location API Keywords
Search Locations
    [Arguments]    ${query}
    [Documentation]    Search for locations by name
    ${params}=    Create Dictionary    query=${query}
    ${response}=    I Send GET Request    ${ENDPOINT_LOCATIONS}    ${params}
    [Return]    ${response}

# Validation Keywords
Validate Hotel Schema
    [Arguments]    ${hotel_data}
    [Documentation]    Validate hotel data against schema
    Dictionary Should Contain Key    ${hotel_data}    hotel_id
    Dictionary Should Contain Key    ${hotel_data}    hotel_name
    Dictionary Should Contain Key    ${hotel_data}    location
    Dictionary Should Contain Key    ${hotel_data}    price

Validate Booking Schema
    [Arguments]    ${booking_data}
    [Documentation]    Validate booking data against schema
    Dictionary Should Contain Key    ${booking_data}    booking_id
    Dictionary Should Contain Key    ${booking_data}    hotel_id
    Dictionary Should Contain Key    ${booking_data}    checkin_date
    Dictionary Should Contain Key    ${booking_data}    checkout_date
    Dictionary Should Contain Key    ${booking_data}    status

# Data Generation
Generate Guest Info
    [Documentation]    Generate random guest information
    ${guest}=    Create Dictionary
    ...    first_name=John
    ...    last_name=Doe
    ...    email=test@example.com
    ...    phone=+1234567890
    [Return]    ${guest}

# Pagination Keywords
Get Paginated Results
    [Arguments]    ${endpoint}    ${page}=1    ${per_page}=10
    [Documentation]    Get paginated results from API
    ${params}=    Create Dictionary    page=${page}    per_page=${per_page}
    ${response}=    I Send GET Request    ${endpoint}    ${params}
    [Return]    ${response}
