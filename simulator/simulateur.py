#!/usr/bin/env python3
"""
Simulateur générique de capteurs IoT pour EcoSmart Campus (Sprint 1 - T04 / RNF3).
Lit les profils YAML (horaires, saisonniers, week-ends) et publie les mesures sur MQTT.
Sujet de publication : mesures/{type}/{capteur_id}
"""

import argparse
import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import paho.mqtt.client as mqtt
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger("simulateur")


class SensorSimulator:
    def __init__(
        self,
        profile_path: str,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        dry_run: bool = False
    ):
        self.profile_path = profile_path
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.dry_run = dry_run
        self.running = True
        self.client: Optional[mqtt.Client] = None
        self.profile = self._load_profile(profile_path)

        if not self.dry_run:
            self._setup_mqtt()

    def _load_profile(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Fichier de profil introuvable : {path}")
        with open(path, "r", encoding="utf-8") as f:
            profile = yaml.safe_load(f)
        logger.info(f"Profil chargé : module={profile.get('module')} avec {len(profile.get('capteurs', []))} capteurs")
        return profile

    def _setup_mqtt(self):
        try:
            self.client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"ecosmart-sim-{random.randint(1000, 9999)}"
            )
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            logger.info(f"Connecté au broker MQTT {self.broker_host}:{self.broker_port}")
        except Exception as e:
            logger.warning(f"Impossible de se connecter au broker MQTT ({e}). Bascule en mode dry-run local.")
            self.dry_run = True

    def calculate_value(self, sensor: Dict[str, Any], sim_time: datetime) -> float:
        """Calcule la valeur du capteur selon les courbes horaires, saisonnières et le bruit (RNF3)."""
        month = sim_time.month
        hour = sim_time.hour
        weekday = sim_time.weekday()  # 0=Lundi, ..., 5=Samedi, 6=Dimanche

        # Facteur saisonnier
        saisons = self.profile.get("saisons", {})
        facteur_saison = saisons.get(month, 1.0)

        # Facteur horaire
        horaires = self.profile.get("profil_horaire_semaine", {})
        facteur_heure = horaires.get(hour, 1.0)

        # Facteur week-end
        weekend_factors = self.profile.get("facteur_weekend", {})
        if weekday == 5:  # Samedi
            facteur_weekend = weekend_factors.get("samedi", 0.35)
        elif weekday == 6:  # Dimanche
            facteur_weekend = weekend_factors.get("dimanche", 0.20)
        else:
            facteur_weekend = 1.0

        # Base talon
        talon = sensor.get("puissance_talon_kwh", 10.0)

        # Valeur théorique
        if weekday in (5, 6):
            # Le week-end, l'activité est principalement le talon amorti
            valeur = talon * facteur_saison * (1.0 + (facteur_heure - 1.0) * facteur_weekend)
        else:
            valeur = talon * facteur_saison * facteur_heure

        # Bruit gaussien
        bruit_std = sensor.get("bruit_ecart_type", 0.5)
        valeur += random.gauss(0, bruit_std)

        # Injection ponctuelle d'un pic d'anomalie pour vérifier RNF2
        prob_pic = sensor.get("probabilite_pic_anomalie", 0.0)
        if random.random() < prob_pic:
            amp = sensor.get("amplitude_pic", 25.0)
            valeur += amp
            logger.info(f"[ANOMALIE INJECTÉE] Pic de +{amp} sur le capteur {sensor['id']}")

        return max(0.1, round(valeur, 2))

    def generate_measurements(self, sim_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Génère un cycle complet de mesures pour tous les capteurs du profil."""
        current_time = sim_time or datetime.now(timezone.utc)
        iso_time = current_time.isoformat()
        module = self.profile.get("module", "energie")
        unite = self.profile.get("unite", "kWh")

        messages = []
        for sensor in self.profile.get("capteurs", []):
            valeur = self.calculate_value(sensor, current_time)
            capteur_id = sensor["id"]
            topic = f"mesures/{module}/{capteur_id}"
            payload = {
                "capteur_id": capteur_id,
                "type": module,
                "batiment_id": sensor.get("batiment_id"),
                "salle_id": sensor.get("salle_id"),
                "valeur": valeur,
                "unite": unite,
                "horodatage": iso_time,
            }
            messages.append({"topic": topic, "payload": payload})
        return messages

    def run(self, interval: Optional[float] = None, count: Optional[int] = None):
        """Boucle de publication principale."""
        pub_interval = interval or self.profile.get("frequence_publication_secondes", 5)
        iterations = 0

        logger.info(f"Démarrage de la simulation (intervalle={pub_interval}s, dry_run={self.dry_run})...")

        try:
            while self.running:
                measurements = self.generate_measurements()
                for item in measurements:
                    payload_json = json.dumps(item["payload"])
                    if self.client and not self.dry_run:
                        self.client.publish(item["topic"], payload_json, qos=0)
                    logger.info(f"MQTT PUB [{item['topic']}] : {item['payload']['valeur']} {item['payload']['unite']}")

                iterations += 1
                if count and iterations >= count:
                    logger.info(f"Nombre d'itérations atteint ({count}). Fin de la simulation.")
                    break

                time.sleep(pub_interval)
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur.")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(description="Simulateur générique de capteurs EcoSmart Campus")
    parser.add_argument(
        "--profile",
        default=os.path.join(os.path.dirname(__file__), "profiles", "energie_profile.yaml"),
        help="Chemin vers le fichier de profil YAML"
    )
    parser.add_argument("--broker", default=os.getenv("MQTT_BROKER_HOST", "localhost"), help="Hôte MQTT Mosquitto")
    parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", "1883")), help="Port MQTT")
    parser.add_argument("--interval", type=float, default=None, help="Intervalle entre chaque publication (secondes)")
    parser.add_argument("--count", type=int, default=None, help="Nombre de cycles à exécuter avant de quitter")
    parser.add_argument("--dry-run", action="store_true", help="Afficher les mesures sans se connecter à MQTT")

    args = parser.parse_args()

    simulator = SensorSimulator(
        profile_path=args.profile,
        broker_host=args.broker,
        broker_port=args.port,
        dry_run=args.dry_run
    )

    def sig_handler(sig, frame):
        simulator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    simulator.run(interval=args.interval, count=args.count)


if __name__ == "__main__":
    main()
