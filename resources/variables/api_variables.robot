*** Settings ***
Documentation    API test variables and endpoints

*** Variables ***
# API Base URLs
${API_BASE_URL}          https://distribution-xml.booking.com/2.0
${API_TIMEOUT}           30s

# Endpoints
${ENDPOINT_AUTH}         /json/auth
${ENDPOINT_HOTELS}       /json/hotels
${ENDPOINT_SEARCH}       /json/search
${ENDPOINT_BOOKINGS}     /json/bookings
${ENDPOINT_LOCATIONS}    /json/locations

# Default Headers
&{DEFAULT_HEADERS}       Content-Type=application/json    Accept=application/json    User-Agent=Robot-Framework-E2E-Tests

# Authentication (set via environment or secrets)
${API_USERNAME}          ${EMPTY}
${API_PASSWORD}          ${EMPTY}
${API_TOKEN}             ${EMPTY}

# Common Test Data
${TEST_HOTEL_ID}         12345
${TEST_LOCATION_ID}      -1456928
${TEST_CHECKIN}          ${EMPTY}
${TEST_CHECKOUT}         ${EMPTY}

# Response Codes
${STATUS_OK}             200
${STATUS_CREATED}        201
${STATUS_BAD_REQUEST}    400
${STATUS_UNAUTHORIZED}   401
${STATUS_NOT_FOUND}      404
${STATUS_SERVER_ERROR}   500
