/**
 * Client d'API et Données factices générées depuis le contrat OpenAPI (T01 / T06).
 * Permet au frontend de fonctionner de manière totalement autonome (mock)
 * ou connectée au backend FastAPI (/api/v1).
 */

export const MOCK_BUILDINGS = [
  {
    id: "bat-a",
    nom: "Bâtiment A - Sciences et Technologies",
    zone: "Nord",
    surface: 4500.0,
    coordonnees: { lat: 48.8580, lng: 2.3510 },
    consommation_actuelle: 62.4,
    eco_score: 78,
  },
  {
    id: "bat-b",
    nom: "Bâtiment B - Enseignement et Amphis",
    zone: "Est",
    surface: 6200.0,
    coordonnees: { lat: 48.8560, lng: 2.3540 },
    consommation_actuelle: 104.8,
    eco_score: 64,
  },
  {
    id: "bat-c",
    nom: "Bâtiment C - Laboratoires de Recherche",
    zone: "Ouest",
    surface: 3800.0,
    coordonnees: { lat: 48.8590, lng: 2.3480 },
    consommation_actuelle: 115.5,
    eco_score: 58,
  },
  {
    id: "bat-d",
    nom: "Bâtiment D - Administration & Vie Étudiante",
    zone: "Sud",
    surface: 2900.0,
    coordonnees: { lat: 48.8540, lng: 2.3500 },
    consommation_actuelle: 39.9,
    eco_score: 85,
  },
];

export const MOCK_ALERTS = [
  {
    id: 1,
    capteur_id: "sensor-elec-batB-amphi",
    batiment_id: "bat-b",
    batiment_nom: "Bâtiment B - Enseignement",
    type: "energie",
    gravite: "critique",
    statut: "ouverte",
    message: "Pic de puissance sur l'amphithéâtre Turing : 104.8 kW (Seuil max : 80 kW)",
    ouverte_le: "Il y a 12 minutes",
  },
  {
    id: 2,
    capteur_id: "sensor-eau-batA-01",
    batiment_id: "bat-a",
    batiment_nom: "Bâtiment A - Sciences",
    type: "eau",
    gravite: "critique",
    statut: "ouverte",
    message: "Débit nocturne continu suspecté (fuite sanitaire bâtiment A)",
    ouverte_le: "Il y a 45 minutes",
  },
  {
    id: 3,
    capteur_id: "sensor-co2-batB-amphi",
    batiment_id: "bat-b",
    batiment_nom: "Bâtiment B - Enseignement",
    type: "co2",
    gravite: "moyenne",
    statut: "acquittee",
    message: "Niveau de CO2 élevé en amphi : 1320 ppm (> 1200 ppm)",
    ouverte_le: "Il y a 1 heure",
  },
];

export const MOCK_DEFIS = [
  {
    id: 1,
    titre: "Extinction des veilles et projecteurs",
    batiment: "Bâtiment B",
    points: 80,
    participants: 142,
    progression: 75,
    fin: "Dans 3 jours",
  },
  {
    id: 2,
    titre: "Objectif Sobriété Thermique (19°C max)",
    batiment: "Bâtiment A",
    points: 120,
    participants: 230,
    progression: 90,
    fin: "Dans 5 jours",
  },
  {
    id: 3,
    titre: "Zéro gaspillage d'eau",
    batiment: "Tous les bâtiments",
    points: 50,
    participants: 410,
    progression: 60,
    fin: "Dans 1 semaine",
  },
];

export const apiClient = {
  async getBuildings() {
    try {
      const token = localStorage.getItem("ecosmart_token");
      const res = await fetch("/api/v1/referentiel/batiments", {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) return await res.json();
    } catch (_) {}
    return MOCK_BUILDINGS;
  },

  async getAlerts() {
    try {
      const token = localStorage.getItem("ecosmart_token");
      const res = await fetch("/api/v1/alertes", {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) return await res.json();
    } catch (_) {}
    return MOCK_ALERTS;
  },

  async askAssistant(question) {
    try {
      const token = localStorage.getItem("ecosmart_token");
      const res = await fetch("/api/v1/assistant", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ question }),
      });
      if (res.ok) return await res.json();
    } catch (_) {}

    // Mock fallback response
    return {
      question,
      reponse:
        "D'après les relevés factices d'OpenAPI, le bâtiment ayant la plus forte consommation est le **Bâtiment B - Enseignement** avec 104.8 kW actuellement. Le bâtiment le plus sobre est le Bâtiment D avec 39.9 kW.",
      outils_appeles: [{ outil: "classement_batiments", resultat: MOCK_BUILDINGS }],
      duree_ms: 120,
      modele: "mock:openapi-fallback",
    };
  },
};
