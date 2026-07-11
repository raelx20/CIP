from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.location.value_objects import Coordinates


class PostGISGeospatial:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def point_in_polygon(
        self,
        coordinates: Coordinates,
        table_name: str,
        geometry_column: str = "geom",
    ) -> list[dict[str, Any]]:
        query = text(f"""
            SELECT * FROM {table_name}
            WHERE ST_Contains(
                {geometry_column},
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
            )
        """)

        result = await self.session.execute(
            query,
            {"latitude": coordinates.latitude, "longitude": coordinates.longitude},
        )

        return [dict(row) for row in result.mappings().all()]

    async def find_nearest(
        self,
        coordinates: Coordinates,
        table_name: str,
        geometry_column: str = "geom",
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        query = text(f"""
            SELECT *, ST_Distance(
                {geometry_column},
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
            ) as distance
            FROM {table_name}
            ORDER BY {geometry_column} <-> ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
            LIMIT :limit
        """)

        result = await self.session.execute(
            query,
            {
                "latitude": coordinates.latitude,
                "longitude": coordinates.longitude,
                "limit": limit,
            },
        )

        return [dict(row) for row in result.mappings().all()]

    async def calculate_distance(
        self,
        coord1: Coordinates,
        coord2: Coordinates,
    ) -> float:
        query = text("""
            SELECT ST_Distance(
                ST_SetSRID(ST_MakePoint(:lon1, :lat1), 4326)::geography,
                ST_SetSRID(ST_MakePoint(:lon2, :lat2), 4326)::geography
            ) as distance
        """)

        result = await self.session.execute(
            query,
            {
                "lat1": coord1.latitude,
                "lon1": coord1.longitude,
                "lat2": coord2.latitude,
                "lon2": coord2.longitude,
            },
        )

        row = result.first()
        return row[0] if row else 0.0

    async def get_constituency(
        self,
        coordinates: Coordinates,
    ) -> str | None:
        query = text("""
            SELECT name FROM constituencies
            WHERE ST_Contains(
                geom,
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
            )
            LIMIT 1
        """)

        result = await self.session.execute(
            query,
            {"latitude": coordinates.latitude, "longitude": coordinates.longitude},
        )

        row = result.first()
        return row[0] if row else None
