"""
Custom Robot Framework library for Booking.com API operations.
Provides high-level keywords for API testing.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from robot.api import logger
from robot.api.deco import keyword, library


@library
class BookingAPI:
    """Custom library for Booking.com API testing."""

    def __init__(self, base_url: str = "https://distribution-xml.booking.com/2.0"):
        self.base_url = base_url
        self.session: Optional[requests.Session] = None
        self.auth_token: Optional[str] = None

    @keyword
    def create_api_session(self, base_url: str = None):
        """Create a new API session.

        Args:
            base_url: Optional override for base URL
        """
        if base_url:
            self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        logger.info(f"Created API session for {self.base_url}")

    @keyword
    def set_auth_token(self, token: str):
        """Set authentication token for subsequent requests.

        Args:
            token: Authentication token
        """
        self.auth_token = token
        if self.session:
            self.session.headers["Authorization"] = f"Bearer {token}"

    @keyword
    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None,
        expected_status: int = 200
    ) -> Dict[str, Any]:
        """Make HTTP request to API endpoint.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            expected_status: Expected HTTP status code

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data,
            timeout=30
        )

        logger.info(f"{method} {url} -> {response.status_code}")

        if response.status_code != expected_status:
            logger.warn(
                f"Unexpected status code: {response.status_code} "
                f"(expected {expected_status})"
            )

        try:
            return response.json()
        except json.JSONDecodeError:
            return {"raw_response": response.text}

    @keyword
    def generate_booking_dates(
        self,
        checkin_days: int = 7,
        stay_duration: int = 3
    ) -> Dict[str, str]:
        """Generate check-in and check-out dates.

        Args:
            checkin_days: Days from today for check-in
            stay_duration: Number of nights for the stay

        Returns:
            Dictionary with checkin and checkout dates
        """
        today = datetime.now()
        checkin = today + timedelta(days=checkin_days)
        checkout = checkin + timedelta(days=stay_duration)

        return {
            "checkin": checkin.strftime("%Y-%m-%d"),
            "checkout": checkout.strftime("%Y-%m-%d")
        }

    @keyword
    def validate_response_schema(
        self,
        response: Dict,
        required_fields: list
    ) -> bool:
        """Validate response contains required fields.

        Args:
            response: API response dictionary
            required_fields: List of required field names

        Returns:
            True if all fields present, raises error otherwise
        """
        missing = [f for f in required_fields if f not in response]

        if missing:
            raise AssertionError(
                f"Missing required fields: {', '.join(missing)}"
            )

        return True

    @keyword
    def extract_value_from_response(
        self,
        response: Dict,
        json_path: str
    ) -> Any:
        """Extract value from response using JSON path.

        Args:
            response: API response dictionary
            json_path: JSON path expression (e.g., 'data.hotels[0].id')

        Returns:
            Extracted value
        """
        import jsonpath_ng

        jsonpath_expr = jsonpath_ng.parse(f"$.{json_path}")
        matches = jsonpath_expr.find(response)

        if not matches:
            raise ValueError(f"No value found at path: {json_path}")

        return matches[0].value

    @keyword
    def compare_response_values(
        self,
        response: Dict,
        field: str,
        expected_value: Any
    ) -> bool:
        """Compare response field value with expected.

        Args:
            response: API response dictionary
            field: Field name to compare
            expected_value: Expected value

        Returns:
            True if values match
        """
        actual = response.get(field)

        if actual != expected_value:
            raise AssertionError(
                f"Field '{field}' expected '{expected_value}' "
                f"but got '{actual}'"
            )

        return True
