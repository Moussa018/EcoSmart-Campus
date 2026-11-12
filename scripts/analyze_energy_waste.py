#!/usr/bin/env python3
"""
Analyse des pics de consommation et du gaspillage d'énergie hors heures de cours (Sprint 1 - T08 / RF10).
Lit le jeu de données de 6 mois et produit un bilan d'analyse chiffré.
"""

import argparse
import json
import os
import pandas as pd


def analyze_energy(input_csv: str = "data/historique_energie_6_mois.csv"):
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Fichier introuvable : {input_csv}. Exécutez d'abord generate_history.py.")

    df = pd.read_csv(input_csv)
    df["horodatage"] = pd.to_datetime(df["horodatage"])

    total_kwh = df["valeur_kwh"].sum()
    nb_mesures = len(df)

    # 1. Répartition Heures de cours vs Hors heures de cours
    cours_df = df[df["est_heure_cours"] == 1]
    hors_cours_df = df[df["est_heure_cours"] == 0]

    kwh_cours = cours_df["valeur_kwh"].sum()
    kwh_hors_cours = hors_cours_df["valeur_kwh"].sum()

    pct_cours = round((kwh_cours / total_kwh) * 100, 2)
    pct_hors_cours = round((kwh_hors_cours / total_kwh) * 100, 2)

    # 2. Analyse des Pics de consommation
    top_pics = df.sort_values(by="valeur_kwh", ascending=False).head(10)
    max_pic = top_pics.iloc[0]

    # 3. Consommation par bâtiment
    par_batiment = df.groupby("batiment_id")["valeur_kwh"].agg(["sum", "mean", "max"]).reset_index()
    par_batiment["pct_total"] = (par_batiment["sum"] / total_kwh * 100).round(2)
    par_batiment = par_batiment.sort_values(by="sum", ascending=False)

    # 4. Estimation du gaspillage hors heures de cours
    # Talon théorique moyen = moyenne du décile le plus bas la nuit (entre 2h et 4h)
    talon_reference = df[(df["horodatage"].dt.hour.isin([2, 3, 4])) & (df["est_weekend"] == 0)]["valeur_kwh"].quantile(0.25)
    heures_hors_cours_total = len(hors_cours_df)
    talon_theorique_total = talon_reference * heures_hors_cours_total
    gaspillage_estime_kwh = max(0.0, kwh_hors_cours - talon_theorique_total)
    pct_gaspillage = round((gaspillage_estime_kwh / total_kwh) * 100, 2)

    # Coût de l'énergie (estimé à 0.22 € / kWh moyen pour campus) et facteur carbone (0.055 kg CO2e / kWh)
    prix_kwh = 0.22
    facteur_co2 = 0.055
    economie_euros = round(gaspillage_estime_kwh * prix_kwh, 2)
    economie_co2_kg = round(gaspillage_estime_kwh * facteur_co2, 2)

    resultats = {
        "periode_analyse_jours": 180,
        "nombre_mesures": nb_mesures,
        "consommation_totale_kwh": round(total_kwh, 2),
        "repartition": {
            "heures_de_cours_kwh": round(kwh_cours, 2),
            "heures_de_cours_pct": pct_cours,
            "hors_heures_de_cours_kwh": round(kwh_hors_cours, 2),
            "hors_heures_de_cours_pct": pct_hors_cours,
        },
        "pic_maximal": {
            "valeur_kwh": float(max_pic["valeur_kwh"]),
            "capteur_id": str(max_pic["capteur_id"]),
            "batiment_id": str(max_pic["batiment_id"]),
            "horodatage": str(max_pic["horodatage"]),
        },
        "gaspillage_estime": {
            "gaspillage_kwh": round(gaspillage_estime_kwh, 2),
            "pct_du_total": pct_gaspillage,
            "economies_financieres_estimees_euros": economie_euros,
            "economies_carbone_estimees_kg_co2": economie_co2_kg
        },
        "classement_batiments": [
            {
                "batiment_id": row["batiment_id"],
                "total_kwh": round(row["sum"], 2),
                "moyenne_horaire_kwh": round(row["mean"], 2),
                "pic_kwh": round(row["max"], 2),
                "pct_campus": row["pct_total"]
            }
            for _, row in par_batiment.iterrows()
        ]
    }

    # Sauvegarde JSON
    json_path = "data/analyse_gaspillage_energie.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultats, f, indent=2, ensure_ascii=False)

    # Rédaction du rapport Markdown
    md_path = "data/rapport_analyse_energie.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📊 Rapport d'analyse de l'historique Énergie (Sprint 1 - T08)\n\n")
        f.write(f"- **Période analysée** : 6 mois (180 jours, {nb_mesures} relevés horaires)\n")
        f.write(f"- **Consommation globale** : **{total_kwh:,.2f} kWh**\n\n")
        f.write("## 1. Répartition de la consommation\n\n")
        f.write(f"- **Heures de cours (8h-18h en semaine)** : {kwh_cours:,.2f} kWh ({pct_cours} %)\n")
        f.write(f"- **Hors heures de cours (nuits & week-ends)** : {kwh_hors_cours:,.2f} kWh ({pct_hors_cours} %)\n\n")
        f.write("## 2. Gaspillage détecté et gisement d'économies\n\n")
        f.write(f"- **Volume de gaspillage estimé** : **{gaspillage_estime_kwh:,.2f} kWh** ({pct_gaspillage} % de la consommation totale)\n")
        f.write(f"- **Impact financier direct** : **{economie_euros:,.2f} €** d'économies annuelles potentielles\n")
        f.write(f"- **Réduction d'empreinte carbone** : **{economie_co2_kg:,.2f} kg CO₂e** évités\n\n")
        f.write("## 3. Pic maximal enregistré\n\n")
        f.write(f"- **Valeur de crête** : **{max_pic['valeur_kwh']} kWh**\n")
        f.write(f"- **Bâtiment & Capteur** : {max_pic['batiment_id']} (`{max_pic['capteur_id']}`)\n")
        f.write(f"- **Horodatage** : {max_pic['horodatage']}\n\n")
        f.write("## 4. Consommation par bâtiment\n\n")
        f.write("| Bâtiment | Conso Totale (kWh) | Pic (kWh) | Part du campus (%) |\n")
        f.write("|----------|--------------------|-----------|--------------------|\n")
        for _, row in par_batiment.iterrows():
            f.write(f"| {row['batiment_id']} | {row['sum']:,.2f} | {row['max']:,.2f} | {row['pct_total']} % |\n")
        f.write("\n> *Recommandation : Programmer des règles d'extinction automatique des éclairages et régulation de consigne thermique nocturne pour résorber les surconsommations identifiées.* \n")

    print(f"✅ Analyse terminée : rapports générés dans {json_path} et {md_path}")
    return resultats


def main():
    parser = argparse.ArgumentParser(description="Analyse du gaspillage d'énergie sur 6 mois (T08)")
    parser.add_argument("--input", default="data/historique_energie_6_mois.csv", help="Chemin du fichier CSV d'historique")
    args = parser.parse_args()

    analyze_energy(input_csv=args.input)


if __name__ == "__main__":
    main()
