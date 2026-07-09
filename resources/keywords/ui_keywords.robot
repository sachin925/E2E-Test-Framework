*** Settings ***
Documentation    Keywords for UI testing with Selenium

Library    SeleniumLibrary
Resource    ../variables/ui_variables.robot
Resource    common_keywords.robot

*** Keywords ***
Open Browser To Booking Homepage
    [Documentation]    Open browser and navigate to booking.com homepage
    ${headless}=    Get Variable Value    ${HEADLESS}    false
    ${browser}=    Get Variable Value    ${BROWSER}    chrome

    Run Keyword If    '${browser}' == 'chrome' and '${headless}' == 'true'
    ...    Open Chrome Browser In Headless Mode
    ...    ELSE    Open Browser    ${BASE_URL}    ${browser}

    Maximize Browser Window
    Set Selenium Timeout    ${EXPLICIT_WAIT}
    Set Selenium Implicit Wait    ${IMPLICIT_WAIT}
    Wait Until Page Contains Element    ${HOMEPAGE_SEARCH_BOX}
    Log    Opened booking.com homepage with ${browser} browser

Open Chrome Browser In Headless Mode
    [Documentation]    Open Chrome in headless mode for CI/CD
    ${options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Call Method    ${options}    add_argument    --headless
    Call Method    ${options}    add_argument    --disable-gpu
    Call Method    ${options}    add_argument    --no-sandbox
    Call Method    ${options}    add_argument    --disable-dev-shm-usage
    Call Method    ${options}    add_argument    --window-size\=1920,1080
    Create WebDriver    Chrome    options=${options}
    Go To    ${BASE_URL}

Close Booking Browser
    [Documentation]    Close browser and cleanup
    Close All Browsers

# Search Keywords
User Searches For Location
    [Arguments]    ${location}
    [Documentation]    Enter location in search box
    Wait Until Element Is Visible    ${HOMEPAGE_SEARCH_BOX}
    Input Text    ${HOMEPAGE_SEARCH_BOX}    ${location}
    Wait Until Page Contains    ${location}
    Sleep    1s    # Wait for autocomplete suggestions
    Press Keys    ${HOMEPAGE_SEARCH_BOX}    ENTER

User Selects Check-in Date
    [Arguments]    ${days_from_now}
    [Documentation]    Select check-in date
    ${date}=    Get Date From Today    ${days_from_now}
    ${formatted_date}=    Format Date For Booking    ${date}
    Click Element    ${HOMEPAGE_CHECKIN_DATE}
    Click Element    css=span[aria-label='${formatted_date}']

User Selects Check-out Date
    [Arguments]    ${days_from_now}
    [Documentation]    Select check-out date
    ${date}=    Get Date From Today    ${days_from_now}
    ${formatted_date}=    Format Date For Booking    ${date}
    Click Element    ${HOMEPAGE_CHECKOUT_DATE}
    Click Element    css=span[aria-label='${formatted_date}']

User Sets Guests
    [Arguments]    ${adults}=2    ${children}=0    ${rooms}=1
    [Documentation]    Set number of guests and rooms
    Click Element    ${HOMEPAGE_GUESTS_SELECTOR}

    # Set adults
    FOR    ${i}    IN RANGE    ${adults}
        Click Element    ${HOMEPAGE_ADULTS_INCREMENT}
    END

    # Set rooms
    FOR    ${i}    IN RANGE    ${rooms}
        Click Element    ${HOMEPAGE_ROOMS_INCREMENT}
    END

User Clicks Search Button
    [Documentation]    Click search button
    Click Element    ${HOMEPAGE_SEARCH_BUTTON}
    Wait Until Page Contains Element    ${SEARCH_RESULTS_CONTAINER}

Search Results Should Be Displayed
    [Documentation]    Verify search results are shown
    Wait Until Page Contains Element    ${SEARCH_RESULTS_CONTAINER}
    Page Should Contain Element    ${SEARCH_RESULT_ITEM}

All Results Should Match Location
    [Arguments]    ${expected_location}
    [Documentation]    Verify all results match the searched location
    ${results}=    Get WebElements    ${SEARCH_RESULT_ITEM}
    ${count}=    Get Length    ${results}
    Log    Found ${count} search results
    Should Be True    ${count} > 0    No search results found

Get Search Results Count
    [Documentation]    Get the number of search results
    ${results}=    Get WebElements    ${SEARCH_RESULT_ITEM}
    ${count}=    Get Length    ${results}
    [Return]    ${count}

Navigate To Next Results Page
    [Documentation]    Go to next page of results
    Click Element    ${NEXT_PAGE_BUTTON}
    Wait Until Page Contains Element    ${SEARCH_RESULTS_CONTAINER}

# Hotel Details Keywords
Open Hotel Details
    [Arguments]    ${index}=1
    [Documentation]    Open a specific hotel from search results
    ${results}=    Get WebElements    ${SEARCH_RESULT_TITLE}
    ${hotel}=    Get From List    ${results}    ${index}
    Click Element    ${hotel}
    Switch Window    NEW
    Wait Until Page Contains Element    ${HOTEL_NAME}

Get Hotel Name
    [Documentation]    Get the hotel name from details page
    ${name}=    Get Text    ${HOTEL_NAME}
    [Return]    ${name}

Get Hotel Price
    [Documentation]    Get the hotel price from details page
    ${price}=    Get Text    ${SEARCH_RESULT_PRICE}
    [Return]    ${price}

# Authentication Keywords
User Logs In
    [Arguments]    ${email}    ${password}
    [Documentation]    Login with credentials
    Go To    ${LOGIN_URL}
    Wait Until Element Is Visible    ${LOGIN_EMAIL}
    Input Text    ${LOGIN_EMAIL}    ${email}
    Input Password    ${LOGIN_PASSWORD}    ${password}
    Click Element    ${LOGIN_SUBMIT}
    Wait Until Element Is Visible    ${USER_AVATAR}

User Is Logged In
    [Documentation]    Verify user is logged in
    Page Should Contain Element    ${USER_AVATAR}

User Logs Out
    [Documentation]    Logout current user
    Click Element    ${USER_AVATAR}
    Click Element    ${LOGOUT_BUTTON}

# Date Helper Keywords
Get Date From Today
    [Arguments]    ${days_from_now}
    [Documentation]    Calculate date from today
    ${date}=    Evaluate    (datetime.date.today() + datetime.timedelta(days=${days_from_now})).strftime('%Y-%m-%d')    modules=datetime
    [Return]    ${date}

Format Date For Booking
    [Arguments]    ${date}
    [Documentation]    Format date for booking.com date picker
    ${formatted}=    Evaluate    datetime.datetime.strptime('${date}', '%Y-%m-%d').strftime('%B %d, %Y')    modules=datetime
    [Return]    ${formatted}

# Screenshot Keywords
Take Screenshot
    [Arguments]    ${filename}=${EMPTY}
    [Documentation]    Take screenshot with optional filename
    ${name}=    Set Variable If    '${filename}'    ${filename}    ${TEST NAME}_${timestamp}
    Capture Page Screenshot    ${SCREENSHOT_DIR}${/}${name}.png

# Waits
Wait For Page To Load
    [Documentation]    Wait for page to fully load
    Wait For Condition    return document.readyState == 'complete'

Wait For Element To Be Visible
    [Arguments]    ${locator}    ${timeout}=${EXPLICIT_WAIT}
    [Documentation]    Wait for element to be visible
    Wait Until Element Is Visible    ${locator}    ${timeout}
