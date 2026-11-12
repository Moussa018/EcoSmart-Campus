from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Batiment(Base):
    __tablename__ = "batiments"

    id = Column(String(50), primary_key=True)
    nom = Column(String(150), nullable=False)
    zone = Column(String(100), nullable=False)
    surface = Column(Float, nullable=False)
    coordonnees = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    salles = relationship("Salle", back_populates="batiment", cascade="all, delete-orphan")
    utilisateurs = relationship("Utilisateur", back_populates="batiment")
    defis = relationship("Defi", back_populates="batiment")
    objectifs = relationship("Objectif", back_populates="batiment")


class Salle(Base):
    __tablename__ = "salles"

    id = Column(String(50), primary_key=True)
    batiment_id = Column(String(50), ForeignKey("batiments.id", ondelete="CASCADE"), nullable=False)
    nom = Column(String(100), nullable=False)
    capacite = Column(Integer, default=30, nullable=False)
    usage = Column(String(100), nullable=False)
    etage = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    batiment = relationship("Batiment", back_populates="salles")
    capteurs = relationship("Capteur", back_populates="salle", cascade="all, delete-orphan")


class Capteur(Base):
    __tablename__ = "capteurs"

    id = Column(String(100), primary_key=True)
    salle_id = Column(String(50), ForeignKey("salles.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    unite = Column(String(20), nullable=False)
    etat = Column(String(20), default="actif", nullable=False)
    derniere_mesure = Column(Float, nullable=True)
    derniere_mesure_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    salle = relationship("Salle", back_populates="capteurs")
    alertes = relationship("Alerte", back_populates="capteur")


class Mesure(Base):
    __tablename__ = "mesures"

    # Note : Sur PostgreSQL TimescaleDB, l'hypertable utilise (capteur_id, horodatage)
    horodatage = Column(DateTime(timezone=True), primary_key=True, default=utc_now)
    capteur_id = Column(String(100), primary_key=True, index=True)
    valeur = Column(Float, nullable=False)


class Regle(Base):
    __tablename__ = "regles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_capteur = Column(String(50), nullable=False)
    operateur = Column(String(10), nullable=False)  # '>', '<', '>=', '<=', '=='
    seuil = Column(Float, nullable=False)
    duree_min = Column(Integer, default=60, nullable=False)  # secondes
    gravite = Column(String(20), default="moyenne", nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    alertes = relationship("Alerte", back_populates="regle")


class Alerte(Base):
    __tablename__ = "alertes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capteur_id = Column(String(100), ForeignKey("capteurs.id", ondelete="CASCADE"), nullable=False, index=True)
    regle_id = Column(Integer, ForeignKey("regles.id", ondelete="SET NULL"), nullable=True)
    source = Column(String(20), default="regle", nullable=False)  # 'regle', 'ia'
    gravite = Column(String(20), default="moyenne", nullable=False)
    statut = Column(String(30), default="ouverte", nullable=False, index=True)  # 'ouverte', 'acquittee', 'en_intervention', 'resolue', 'fausse_alarme'
    valeur_declenchement = Column(Float, nullable=True)
    message = Column(Text, nullable=True)
    ouverte_le = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    close_le = Column(DateTime(timezone=True), nullable=True)

    capteur = relationship("Capteur", back_populates="alertes")
    regle = relationship("Regle", back_populates="alertes")
    interventions = relationship("Intervention", back_populates="alerte")


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'gestionnaire', 'technicien', 'etudiant', 'direction'
    batiment_id = Column(String(50), ForeignKey("batiments.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    batiment = relationship("Batiment", back_populates="utilisateurs")
    participations = relationship("Participation", back_populates="utilisateur")
    echanges = relationship("EchangeAssistant", back_populates="utilisateur")


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alerte_id = Column(Integer, ForeignKey("alertes.id", ondelete="CASCADE"), nullable=False)
    technicien_id = Column(Integer, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)
    statut = Column(String(30), default="a_faire", nullable=False)
    creee_le = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    close_le = Column(DateTime(timezone=True), nullable=True)

    alerte = relationship("Alerte", back_populates="interventions")


class Defi(Base):
    __tablename__ = "defis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batiment_id = Column(String(50), ForeignKey("batiments.id", ondelete="CASCADE"), nullable=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    debut = Column(DateTime(timezone=True), nullable=False)
    fin = Column(DateTime(timezone=True), nullable=False)
    indicateur = Column(String(50), nullable=False)
    points_recompense = Column(Integer, default=50, nullable=False)

    batiment = relationship("Batiment", back_populates="defis")
    participations = relationship("Participation", back_populates="defi")


class Participation(Base):
    __tablename__ = "participations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    defi_id = Column(Integer, ForeignKey("defis.id", ondelete="CASCADE"), nullable=False)
    points = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    utilisateur = relationship("Utilisateur", back_populates="participations")
    defi = relationship("Defi", back_populates="participations")


class Objectif(Base):
    __tablename__ = "objectifs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batiment_id = Column(String(50), ForeignKey("batiments.id", ondelete="CASCADE"), nullable=False)
    indicateur = Column(String(50), nullable=False)
    valeur_cible = Column(Float, nullable=False)
    mois = Column(String(7), nullable=False)

    batiment = relationship("Batiment", back_populates="objectifs")


class Tournee(Base):
    __tablename__ = "tournees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    ordre_bacs = Column(JSON, default=list, nullable=False)
    distance = Column(Float, nullable=True)
    statut = Column(String(30), default="planifiee", nullable=False)


class EchangeAssistant(Base):
    __tablename__ = "echanges_assistant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True)
    question = Column(Text, nullable=False)
    reponse = Column(Text, nullable=False)
    outils_appeles = Column(JSON, default=list, nullable=False)
    duree_ms = Column(Integer, default=0, nullable=False)
    horodatage = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    utilisateur = relationship("Utilisateur", back_populates="echanges")
