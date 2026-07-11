from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.citizen.router import router as citizen_router
from app.api.v1.mp.router import router as mp_router
from app.api.v1.admin.router import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(citizen_router, prefix="/citizen", tags=["Citizen"])
api_router.include_router(mp_router, prefix="/mp", tags=["MP & Associates"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
