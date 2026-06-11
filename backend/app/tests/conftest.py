import os
import pytest
from unittest.mock import AsyncMock, patch

# Set environment variables to override any real settings from .env
os.environ["ENVIRONMENT"] = "test"
os.environ["BREVO_API_KEY"] = "dummy-test-key"

from app.core.config import settings

# Force setting updates
settings.ENVIRONMENT = "test"
settings.BREVO_API_KEY = "dummy-test-key"

@pytest.fixture(autouse=True)
def mock_email_service():
    """
    Globally mock send_transactional_email to prevent any network calls
    to Brevo during test runs, returning True (mock success) by default.
    """
    with patch("app.services.email_service.EmailService.send_transactional_email", new_callable=AsyncMock) as mock:
        mock.return_value = True
        yield mock
