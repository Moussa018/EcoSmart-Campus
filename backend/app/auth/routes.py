from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import MOCK_USERS, UserPayload, get_current_user
from app.auth.security import create_access_token, verify_password
from app.db.models import Utilisateur
from app.db.session import get_db
from app.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentification"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPayload


# Hash bcrypt par défaut pour les utilisateurs de démo (Admin123!, Tech123!, Etudiant123!, Direction123!)
DEMO_PASSWORDS = {
    "admin@campus.fr": "Admin123!",
    "tech@campus.fr": "Tech123!",
    "etudiant@campus.fr": "Etudiant123!",
    "direction@campus.fr": "Direction123!",
}


@router.post("/login", response_model=TokenResponse, summary="Connexion et obtention du jeton JWT")
async def login(
    credentials: LoginRequest,
    db: Optional[AsyncSession] = Depends(get_db)
):
    """
    Authentifie l'utilisateur via son email et mot de passe (RF01 / T03).
    Renvoie un jeton JWT contenant le rôle et l'identifiant du campus.
    """
    user_data: Optional[UserPayload] = None
    is_authenticated = False

    # 1. Tentative d'authentification via PostgreSQL
    if db:
        try:
            stmt = select(Utilisateur).where(Utilisateur.email == credentials.email)
            result = await db.execute(stmt)
            user_db = result.scalar_one_or_none()
            if user_db and verify_password(credentials.password, user_db.mot_de_passe_hash):
                is_authenticated = True
                user_data = UserPayload(
                    id=user_db.id,
                    email=user_db.email,
                    nom=user_db.nom,
                    role=user_db.role,
                    batiment_id=user_db.batiment_id
                )
        except Exception as e:
            logger.warning(f"Connexion DB indisponible lors du login: {e}")

    # 2. Fallback pour utilisateurs de démo
    if not is_authenticated and credentials.email in DEMO_PASSWORDS:
        expected_pwd = DEMO_PASSWORDS[credentials.email]
        if credentials.password == expected_pwd:
            is_authenticated = True
            mock_u = MOCK_USERS[credentials.email]
            user_data = UserPayload(
                id=mock_u["id"],
                email=mock_u["email"],
                nom=mock_u["nom"],
                role=mock_u["role"],
                batiment_id=mock_u["batiment_id"]
            )

    if not is_authenticated or not user_data:
        logger.warning(f"Échec de connexion pour l'email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects (email ou mot de passe)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Création du jeton JWT avec les claims
    token_claims = {
        "sub": user_data.email,
        "user_id": user_data.id,
        "role": user_data.role,
        "nom": user_data.nom,
        "batiment_id": user_data.batiment_id
    }
    token = create_access_token(token_claims)

    logger.info(
        f"Connexion réussie pour {user_data.email} avec rôle {user_data.role}",
        extra={"extra_data": {"user_id": user_data.id, "role": user_data.role}}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_data
    )


@router.get("/me", response_model=UserPayload, summary="Informations sur l'utilisateur connecté")
async def get_me(current_user: UserPayload = Depends(get_current_user)):
    """Renvoie le profil de l'utilisateur extrait du jeton JWT."""
    return current_user
