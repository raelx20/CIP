from typing import Any

import httpx

from app.contracts.geocoder import GeocoderProvider
from app.contracts.places import PlacesProvider


class GoogleMapsGeocoder(GeocoderProvider, PlacesProvider):
    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 10.0,
    ):
        self.api_key = api_key or ""
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.client = httpx.AsyncClient(timeout=timeout)

    async def geocode(self, address: str, **kwargs) -> dict[str, Any]:
        if not self.api_key:
            return {"error": "API key not configured"}

        response = await self.client.get(
            f"{self.base_url}/geocode/json",
            params={
                "address": address,
                "key": self.api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK" and data["results"]:
            result = data["results"][0]
            return {
                "latitude": result["geometry"]["location"]["lat"],
                "longitude": result["geometry"]["location"]["lng"],
                "formatted_address": result.get("formatted_address"),
                "address_components": result.get("address_components", []),
                "place_id": result.get("place_id"),
            }

        return {"error": f"Geocoding failed: {data['status']}"}

    async def reverse_geocode(self, latitude: float, longitude: float, **kwargs) -> dict[str, Any]:
        if not self.api_key:
            return {"error": "API key not configured"}

        response = await self.client.get(
            f"{self.base_url}/geocode/json",
            params={
                "latlng": f"{latitude},{longitude}",
                "key": self.api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK" and data["results"]:
            result = data["results"][0]
            return {
                "formatted_address": result.get("formatted_address"),
                "address_components": result.get("address_components", []),
                "place_id": result.get("place_id"),
            }

        return {"error": f"Reverse geocoding failed: {data['status']}"}

    async def search_places(
        self,
        query: str,
        location: tuple[float, float] | None = None,
        radius: int | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        if not self.api_key:
            return []

        params = {
            "input": query,
            "key": self.api_key,
        }

        if location and radius:
            params["location"] = f"{location[0]},{location[1]}"
            params["radius"] = radius

        response = await self.client.get(
            f"{self.base_url}/place/autocomplete/json",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            return [
                {
                    "place_id": pred.get("place_id"),
                    "description": pred.get("description"),
                    "structured_formatting": pred.get("structured_formatting"),
                }
                for pred in data.get("predictions", [])
            ]

        return []

    async def get_place_details(self, place_id: str, **kwargs) -> dict[str, Any]:
        if not self.api_key:
            return {"error": "API key not configured"}

        response = await self.client.get(
            f"{self.base_url}/place/details/json",
            params={
                "place_id": place_id,
                "key": self.api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            result = data["result"]
            return {
                "name": result.get("name"),
                "formatted_address": result.get("formatted_address"),
                "latitude": result["geometry"]["location"]["lat"],
                "longitude": result["geometry"]["location"]["lng"],
                "types": result.get("types", []),
            }

        return {"error": f"Place details failed: {data['status']}"}

    def health_check(self) -> bool:
        return bool(self.api_key)
