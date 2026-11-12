-- ====================================================================
-- EcoSmart Campus - Base de données PostgreSQL & TimescaleDB
-- Sprint 1 - T05 : Référentiel, hypertable des mesures et données initiales
-- ====================================================================

-- 1. Extension TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 2. Référentiel : Bâtiments
CREATE TABLE IF NOT EXISTS batiments (
    id VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    zone VARCHAR(100) NOT NULL,
    surface DOUBLE PRECISION NOT NULL,
    coordonnees JSONB DEFAULT '{"lat": 48.8566, "lng": 2.3522}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Référentiel : Salles
CREATE TABLE IF NOT EXISTS salles (
    id VARCHAR(50) PRIMARY KEY,
    batiment_id VARCHAR(50) NOT NULL REFERENCES batiments(id) ON DELETE CASCADE,
    nom VARCHAR(100) NOT NULL,
    capacite INT NOT NULL DEFAULT 30,
    usage VARCHAR(100) NOT NULL, -- 'cours', 'tp_informatique', 'labo_recherche', 'amphi', 'administration'
    etage INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Référentiel : Capteurs
CREATE TABLE IF NOT EXISTS capteurs (
    id VARCHAR(100) PRIMARY KEY,
    salle_id VARCHAR(50) NOT NULL REFERENCES salles(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'energie', 'eau', 'dechets', 'co2', 'temperature', 'occupation'
    unite VARCHAR(20) NOT NULL, -- 'kWh', 'm3', '%', 'ppm', '°C', 'personnes'
    etat VARCHAR(20) NOT NULL DEFAULT 'actif', -- 'actif', 'inactif', 'panne'
    derniere_mesure DOUBLE PRECISION,
    derniere_mesure_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index sur type et salle
CREATE INDEX IF NOT EXISTS idx_capteurs_type ON capteurs(type);
CREATE INDEX IF NOT EXISTS idx_capteurs_salle ON capteurs(salle_id);

-- 5. Mesures (Hypertable TimescaleDB)
CREATE TABLE IF NOT EXISTS mesures (
    horodatage TIMESTAMPTZ NOT NULL,
    capteur_id VARCHAR(100) NOT NULL,
    valeur DOUBLE PRECISION NOT NULL
);

-- Création de l'hypertable sur la dimension temporelle
SELECT create_hypertable('mesures', 'horodatage', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_mesures_capteur_horodatage ON mesures(capteur_id, horodatage DESC);

-- 6. Règles d'alertes
CREATE TABLE IF NOT EXISTS regles (
    id SERIAL PRIMARY KEY,
    type_capteur VARCHAR(50) NOT NULL,
    operateur VARCHAR(10) NOT NULL, -- '>', '<', '>=', '<=', '=='
    seuil DOUBLE PRECISION NOT NULL,
    duree_min INT NOT NULL DEFAULT 60, -- en secondes
    gravite VARCHAR(20) NOT NULL DEFAULT 'moyenne', -- 'faible', 'moyenne', 'critique'
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Alertes
CREATE TABLE IF NOT EXISTS alertes (
    id SERIAL PRIMARY KEY,
    capteur_id VARCHAR(100) NOT NULL REFERENCES capteurs(id) ON DELETE CASCADE,
    regle_id INT REFERENCES regles(id) ON DELETE SET NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'regle', -- 'regle', 'ia'
    gravite VARCHAR(20) NOT NULL DEFAULT 'moyenne',
    statut VARCHAR(30) NOT NULL DEFAULT 'ouverte', -- 'ouverte', 'acquittee', 'en_intervention', 'resolue', 'fausse_alarme'
    valeur_declenchement DOUBLE PRECISION,
    message TEXT,
    ouverte_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    close_le TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alertes_statut ON alertes(statut);
CREATE INDEX IF NOT EXISTS idx_alertes_capteur ON alertes(capteur_id);

-- 8. Utilisateurs & Authentification (Sprint 1 - T03)
CREATE TABLE IF NOT EXISTS utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'gestionnaire', 'technicien', 'etudiant', 'direction'
    batiment_id VARCHAR(50) REFERENCES batiments(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_utilisateurs_email ON utilisateurs(email);

-- 9. Interventions
CREATE TABLE IF NOT EXISTS interventions (
    id SERIAL PRIMARY KEY,
    alerte_id INT NOT NULL REFERENCES alertes(id) ON DELETE CASCADE,
    technicien_id INT REFERENCES utilisateurs(id) ON DELETE SET NULL,
    description TEXT,
    statut VARCHAR(30) NOT NULL DEFAULT 'a_faire', -- 'a_faire', 'en_cours', 'terminee', 'annulee'
    creee_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    close_le TIMESTAMPTZ
);

-- 10. Défis & Gamification (Éco-score)
CREATE TABLE IF NOT EXISTS defis (
    id SERIAL PRIMARY KEY,
    batiment_id VARCHAR(50) REFERENCES batiments(id) ON DELETE CASCADE,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    debut TIMESTAMPTZ NOT NULL,
    fin TIMESTAMPTZ NOT NULL,
    indicateur VARCHAR(50) NOT NULL, -- 'reduction_energie', 'tri_dechets', 'extinction_veille'
    points_recompense INT NOT NULL DEFAULT 50
);

CREATE TABLE IF NOT EXISTS participations (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    defi_id INT NOT NULL REFERENCES defis(id) ON DELETE CASCADE,
    points INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (utilisateur_id, defi_id)
);

-- 11. Objectifs de Direction
CREATE TABLE IF NOT EXISTS objectifs (
    id SERIAL PRIMARY KEY,
    batiment_id VARCHAR(50) REFERENCES batiments(id) ON DELETE CASCADE,
    indicateur VARCHAR(50) NOT NULL, -- 'consommation_kwh', 'taux_recyclage', 'fuite_eau_max'
    valeur_cible DOUBLE PRECISION NOT NULL,
    mois VARCHAR(7) NOT NULL -- Format YYYY-MM
);

-- 12. Tournées de collecte des déchets
CREATE TABLE IF NOT EXISTS tournees (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    ordre_bacs JSONB NOT NULL DEFAULT '[]'::jsonb,
    distance DOUBLE PRECISION,
    statut VARCHAR(30) NOT NULL DEFAULT 'planifiee'
);

-- 13. Échanges Assistant EcoSmart (Sprint 1 - T09 / RNF5)
CREATE TABLE IF NOT EXISTS echanges_assistant (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT REFERENCES utilisateurs(id) ON DELETE SET NULL,
    question TEXT NOT NULL,
    reponse TEXT NOT NULL,
    outils_appeles JSONB NOT NULL DEFAULT '[]'::jsonb,
    duree_ms INT NOT NULL DEFAULT 0,
    horodatage TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ====================================================================
-- Données de démo initiales (Seed Data)
-- ====================================================================

-- Bâtiments
INSERT INTO batiments (id, nom, zone, surface, coordonnees) VALUES
('bat-a', 'Bâtiment A - Sciences et Technologies', 'Nord', 4500.0, '{"lat": 48.8580, "lng": 2.3510}'::jsonb),
('bat-b', 'Bâtiment B - Enseignement et Amphis', 'Est', 6200.0, '{"lat": 48.8560, "lng": 2.3540}'::jsonb),
('bat-c', 'Bâtiment C - Laboratoires de Recherche', 'Ouest', 3800.0, '{"lat": 48.8590, "lng": 2.3480}'::jsonb),
('bat-d', 'Bâtiment D - Administration & Vie Étudiante', 'Sud', 2900.0, '{"lat": 48.8540, "lng": 2.3500}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- Salles
INSERT INTO salles (id, batiment_id, nom, capacite, usage, etage) VALUES
('salle-a-101', 'bat-a', 'Salle 101 - TP Physique', 35, 'cours', 1),
('salle-a-201', 'bat-a', 'Salle 201 - Labo Électronique', 30, 'labo_recherche', 2),
('salle-b-amphi', 'bat-b', 'Amphithéâtre Turing', 250, 'amphi', 0),
('salle-b-td12', 'bat-b', 'Salle TD 12 - Mathématiques', 40, 'cours', 1),
('salle-c-labo3', 'bat-c', 'Laboratoire Nanotech', 20, 'labo_recherche', 0),
('salle-d-hall', 'bat-d', 'Hall Central & Espace Coworking', 100, 'administration', 0)
ON CONFLICT (id) DO NOTHING;

-- Capteurs principaux (Énergie en priorité pour Sprint 1)
INSERT INTO capteurs (id, salle_id, type, unite, etat) VALUES
('sensor-elec-batA-01', 'salle-a-101', 'energie', 'kWh', 'actif'),
('sensor-elec-batA-02', 'salle-a-201', 'energie', 'kWh', 'actif'),
('sensor-elec-batB-amphi', 'salle-b-amphi', 'energie', 'kWh', 'actif'),
('sensor-elec-batB-td12', 'salle-b-td12', 'energie', 'kWh', 'actif'),
('sensor-elec-batC-labo', 'salle-c-labo3', 'energie', 'kWh', 'actif'),
('sensor-elec-batD-hall', 'salle-d-hall', 'energie', 'kWh', 'actif'),
('sensor-eau-batA-01', 'salle-a-101', 'eau', 'm3', 'actif'),
('sensor-eau-batB-01', 'salle-b-amphi', 'eau', 'm3', 'actif'),
('sensor-dechets-batA-01', 'salle-a-101', 'dechets', '%', 'actif'),
('sensor-temp-batA-101', 'salle-a-101', 'temperature', '°C', 'actif'),
('sensor-co2-batB-amphi', 'salle-b-amphi', 'co2', 'ppm', 'actif'),
('sensor-occup-batB-amphi', 'salle-b-amphi', 'occupation', 'personnes', 'actif')
ON CONFLICT (id) DO NOTHING;

-- Règles par défaut
INSERT INTO regles (type_capteur, operateur, seuil, duree_min, gravite) VALUES
('energie', '>', 50.0, 300, 'moyenne'),
('energie', '>', 80.0, 180, 'critique'),
('eau', '>', 5.0, 600, 'critique'),
('co2', '>', 1200.0, 900, 'moyenne'),
('temperature', '<', 18.0, 1200, 'faible'),
('temperature', '>', 26.0, 1200, 'faible'),
('dechets', '>', 85.0, 300, 'moyenne')
ON CONFLICT DO NOTHING;

-- Utilisateurs avec mots de passe hachés bcrypt (Sprint 1 - T03)
-- Admin123! -> $2b$12$A63OQjvjbciwNwalM0qQyOzXVNAExggt3haCBrF5Z.BZXAafSnAjO
-- Tech123! -> $2b$12$ID4SHAZqJyB1fSuIu.mKUOUwEe7kxD6y1aW1A3OeKufHcSa2DzafS
-- Etudiant123! -> $2b$12$MNals2lMml8CArF6.Z3EE.54wCTrMMKKUNSlu2HW2iRTXw/iUygze
-- Direction123! -> $2b$12$9AeZu0rgFxLDgKXzt3HQMu0tmeSq6hrdFZuAlRpJG59MAu04PdHeq
INSERT INTO utilisateurs (nom, email, mot_de_passe_hash, role, batiment_id) VALUES
('Moussa Mohammed (Gestionnaire)', 'admin@campus.fr', '$2b$12$A63OQjvjbciwNwalM0qQyOzXVNAExggt3haCBrF5Z.BZXAafSnAjO', 'gestionnaire', 'bat-a'),
('Reghioui Mohamed (Technicien)', 'tech@campus.fr', '$2b$12$ID4SHAZqJyB1fSuIu.mKUOUwEe7kxD6y1aW1A3OeKufHcSa2DzafS', 'technicien', 'bat-a'),
('Benomar Youssef (Étudiant)', 'etudiant@campus.fr', '$2b$12$MNals2lMml8CArF6.Z3EE.54wCTrMMKKUNSlu2HW2iRTXw/iUygze', 'etudiant', 'bat-b'),
('Najib Ibrahim (Direction)', 'direction@campus.fr', '$2b$12$9AeZu0rgFxLDgKXzt3HQMu0tmeSq6hrdFZuAlRpJG59MAu04PdHeq', 'direction', 'bat-d')
ON CONFLICT (email) DO NOTHING;
