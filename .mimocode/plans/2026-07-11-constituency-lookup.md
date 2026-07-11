# Constituency Lookup Feature — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a validated constituency lookup with GPS-based auto-detection and search autocomplete across the CIP platform.

**Architecture:** New `constituencies` table with PostGIS geometry for boundary storage. REST API for search/lookup. Reusable React `<ConstituencySelector>` component integrated into registration, submission, and dashboards.

**Tech Stack:** Python/FastAPI, PostgreSQL/PostGIS, SQLAlchemy/Alembic, Next.js 16, React 19, Tailwind CSS 4

## Global Constraints

- Python 3.12+, Next.js 16, React 19, Tailwind CSS 4
- All new code follows existing DDD patterns in `backend/app/`
- Frontend uses existing API client at `frontend/src/lib/api/client.ts`
- PostGIS extension required — verify it's enabled before Task 1
- UUID primary keys on all new tables
- All endpoints under `/api/v1/` prefix
- No external API dependencies for GPS lookup (PostGIS only)

---

## File Structure

### Backend (new/modified)

| File | Responsibility |
|------|---------------|
| `backend/app/database/models/constituency.py` | Constituency SQLAlchemy model |
| `backend/app/domain/constituency/value_objects.py` | Constituency domain value objects |
| `backend/app/domain/constituency/entities.py` | Constituency entity |
| `backend/app/infrastructure/database/repositories/constituency.py` | Constituency repository |
| `backend/app/infrastructure/geospatial/postgis.py` | **Modify** — wire up GPS lookup |
| `backend/app/api/v1/constituencies/router.py` | Constituency API routes |
| `backend/app/api/v1/constituencies/schemas.py` | Request/response schemas |
| `backend/app/api/v1/__init__.py` | **Modify** — register router |
| `backend/app/application/services/constituency.py` | Constituency application service |
| `backend/scripts/seed_constituencies.py` | Data seeding script |
| `backend/migrations/versions/xxxx_add_constituencies.py` | Alembic migration |
| `backend/tests/api/v1/test_constituencies.py` | API endpoint tests |
| `backend/tests/infrastructure/test_constituency_repository.py` | Repository tests |

### Frontend (new/modified)

| File | Responsibility |
|------|---------------|
| `frontend/src/components/ConstituencySelector.tsx` | Reusable selector component |
| `frontend/src/lib/api/client.ts` | **Modify** — add constituency API methods |
| `frontend/src/app/register/page.tsx` | **Modify** — integrate selector |
| `frontend/src/app/mp/page.tsx` | **Modify** — add constituency filter |

---

### Task 1: Database Model + Migration

**Covers:** [S1]

**Files:**
- Create: `backend/app/database/models/constituency.py`
- Create: `backend/migrations/versions/xxxx_add_constituencies.py`

**Interfaces:**
- Produces: `Constituency` SQLAlchemy model with `id`, `name`, `state`, `district`, `type`, `geom`, `centroid_lat`, `centroid_lng`, `population`, `created_at`

- [ ] **Step 1: Verify PostGIS extension**

```bash
cd backend
python -c "from app.database.session import engine; import sqlalchemy; sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS postgis').execute_with(engine)"
```

- [ ] **Step 2: Create the Constituency model**

```python
# backend/app/database/models/constituency.py
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from app.database.base import Base


class Constituency(Base):
    __tablename__ = "constituencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    district: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="lok_sabha"
    )  # 'lok_sabha' or 'vidhan_sabha'
    ac_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pc_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    geom = mapped_column(
        Geometry("MULTIPOLYGON", srid=4326), nullable=True
    )
    centroid_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    centroid_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

- [ ] **Step 3: Generate Alembic migration**

```bash
cd backend
alembic revision --autogenerate -m "add constituencies table"
```

- [ ] **Step 4: Add PostGIS extension to migration**

Edit the generated migration to add at the top of `upgrade()`:

```python
def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    # ... auto-generated code
```

- [ ] **Step 5: Run migration**

```bash
cd backend
alembic upgrade head
```

- [ ] **Step 6: Verify table exists**

```bash
cd backend
python -c "
from app.database.session import engine
import sqlalchemy
result = sqlalchemy.text(\"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'constituencies'\").execute_with(engine)
for row in result:
    print(row)
"
```

Expected: All columns listed with correct types.

- [ ] **Step 7: Commit**

```bash
git add backend/app/database/models/constituency.py backend/migrations/versions/
git commit -m "feat: add constituencies table with PostGIS geometry"
```

---

### Task 2: Domain Layer

**Covers:** [S1]

**Files:**
- Create: `backend/app/domain/constituency/__init__.py`
- Create: `backend/app/domain/constituency/value_objects.py`
- Create: `backend/app/domain/constituency/entities.py`

**Interfaces:**
- Produces: `ConstituencyType` enum, `ConstituencySearchCriteria` dataclass, `Constituency` entity

- [ ] **Step 1: Create value objects**

```python
# backend/app/domain/constituency/value_objects.py
from dataclasses import dataclass
from enum import Enum


class ConstituencyType(str, Enum):
    LOK_SABHA = "lok_sabha"
    VIDHAN_SABHA = "vidhan_sabha"


@dataclass(frozen=True)
class ConstituencySearchCriteria:
    query: str | None = None
    state: str | None = None
    district: str | None = None
    type: ConstituencyType | None = None
    skip: int = 0
    limit: int = 20


@dataclass(frozen=True)
class GPSLookupResult:
    latitude: float
    longitude: float
```

- [ ] **Step 2: Create entity**

```python
# backend/app/domain/constituency/entities.py
import uuid
from dataclasses import dataclass

from app.domain.constituency.value_objects import ConstituencyType


@dataclass(frozen=True)
class Constituency:
    id: uuid.UUID
    name: str
    state: str
    district: str | None
    type: ConstituencyType
    ac_number: str | None
    pc_number: str | None
    centroid_lat: float | None
    centroid_lng: float | None
    population: int | None
```

- [ ] **Step 3: Create `__init__.py`**

```python
# backend/app/domain/constituency/__init__.py
from app.domain.constituency.entities import Constituency
from app.domain.constituency.value_objects import (
    ConstituencySearchCriteria,
    ConstituencyType,
    GPSLookupResult,
)

__all__ = [
    "Constituency",
    "ConstituencySearchCriteria",
    "ConstituencyType",
    "GPSLookupResult",
]
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/domain/constituency/
git commit -m "feat: add constituency domain layer (value objects, entity)"
```

---

### Task 3: Repository Layer

**Covers:** [S1, S2]

**Files:**
- Create: `backend/app/infrastructure/database/repositories/constituency.py`
- Create: `backend/tests/infrastructure/test_constituency_repository.py`

**Interfaces:**
- Consumes: `Constituency` model (Task 1), `ConstituencySearchCriteria` (Task 2)
- Produces: `ConstituencyRepository` with `search()`, `get_by_id()`, `get_by_gps()`

- [ ] **Step 1: Write failing test for search**

```python
# backend/tests/infrastructure/test_constituency_repository.py
import pytest
from app.infrastructure.database.repositories.constituency import ConstituencyRepository
from app.domain.constituency.value_objects import ConstituencySearchCriteria


@pytest.mark.asyncio
async def test_search_returns_matching_constituencies(async_session):
    repo = ConstituencyRepository(async_session)
    criteria = ConstituencySearchCriteria(query="Mumbai")
    results = await repo.search(criteria)
    assert isinstance(results, list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/infrastructure/test_constituency_repository.py -v
```

Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement repository**

```python
# backend/app/infrastructure/database/repositories/constituency.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_Contains, ST_SetSRID, ST_MakePoint

from app.database.models.constituency import Constituency as ConstituencyModel
from app.domain.constituency.value_objects import (
    ConstituencySearchCriteria,
    ConstituencyType,
)
from app.domain.constituency.entities import Constituency


class ConstituencyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(self, criteria: ConstituencySearchCriteria) -> list[Constituency]:
        query = select(ConstituencyModel)

        if criteria.query:
            query = query.where(
                ConstituencyModel.name.ilike(f"%{criteria.query}%")
            )
        if criteria.state:
            query = query.where(ConstituencyModel.state == criteria.state)
        if criteria.district:
            query = query.where(ConstituencyModel.district == criteria.district)
        if criteria.type:
            query = query.where(ConstituencyModel.type == criteria.type.value)

        query = query.order_by(ConstituencyModel.name)
        query = query.offset(criteria.skip).limit(criteria.limit)

        result = await self.session.execute(query)
        return [self._to_entity(r) for r in result.scalars().all()]

    async def get_by_id(self, constituency_id: str) -> Constituency | None:
        query = select(ConstituencyModel).where(
            ConstituencyModel.id == constituency_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_gps(self, latitude: float, longitude: float) -> Constituency | None:
        point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        query = (
            select(ConstituencyModel)
            .where(ST_Contains(ConstituencyModel.geom, point))
            .limit(1)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def count(self, criteria: ConstituencySearchCriteria) -> int:
        query = select(func.count(ConstituencyModel.id))

        if criteria.query:
            query = query.where(
                ConstituencyModel.name.ilike(f"%{criteria.query}%")
            )
        if criteria.state:
            query = query.where(ConstituencyModel.state == criteria.state)
        if criteria.district:
            query = query.where(ConstituencyModel.district == criteria.district)
        if criteria.type:
            query = query.where(ConstituencyModel.type == criteria.type.value)

        result = await self.session.execute(query)
        return result.scalar()

    def _to_entity(self, model: ConstituencyModel) -> Constituency:
        return Constituency(
            id=model.id,
            name=model.name,
            state=model.state,
            district=model.district,
            type=ConstituencyType(model.type),
            ac_number=model.ac_number,
            pc_number=model.pc_number,
            centroid_lat=model.centroid_lat,
            centroid_lng=model.centroid_lng,
            population=model.population,
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/infrastructure/test_constituency_repository.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/infrastructure/database/repositories/constituency.py backend/tests/infrastructure/test_constituency_repository.py
git commit -m "feat: add constituency repository with search, GPS lookup"
```

---

### Task 4: API Schemas

**Covers:** [S2]

**Files:**
- Create: `backend/app/api/v1/constituencies/__init__.py`
- Create: `backend/app/api/v1/constituencies/schemas.py`

**Interfaces:**
- Consumes: `Constituency` entity (Task 2)
- Produces: `ConstituencyResponse`, `ConstituencyListResponse`, `ConstituencyLookupRequest`

- [ ] **Step 1: Create schemas**

```python
# backend/app/api/v1/constituencies/schemas.py
import uuid
from pydantic import BaseModel, Field


class ConstituencyResponse(BaseModel):
    id: uuid.UUID
    name: str
    state: str
    district: str | None = None
    type: str
    ac_number: str | None = None
    pc_number: str | None = None
    centroid_lat: float | None = None
    centroid_lng: float | None = None
    population: int | None = None

    model_config = {"from_attributes": True}


class ConstituencyListResponse(BaseModel):
    constituencies: list[ConstituencyResponse]
    total: int
    skip: int
    limit: int


class ConstituencyLookupResponse(BaseModel):
    constituency: ConstituencyResponse | None = None
    found: bool
    message: str | None = None
```

- [ ] **Step 2: Create `__init__.py`**

```python
# backend/app/api/v1/constituencies/__init__.py
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/constituencies/
git commit -m "feat: add constituency API schemas"
```

---

### Task 5: Application Service

**Covers:** [S2]

**Files:**
- Create: `backend/app/application/services/constituency.py`

**Interfaces:**
- Consumes: `ConstituencyRepository` (Task 3), `ConstituencySearchCriteria` (Task 2)
- Produces: `ConstituencyService` with `search()`, `get_by_id()`, `lookup_by_gps()`

- [ ] **Step 1: Implement service**

```python
# backend/app/application/services/constituency.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.constituency.value_objects import (
    ConstituencySearchCriteria,
    GPSLookupResult,
)
from app.domain.constituency.entities import Constituency
from app.infrastructure.database.repositories.constituency import ConstituencyRepository


class ConstituencyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ConstituencyRepository(session)

    async def search(self, criteria: ConstituencySearchCriteria) -> tuple[list[Constituency], int]:
        constituencies = await self.repository.search(criteria)
        total = await self.repository.count(criteria)
        return constituencies, total

    async def get_by_id(self, constituency_id: str) -> Constituency | None:
        return await self.repository.get_by_id(constituency_id)

    async def lookup_by_gps(self, latitude: float, longitude: float) -> Constituency | None:
        return await self.repository.get_by_gps(latitude, longitude)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/application/services/constituency.py
git commit -m "feat: add constituency application service"
```

---

### Task 6: API Endpoints

**Covers:** [S2]

**Files:**
- Create: `backend/app/api/v1/constituencies/router.py`
- Modify: `backend/app/api/v1/__init__.py`
- Create: `backend/tests/api/v1/test_constituencies.py`

**Interfaces:**
- Consumes: `ConstituencyService` (Task 5), schemas (Task 4)
- Produces: GET `/api/v1/constituencies`, GET `/api/v1/constituencies/{id}`, GET `/api/v1/constituencies/lookup`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/api/v1/test_constituencies.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_constituencies(client: AsyncClient):
    response = await client.get("/api/v1/constituencies")
    assert response.status_code == 200
    data = response.json()
    assert "constituencies" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_constituency_not_found(client: AsyncClient):
    response = await client.get("/api/v1/constituencies/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_gps_lookup_no_match(client: AsyncClient):
    response = await client.get("/api/v1/constituencies/lookup?lat=0.0&lng=0.0")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/api/v1/test_constituencies.py -v
```

Expected: FAIL with 404 (endpoint doesn't exist yet).

- [ ] **Step 3: Create router**

```python
# backend/app/api/v1/constituencies/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.application.services.constituency import ConstituencyService
from app.domain.constituency.value_objects import ConstituencySearchCriteria
from app.api.v1.constituencies.schemas import (
    ConstituencyResponse,
    ConstituencyListResponse,
    ConstituencyLookupResponse,
)

router = APIRouter(prefix="/constituencies", tags=["Constituencies"])


@router.get("", response_model=ConstituencyListResponse)
async def list_constituencies(
    q: str | None = Query(None, description="Search query"),
    state: str | None = Query(None),
    district: str | None = Query(None),
    type: str | None = Query(None, description="lok_sabha or vidhan_sabha"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = ConstituencyService(db)
    criteria = ConstituencySearchCriteria(
        query=q, state=state, district=district, type=type, skip=skip, limit=limit
    )
    constituencies, total = await service.search(criteria)
    return ConstituencyListResponse(
        constituencies=[ConstituencyResponse.model_validate(c) for c in constituencies],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/lookup", response_model=ConstituencyLookupResponse)
async def lookup_by_gps(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    db: AsyncSession = Depends(get_db),
):
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")

    service = ConstituencyService(db)
    constituency = await service.lookup_by_gps(lat, lng)

    if constituency:
        return ConstituencyLookupResponse(
            constituency=ConstituencyResponse.model_validate(constituency),
            found=True,
        )
    return ConstituencyLookupResponse(
        found=False,
        message="Location not found in any constituency",
    )


@router.get("/{constituency_id}", response_model=ConstituencyResponse)
async def get_constituency(
    constituency_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ConstituencyService(db)
    constituency = await service.get_by_id(constituency_id)
    if not constituency:
        raise HTTPException(status_code=404, detail="Constituency not found")
    return ConstituencyResponse.model_validate(constituency)
```

- [ ] **Step 4: Register router**

```python
# backend/app/api/v1/__init__.py
# Add to existing router registrations:
from app.api.v1.constituencies.router import router as constituencies_router
api_router.include_router(constituencies_router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend
pytest tests/api/v1/test_constituencies.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/v1/constituencies/ backend/app/api/v1/__init__.py backend/tests/api/v1/test_constituencies.py
git commit -m "feat: add constituency API endpoints (list, search, GPS lookup)"
```

---

### Task 7: Frontend API Client

**Covers:** [S2]

**Files:**
- Modify: `frontend/src/lib/api/client.ts`

**Interfaces:**
- Consumes: API endpoints (Task 6)
- Produces: `searchConstituencies()`, `lookupConstituencyByGPS()`, `getConstituency()`

- [ ] **Step 1: Add types and methods to client**

```typescript
// Add to frontend/src/lib/api/client.ts

export interface Constituency {
  id: string;
  name: string;
  state: string;
  district?: string;
  type: string;
  ac_number?: string;
  pc_number?: string;
  centroid_lat?: number;
  centroid_lng?: number;
  population?: number;
}

export interface ConstituencyListResponse {
  constituencies: Constituency[];
  total: number;
  skip: number;
  limit: number;
}

export interface ConstituencyLookupResponse {
  constituency?: Constituency;
  found: boolean;
  message?: string;
}

// Add methods to the apiClient object:
async searchConstituencies(params: {
  q?: string;
  state?: string;
  district?: string;
  type?: string;
  skip?: number;
  limit?: number;
}): Promise<ConstituencyListResponse> {
  const searchParams = new URLSearchParams();
  if (params.q) searchParams.set("q", params.q);
  if (params.state) searchParams.set("state", params.state);
  if (params.district) searchParams.set("district", params.district);
  if (params.type) searchParams.set("type", params.type);
  if (params.skip) searchParams.set("skip", String(params.skip));
  if (params.limit) searchParams.set("limit", String(params.limit));
  return this.get(`/api/v1/constituencies?${searchParams.toString()}`);
}

async lookupConstituencyByGPS(lat: number, lng: number): Promise<ConstituencyLookupResponse> {
  return this.get(`/api/v1/constituencies/lookup?lat=${lat}&lng=${lng}`);
}

async getConstituency(id: string): Promise<Constituency> {
  return this.get(`/api/v1/constituencies/${id}`);
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/lib/api/client.ts
git commit -m "feat: add constituency API client methods"
```

---

### Task 8: ConstituencySelector Component

**Covers:** [S3]

**Files:**
- Create: `frontend/src/components/ConstituencySelector.tsx`

**Interfaces:**
- Consumes: `searchConstituencies()`, `lookupConstituencyByGPS()` (Task 7)
- Produces: `<ConstituencySelector value={...} onChange={...} />`

- [ ] **Step 1: Create component**

```tsx
// frontend/src/components/ConstituencySelector.tsx
"use client";

import { useState, useEffect, useRef } from "react";
import { apiClient, type Constituency } from "@/lib/api/client";

interface ConstituencySelectorProps {
  value?: Constituency | null;
  onChange: (constituency: Constituency | null) => void;
  placeholder?: string;
}

export function ConstituencySelector({
  value,
  onChange,
  placeholder = "Search constituency...",
}: ConstituencySelectorProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Constituency[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGeolocating, setIsGeolocating] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.length >= 2) {
        setIsLoading(true);
        try {
          const response = await apiClient.searchConstituencies({ q: query, limit: 10 });
          setResults(response.constituencies);
          setIsOpen(true);
        } catch {
          setResults([]);
        } finally {
          setIsLoading(false);
        }
      } else {
        setResults([]);
        setIsOpen(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (constituency: Constituency) => {
    onChange(constituency);
    setQuery(constituency.name);
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange(null);
    setQuery("");
    setResults([]);
  };

  const handleGeolocate = async () => {
    if (!navigator.geolocation) return;
    setIsGeolocating(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const response = await apiClient.lookupConstituencyByGPS(
            position.coords.latitude,
            position.coords.longitude
          );
          if (response.found && response.constituency) {
            handleSelect(response.constituency);
          }
        } finally {
          setIsGeolocating(false);
        }
      },
      () => setIsGeolocating(false)
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setIsOpen(false);
      inputRef.current?.blur();
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={value ? value.name : query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (value) onChange(null);
          }}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={!!value}
        />
        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="px-3 py-2 text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        )}
        <button
          type="button"
          onClick={handleGeolocate}
          disabled={isGeolocating}
          className="px-3 py-2 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 disabled:opacity-50"
          title="Use my location"
        >
          {isGeolocating ? "..." : "GPS"}
        </button>
      </div>

      {isOpen && results.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
          {results.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => handleSelect(c)}
              className="w-full px-4 py-2 text-left hover:bg-gray-100 flex justify-between items-center"
            >
              <div>
                <div className="font-medium">{c.name}</div>
                <div className="text-sm text-gray-500">
                  {c.district ? `${c.district}, ` : ""}{c.state}
                </div>
              </div>
              <span className="text-xs px-2 py-1 bg-gray-100 rounded">
                {c.type === "lok_sabha" ? "LS" : "VS"}
              </span>
            </button>
          ))}
        </div>
      )}

      {isLoading && (
        <div className="absolute right-10 top-2 text-sm text-gray-400">Searching...</div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ConstituencySelector.tsx
git commit -m "feat: add ConstituencySelector component with search and GPS"
```

---

### Task 9: Integrate into Registration Form

**Covers:** [S3]

**Files:**
- Modify: `frontend/src/app/register/page.tsx`

**Interfaces:**
- Consumes: `<ConstituencySelector>` (Task 8)
- Produces: Updated registration form with constituency selector

- [ ] **Step 1: Update registration form**

Replace the free-text constituency input in `register/page.tsx` with:

```tsx
import { ConstituencySelector } from "@/components/ConstituencySelector";

// Replace the constituency text input with:
<div>
  <label className="block text-sm font-medium text-gray-700 mb-1">
    Constituency (optional)
  </label>
  <ConstituencySelector
    value={selectedConstituency}
    onChange={(c) => {
      setSelectedConstituency(c);
      setFormData((prev) => ({ ...prev, constituency: c?.name || "" }));
    }}
  />
</div>
```

Add state: `const [selectedConstituency, setSelectedConstituency] = useState<Constituency | null>(null);`

- [ ] **Step 2: Verify page loads**

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000/register` and verify the constituency selector appears.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/register/page.tsx
git commit -m "feat: integrate ConstituencySelector into registration form"
```

---

### Task 10: Integrate into MP Dashboard

**Covers:** [S3]

**Files:**
- Modify: `frontend/src/app/mp/page.tsx`

**Interfaces:**
- Consumes: `<ConstituencySelector>` (Task 8)
- Produces: MP dashboard with constituency filter

- [ ] **Step 1: Add constituency filter to dashboard**

Add a constituency filter bar at the top of the MP dashboard page:

```tsx
import { ConstituencySelector } from "@/components/ConstituencySelector";

// Add filter state and selector to the dashboard
const [selectedConstituency, setSelectedConstituency] = useState<Constituency | null>(null);

// Pass selectedConstituency.id as query param to API calls
```

- [ ] **Step 2: Verify filter works**

Navigate to `/mp` and verify the constituency filter appears and can be used to filter dashboard data.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/mp/page.tsx
git commit -m "feat: add constituency filter to MP dashboard"
```

---

### Task 11: Seed Data Script

**Covers:** [S4]

**Files:**
- Create: `backend/scripts/seed_constituencies.py`

**Interfaces:**
- Consumes: `Constituency` model (Task 1)
- Produces: Populated `constituencies` table

- [ ] **Step 1: Create seed script**

```python
# backend/scripts/seed_constituencies.py
"""
Seed constituencies table with Indian parliamentary constituency data.

Usage:
    python -m scripts.seed_constituencies --geojson path/to/constituencies.geojson

GeoJSON format: FeatureCollection with Properties containing:
    - name: constituency name
    - state: state name
    - district: district name
    - type: "lok_sabha" or "vidhan_sabha"
    - ac_number: assembly constituency number (optional)
    - pc_number: parliamentary constituency number (optional)
"""
import argparse
import json
import asyncio
from pathlib import Path

from geoalchemy2.elements import WKTElement
from shapely.geometry import shape

from app.database.session import async_session
from app.database.models.constituency import Constituency


async def seed_from_geojson(geojson_path: str):
    with open(geojson_path) as f:
        data = json.load(f)

    features = data.get("features", [])
    print(f"Seeding {len(features)} constituencies from {geojson_path}")

    async with async_session() as session:
        count = 0
        for feature in features:
            props = feature.get("properties", {})
            geometry = feature.get("geometry")

            if not geometry:
                continue

            # Compute centroid
            shapely_geom = shape(geometry)
            centroid = shapely_geom.centroid

            constituency = Constituency(
                name=props.get("name", "Unknown"),
                state=props.get("state", "Unknown"),
                district=props.get("district"),
                type=props.get("type", "lok_sabha"),
                ac_number=props.get("ac_number"),
                pc_number=props.get("pc_number"),
                centroid_lat=centroid.y,
                centroid_lng=centroid.x,
                geom=WKTElement(shapely_geom.wkt, srid=4326),
            )
            session.add(constituency)
            count += 1

            if count % 100 == 0:
                print(f"  Progress: {count}/{len(features)}")

        await session.commit()
        print(f"Seeded {count} constituencies successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed constituencies from GeoJSON")
    parser.add_argument("--geojson", required=True, help="Path to GeoJSON file")
    args = parser.parse_args()
    asyncio.run(seed_from_geojson(args.geojson))
```

- [ ] **Step 2: Verify script runs (dry run)**

```bash
cd backend
python -c "from scripts.seed_constituencies import seed_from_geojson; print('Import OK')"
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add backend/scripts/seed_constituencies.py
git commit -m "feat: add constituency seeding script"
```

---

## Verification

After completing all tasks:

1. Run backend tests: `cd backend && pytest tests/api/v1/test_constituencies.py tests/infrastructure/test_constituency_repository.py -v`
2. Run frontend type check: `cd frontend && npx tsc --noEmit`
3. Start both servers and test:
   - Visit `http://localhost:3000/register` — verify constituency selector works
   - Visit `http://localhost:8000/api/v1/constituencies?q=Mumbai` — verify search returns results
   - Visit `http://localhost:8000/api/v1/constituencies/lookup?lat=19.076&lng=72.8777` — verify GPS lookup
4. Seed constituency data: `cd backend && python -m scripts.seed_constituencies --geojson path/to/data.geojson`
5. Re-test with real data
