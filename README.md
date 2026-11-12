#  EcoSmart Campus - Plateforme IoT & IA

Plateforme intelligente de pilotage énergétique et environnemental pour campus universitaire (PFA 3A).

---

## Livrables du Sprint 1 (Socle & Dérisquage de l'Agent)

| Tâche | Intitulé | Responsable | Statut | Livrables associés |
|---|---|---|---|---|
| **T01** | Atelier de cadrage (OpenAPI, schéma, MQTT, maquettes) | Équipe | ✅ Déjà fait | Document de planification PDF v2 |
| **T02** | Squelette FastAPI, journalisation JSON, Docker Compose, CI | Moussa | ✅ Réalisé | `backend/`, `backend/app/logger.py`, `docker-compose.yml`, `.github/workflows/ci.yml` |
| **T03** | Authentification JWT, rôles RBAC, hachage bcrypt | Moussa | ✅ Réalisé | `backend/app/auth/` (routes, deps, security), tests unitaires |
| **T04** | Simulateur générique (profils YAML horaires/saisonniers) | Reghioui | ✅ Réalisé | `simulator/simulateur.py`, `simulator/profiles/energie_profile.yaml` |
| **T05** | Schéma TimescaleDB (hypertable, référentiel) & Mosquitto | Reghioui | ✅ Réalisé | `database/init.sql`, `mosquitto/config/mosquitto.conf` |
| **T06** | Init React (Vite, MUI, routage) & client OpenAPI factice | Benomar | ✅ Réalisé | `frontend/`, `frontend/src/mocks/apiMock.js` |
| **T07** | Page de connexion & mise en page par rôle | Benomar | ✅ Réalisé | `frontend/src/pages/Login.jsx`, `Layout.jsx`, 4 vues par rôle |
| **T08** | Génération 6 mois historique Énergie & analyse gaspillage | Najib | ✅ Réalisé | `scripts/generate_history.py`, `scripts/analyze_energy_waste.py`, `data/` |
| **T09** | Prototype Agent LangChain (outils typés, test appel d'outils) | Najib | ✅ Réalisé | `backend/app/agent/` (assistant, tools), tests automatisés |

---

##  Comptes de démonstration par rôle

Le mot de passe par défaut est indiqué pour chaque rôle :

| Rôle | Nom | E-mail | Mot de passe | Périmètre & Accès |
|---|---|---|---|---|
| **Gestionnaire** | Moussa Mohammed | `admin@campus.fr` | `Admin123!` | Vue globale, carte, règles, analyse de consommation |
| **Technicien** | Reghioui Mohamed | `tech@campus.fr` | `Tech123!` | Alertes actives, acquittement, interventions |
| **Étudiant** | Benomar Youssef | `etudiant@campus.fr` | `Etudiant123!` | Éco-score du bâtiment, défis éco-citoyens |
| **Direction** | Najib Ibrahim | `direction@campus.fr` | `Direction123!` | Indicateurs stratégiques, objectifs, bilans IA |

---

##  Démarrage rapide

### Option 1 : Lancement avec Docker Compose (Une seule commande)
```bash
docker compose up -d --build
```
- **Frontend React** : http://localhost:5173
- **API FastAPI & Swagger** : http://localhost:8000/docs
- **Broker MQTT Mosquitto** : `localhost:1883` (WebSockets: `localhost:9001`)
- **TimescaleDB** : `localhost:5432` (user: `ecosmart`, pass: `ecosmart_secret`)

### Option 2 : Lancement en local (Développement)

#### 1. Backend FastAPI
```bash
# Dans le dossier backend/
source ../.venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

#### 2. Lancer les tests & contrôles de qualité (CI)
```bash
cd backend
ruff check .
pytest -v
```

#### 3. Simulateur de capteurs Énergie
```bash
python3 simulator/simulateur.py --dry-run --count 5
```

#### 4. Frontend React Vite
```bash
cd frontend
npm install
npm run dev
```

#### 5. Historique & Analyse du gaspillage Énergie (T08)
```bash
python3 scripts/generate_history.py
python3 scripts/analyze_energy_waste.py
```
Le rapport d'analyse est disponible dans [`data/rapport_analyse_energie.md`](data/rapport_analyse_energie.md).
