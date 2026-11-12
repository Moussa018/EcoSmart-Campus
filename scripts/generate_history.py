#!/usr/bin/env python3
"""
Générateur de 6 mois d'historique Énergie pour EcoSmart Campus (Sprint 1 - T08 / RF10).
Simule 180 jours de mesures horaires pour l'ensemble des capteurs d'énergie du campus,
avec distinction heures de cours vs nuit/week-end, saisonnalité et gaspillage simulé.
"""

import argparse
import csv
import os
import random
from datetime import datetime, timedelta, timezone

# Bâtiments et leurs capteurs principaux
SENSORS_CONFIG = [
    {
        "capteur_id": "sensor-elec-batA-01",
        "batiment_id": "bat-a",
        "nom": "TGBT Bâtiment A - Amphi & TP",
        "talon_kwh": 8.5,
        "puissance_cours_kwh": 48.0,
        "std_dev": 2.5
    },
    {
        "capteur_id": "sensor-elec-batA-02",
        "batiment_id": "bat-a",
        "nom": "Sous-station Labo Bat A",
        "talon_kwh": 12.0,
        "puissance_cours_kwh": 65.0,
        "std_dev": 3.0
    },
    {
        "capteur_id": "sensor-elec-batB-amphi",
        "batiment_id": "bat-b",
        "nom": "Compteur Amphi Turing Bat B",
        "talon_kwh": 14.5,
        "puissance_cours_kwh": 75.0,
        "std_dev": 4.0
    },
    {
        "capteur_id": "sensor-elec-batB-td12",
        "batiment_id": "bat-b",
        "nom": "Aile Enseignement Bat B",
        "talon_kwh": 9.0,
        "puissance_cours_kwh": 50.0,
        "std_dev": 2.8
    },
    {
        "capteur_id": "sensor-elec-batC-labo",
        "batiment_id": "bat-c",
        "nom": "Laboratoires Recherche Bat C",
        "talon_kwh": 16.0,
        "puissance_cours_kwh": 82.0,
        "std_dev": 4.5
    },
    {
        "capteur_id": "sensor-elec-batD-hall",
        "batiment_id": "bat-d",
        "nom": "Administration Bat D",
        "talon_kwh": 5.5,
        "puissance_cours_kwh": 28.0,
        "std_dev": 1.8
    }
]

# Facteur saisonnier moyen par mois (Janvier à Décembre)
FACTEURS_MOIS = {
    1: 1.40, 2: 1.35, 3: 1.15, 4: 0.95, 5: 0.85, 6: 0.75,
    7: 0.45, 8: 0.40, 9: 1.05, 10: 1.15, 11: 1.30, 12: 1.45
}


def generate_history(days: int = 180, output_path: str = "data/historique_energie_6_mois.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    end_date = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days)

    total_rows = 0
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["horodatage", "capteur_id", "batiment_id", "valeur_kwh", "est_heure_cours", "est_weekend", "anomalie_injectee"])

        current_dt = start_date
        one_hour = timedelta(hours=1)

        while current_dt <= end_date:
            hour = current_dt.hour
            weekday = current_dt.weekday()  # 0=Lundi, ..., 5=Samedi, 6=Dimanche
            is_weekend = weekday in (5, 6)
            is_course_hours = (not is_weekend) and (8 <= hour <= 18)

            saison_coeff = FACTEURS_MOIS.get(current_dt.month, 1.0)

            for cfg in SENSORS_CONFIG:
                talon = cfg["talon_kwh"] * saison_coeff
                max_cours = cfg["puissance_cours_kwh"] * saison_coeff

                anomalie_injectee = False
                if is_course_hours:
                    # Variation cours : pic 10h-12h et 14h-16h
                    if hour in (10, 11, 14, 15):
                        base_val = max_cours * random.uniform(0.9, 1.05)
                    elif hour in (12, 13):
                        base_val = max_cours * 0.70  # pause midi
                    else:
                        base_val = max_cours * random.uniform(0.75, 0.85)
                else:
                    # Période hors cours (nuit ou week-end)
                    base_val = talon * (1.1 if is_weekend else 1.0)

                    # Injection de gaspillage / anomalies réalistes :
                    # 1. Éclairage/matériel resté allumé la nuit (probabilité 4%)
                    if random.random() < 0.04 and not is_weekend:
                        base_val += random.uniform(15.0, 30.0)
                        anomalie_injectee = True
                    # 2. Climatisation ou chauffage non coupé le week-end (probabilité 3%)
                    elif random.random() < 0.03 and is_weekend:
                        base_val += random.uniform(20.0, 45.0)
                        anomalie_injectee = True

                # Bruit aléatoire
                valeur = max(0.5, round(base_val + random.gauss(0, cfg["std_dev"]), 2))

                writer.writerow([
                    current_dt.isoformat(),
                    cfg["capteur_id"],
                    cfg["batiment_id"],
                    valeur,
                    1 if is_course_hours else 0,
                    1 if is_weekend else 0,
                    1 if anomalie_injectee else 0
                ])
                total_rows += 1

            current_dt += one_hour

    print(f"✅ Historique généré avec succès : {total_rows} mesures enregistrées dans {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Générateur de 6 mois d'historique Énergie (T08)")
    parser.add_argument("--days", type=int, default=180, help="Nombre de jours d'historique (défaut : 180)")
    parser.add_argument("--output", default="data/historique_energie_6_mois.csv", help="Chemin de sortie du fichier CSV")
    args = parser.parse_args()

    generate_history(days=args.days, output_path=args.output)


if __name__ == "__main__":
    main()
