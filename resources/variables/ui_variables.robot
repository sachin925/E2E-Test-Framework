*** Settings ***
Documentation    UI test variables and locators

*** Variables ***
# URLs
${BASE_URL}              https://www.booking.com
${LOGIN_URL}             ${BASE_URL}/signin
${ACCOUNT_URL}           ${BASE_URL}/account

# Locators - Homepage
${HOMEPAGE_SEARCH_BOX}           css=div#ss
${HOMEPAGE_SEARCH_BUTTON}        css=button[type='submit']
${HOMEPAGE_CHECKIN_DATE}         css=div[data-mode='checkin']
${HOMEPAGE_CHECKOUT_DATE}        css=div[data-mode='checkout']
${HOMEPAGE_GUESTS_SELECTOR}      css=div#xp__guests__toggle
${HOMEPAGE_ADULTS_INCREMENT}     css=button[data-bui-ref='adults-increment']
${HOMEPAGE_ADULTS_DECREMENT}     css=button[data-bui-ref='adults-decrement']
${HOMEPAGE_ROOMS_INCREMENT}      css=button[data-bui-ref='rooms-increment']
${HOMEPAGE_ROOMS_DECREMENT}      css=button[data-bui-ref='rooms-decrement']

# Locators - Search Results
${SEARCH_RESULTS_CONTAINER}      css=div#search_results_table
${SEARCH_RESULT_ITEM}            css=div[data-testid='property-card']
${SEARCH_RESULT_TITLE}           css=div[data-testid='title']
${SEARCH_RESULT_PRICE}           css=span[data-testid='price-and-discounted-price']
${SEARCH_RESULT_RATING}          css=div[data-testid='review-score']
${NEXT_PAGE_BUTTON}              css=button[aria-label='Next page']

# Locators - Hotel Details
${HOTEL_NAME}                    css=div#hp_hotel_name
${HOTEL_ADDRESS}                 css=span.hp_address_subtitle
${HOTEL_RATING}                  css=div.bui-review-score__badge
${BOOK_NOW_BUTTON}               css=button#booking_form_submit

# Locators - Booking Form
${BOOKING_FIRSTNAME}             css=input[name='firstname']
${BOOKING_LASTNAME}              css=input[name='lastname']
${BOOKING_EMAIL}                 css=input[name='email']
${BOOKING_PHONE}                 css=input[name='phone']
${BOOKING_REQUESTS}              css=textarea[name='requests']
${BOOKING_TERMS_CHECKBOX}        css=input[name='terms_and_conditions']
${BOOKING_COMPLETE_BUTTON}       css=button[data-testid='complete-booking']

# Locators - Authentication
${LOGIN_EMAIL}                   css=input[name='username']
${LOGIN_PASSWORD}                css=input[name='password']
${LOGIN_SUBMIT}                  css=button[type='submit']
${SIGNUP_BUTTON}                 css=a[data-testid='signup-link']
${USER_AVATAR}                   css=div[data-testid='user-avatar']
${LOGOUT_BUTTON}                 css=button[data-testid='logout']

# Locators - Error Messages
${ERROR_MESSAGE}                 css=div.bui-message--error
${SEARCH_NO_RESULTS}             css=div.sr_no_results
