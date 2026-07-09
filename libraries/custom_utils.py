"""
Custom utility functions for the E2E test framework.
"""

import json
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path

import yaml
from faker import Faker


class TestDataGenerator:
    """Generate test data for testing."""

    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)

    def generate_email(self) -> str:
        """Generate random email address."""
        return self.fake.email()

    def generate_name(self) -> Dict[str, str]:
        """Generate random name."""
        return {
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name()
        }

    def generate_phone(self) -> str:
        """Generate random phone number."""
        return self.fake.phone_number()

    def generate_address(self) -> Dict[str, str]:
        """Generate random address."""
        return {
            "street": self.fake.street_address(),
            "city": self.fake.city(),
            "country": self.fake.country(),
            "postcode": self.fake.postcode()
        }

    def generate_credit_card(self) -> Dict[str, str]:
        """Generate test credit card data."""
        return {
            "number": self.fake.credit_card_number(),
            "expiry": self.fake.credit_card_expire(),
            "cvv": "123"
        }

    def generate_guest_info(self) -> Dict[str, Any]:
        """Generate complete guest information."""
        name = self.generate_name()
        return {
            "first_name": name["first_name"],
            "last_name": name["last_name"],
            "email": self.generate_email(),
            "phone": self.generate_phone()
        }


class ConfigLoader:
    """Load and manage configuration files."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, Dict] = {}

    def load(self, environment: str = "dev") -> Dict:
        """Load configuration for specified environment.

        Args:
            environment: Environment name (dev, staging, prod)

        Returns:
            Configuration dictionary
        """
        if environment in self._configs:
            return self._configs[environment]

        config_path = self.config_dir / f"{environment}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self._configs[environment] = config
        return config

    def get(self, environment: str, key: str, default: Any = None) -> Any:
        """Get specific configuration value.

        Args:
            environment: Environment name
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        config = self.load(environment)

        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value


class DateUtils:
    """Date manipulation utilities."""

    @staticmethod
    def get_date(days_offset: int = 0) -> str:
        """Get date string with offset from today.

        Args:
            days_offset: Days from today (positive = future)

        Returns:
            Date string in YYYY-MM-DD format
        """
        target_date = datetime.now() + timedelta(days=days_offset)
        return target_date.strftime("%Y-%m-%d")

    @staticmethod
    def get_date_range(
        start_offset: int,
        duration: int
    ) -> Dict[str, str]:
        """Get date range for booking.

        Args:
            start_offset: Days from today for start date
            duration: Number of days for the duration

        Returns:
            Dictionary with start and end dates
        """
        start = datetime.now() + timedelta(days=start_offset)
        end = start + timedelta(days=duration)

        return {
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d")
        }

    @staticmethod
    def format_date(
        date_string: str,
        output_format: str = "%B %d, %Y"
    ) -> str:
        """Format date string to different format.

        Args:
            date_string: Input date string (YYYY-MM-DD)
            output_format: Output format string

        Returns:
            Formatted date string
        """
        date = datetime.strptime(date_string, "%Y-%m-%d")
        return date.strftime(output_format)


class FileUtils:
    """File operation utilities."""

    @staticmethod
    def read_json(file_path: str) -> Dict:
        """Read JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON data
        """
        with open(file_path, "r") as f:
            return json.load(f)

    @staticmethod
    def write_json(file_path: str, data: Dict):
        """Write data to JSON file.

        Args:
            file_path: Path to output file
            data: Data to write
        """
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def read_yaml(file_path: str) -> Dict:
        """Read YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML data
        """
        with open(file_path, "r") as f:
            return yaml.safe_load(f)


# Convenience functions
def generate_random_string(length: int = 10) -> str:
    """Generate random alphanumeric string."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def generate_random_number(min_val: int = 1, max_val: int = 100) -> int:
    """Generate random number in range."""
    return random.randint(min_val, max_val)
