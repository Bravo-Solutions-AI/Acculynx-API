from datetime import date
from typing import List, Optional, Dict, Any, AsyncIterator
import httpx
from .models import Job, Customer, Lead
from .exceptions import (
    AccuLynxAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)
from .mixins.jobs import JobsMixin
from .mixins.leads import LeadsMixin
from .enums import DateFilterType, SortOrder


class AccuLynxAPI(JobsMixin, LeadsMixin):
    """Client for interacting with the AccuLynx API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.acculynx.com/api/v2",
        timeout: float = 30.0,
    ):
        """Initialize the AccuLynx API client.

        Args:
            api_key: The API key for authentication
            base_url: The base URL for the API (defaults to v2 production API)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the underlying HTTP client."""
        await self._client.aclose()

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid authentication credentials", 401)
        elif response.status_code == 404:
            raise NotFoundError("Resource not found", 404)
        elif response.status_code == 422:
            raise ValidationError("Invalid request data", 422)
        elif response.status_code == 429:
            raise RateLimitError("API rate limit exceeded", 429)
        elif response.status_code >= 400:
            raise AccuLynxAPIError(
                f"API request failed: {response.text}", response.status_code
            )

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """Make a GET request to the API."""
        response = await self._client.get(endpoint, params=params)
        
        
        if response.status_code >= 400:
            self._handle_error(response)
        return response.json()

    async def get_customers(
        self, limit: int = 100, offset: int = 0
    ) -> List[Customer]:
        """Retrieve a list of customers.

        Args:
            limit: Maximum number of customers to return
            offset: Number of customers to skip

        Returns:
            List of Customer objects
        """
        data = await self._get(
            "/customers", params={"limit": limit, "offset": offset}
        )
        return [Customer.parse_obj(customer) for customer in data["customers"]]
  