from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_access_token
from app.db.models import Utilisateur
from app.db.session import get_db

security_scheme = HTTPBearer(auto_error=False)

# Définition des rôles valides du système (RF01 / Cahier des charges 1.1)
ROLES_VALIDES = ["gestionnaire", "technicien", "etudiant", "direction"]


class UserPayload(BaseModel):
    id: Optional[int] = None
    email: str
    nom: Optional[str] = None
    role: str
    batiment_id: Optional[str] = None


# Utilisateurs de démonstration par défaut
MOCK_USERS = {
    "admin@campus.fr": {
        "id": 1,
        "email": "admin@campus.fr",
        "nom": "Moussa Mohammed (Gestionnaire)",
        "role": "gestionnaire",
        "batiment_id": "bat-a"
    },
    "tech@campus.fr": {
        "id": 2,
        "email": "tech@campus.fr",
        "nom": "Reghioui Mohamed (Technicien)",
        "role": "technicien",
        "batiment_id": "bat-a"
    },
    "etudiant@campus.fr": {
        "id": 3,
        "email": "etudiant@campus.fr",
        "nom": "Benomar Youssef (Étudiant)",
        "role": "etudiant",
        "batiment_id": "bat-b"
    },
    "direction@campus.fr": {
        "id": 4,
        "email": "direction@campus.fr",
        "nom": "Najib Ibrahim (Direction)",
        "role": "direction",
        "batiment_id": "bat-d"
    },
}


async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Optional[AsyncSession] = Depends(get_db),
) -> UserPayload:
    """Valide le jeton JWT et extrait l'utilisateur courant (RF01 / RNF4)."""
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: Optional[str] = payload.get("sub")
    role: Optional[str] = payload.get("role")
    if not email or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton malformé",
        )

    # Tentative de récupération depuis la base de données
    if db:
        try:
            stmt = select(Utilisateur).where(Utilisateur.email == email)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                return UserPayload(
                    id=user.id,
                    email=user.email,
                    nom=user.nom,
                    role=user.role,
                    batiment_id=user.batiment_id
                )
        except Exception:
            # Fallback gracieux en mode démo / test
            pass

    # Fallback mock users si la BD n'est pas encore connectée
    if email in MOCK_USERS:
        u = MOCK_USERS[email]
        return UserPayload(
            id=u["id"],
            email=u["email"],
            nom=u["nom"],
            role=u["role"],
            batiment_id=u["batiment_id"]
        )

    return UserPayload(
        id=payload.get("user_id"),
        email=email,
        nom=payload.get("nom", email),
        role=role,
        batiment_id=payload.get("batiment_id")
    )


def require_roles(allowed_roles: List[str]):
    """Vérifie que l'utilisateur possède l'un des rôles requis (RF01 / RBAC)."""
    async def role_checker(current_user: UserPayload = Depends(get_current_user)) -> UserPayload:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôles autorisés: {', '.join(allowed_roles)}. Votre rôle: {current_user.role}",
            )
        return current_user
    return role_checker
