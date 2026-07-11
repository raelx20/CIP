from fastapi import APIRouter, HTTPException, status

from app.application.dto.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    from app.infrastructure.database.repositories.user import UserRepository
    from app.database.session import AsyncSessionLocal
    from app.security.authentication import verify_password, create_access_token

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_by_email(request.email)

        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )

        return LoginResponse(
            access_token=access_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                is_active=user.is_active,
                phone=user.phone,
                constituency=user.constituency,
                district=user.district,
                state=user.state,
                created_at=user.created_at,
            ),
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user."""
    from app.infrastructure.database.repositories.user import UserRepository
    from app.database.session import AsyncSessionLocal
    from app.security.authentication import hash_password
    from app.database.models.user import UserRole

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)

        existing = await repo.get_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        try:
            role = UserRole(request.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {request.role}",
            )

        user = await repo.create({
            "email": request.email,
            "hashed_password": hash_password(request.password),
            "full_name": request.full_name,
            "role": role,
            "phone": request.phone,
            "constituency": request.constituency,
            "district": request.district,
            "state": request.state,
        })

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            phone=user.phone,
            constituency=user.constituency,
            district=user.district,
            state=user.state,
            created_at=user.created_at,
        )
