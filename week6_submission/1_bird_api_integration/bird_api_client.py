import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_BASE_URL = os.getenv("BIRDS_API_URL", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_TIMEOUT = 10.0


class BirdAPIError(Exception):
    """Raised when the Gradio app cannot complete an API request."""


class BirdAPIClient:
    """Small HTTP client used by the Gradio integration app."""

    def __init__(
        self,
        base_url: str = DEFAULT_API_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        try:
            with httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                transport=self.transport,
            ) as client:
                response = client.request(method, path, params=params, json=json)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BirdAPIError(_extract_error_message(exc.response)) from exc
        except httpx.HTTPError as exc:
            raise BirdAPIError(
                f"Could not reach the Birds API at {self.base_url}. "
                "Start the FastAPI server and try again."
            ) from exc

        if response.status_code == 204:
            return None
        return response.json()

    def list_species(
        self,
        *,
        conservation_status: Optional[str] = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if conservation_status:
            params["conservation_status"] = conservation_status
        return self._request("GET", "/species/", params=params)

    def create_species(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/species/", json=payload)

    def list_birds(
        self,
        *,
        species_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if species_id is not None:
            params["species_id"] = species_id
        return self._request("GET", "/birds/", params=params)

    def create_bird(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/birds/", json=payload)

    def list_birdspottings(
        self,
        *,
        observer_name: Optional[str] = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if observer_name:
            params["observer_name"] = observer_name
        return self._request("GET", "/birdspotting/", params=params)

    def create_birdspotting(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/birdspotting/", json=payload)


def _extract_error_message(response: httpx.Response) -> str:
    default_message = response.text or response.reason_phrase or "Unknown API error"

    try:
        payload = response.json()
    except ValueError:
        return default_message

    detail = payload.get("detail")
    if isinstance(detail, list):
        messages = [item.get("msg", str(item)) for item in detail]
        return "; ".join(messages)
    if detail:
        return str(detail)
    return default_message
