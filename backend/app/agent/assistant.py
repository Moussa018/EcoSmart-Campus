import time
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.tools import get_tools_for_role
from app.config import settings
from app.logger import logger

CONSIGNE_SYSTEME = (
    "Tu es l'assistant intelligent EcoSmart Campus. Tu aides les gestionnaires et la direction "
    "du campus universitaire à piloter la transition écologique et énergétique.\n\n"
    "Règles strictes (Garde-fous RNF9 / Section 2.3) :\n"
    "1. Réponds toujours en français professionnel et clair.\n"
    "2. Ne cite QUE des chiffres et des faits renvoyés par les outils à ta disposition.\n"
    "3. N'invente jamais de valeur. Si une information est absente, indique clairement que la donnée manque.\n"
    "4. Précise le nom des bâtiments et les unités de mesure exactes (ex: kWh, m3).\n"
    "5. Propose une action concrète d'amélioration si une anomalie ou surconsommation est constatée."
)


class EcoSmartAssistant:
    """Assistant EcoSmart LangChain respectant les contraintes du Sprint 1 (T09, RF24, RF25)."""

    def __init__(self, role: str = "gestionnaire"):
        self.role = role
        self.tools = get_tools_for_role(role)
        self.tool_map = {t.name: t for t in self.tools}

    def _execute_mock_or_deterministic(self, question: str) -> Dict[str, Any]:
        """
        Moteur d'exécution déterministe pour tests, CI et mode secours hors-ligne (RNF10).
        Sélectionne et appelle les vrais outils LangChain et formate la réponse.
        """
        tools_called: List[Dict[str, Any]] = []
        q_lower = question.lower()
        response_text = ""

        # Cas 1 : Question sur le classement ou quel bâtiment a le plus consommé
        if any(w in q_lower for w in ["classe", "plus consommé", "consommation", "rang", "qui consomme"]):
            tool = self.tool_map.get("classement_batiments")
            if tool:
                result = tool.invoke({"module": "energie"})
                tools_called.append({
                    "outil": "classement_batiments",
                    "arguments": {"module": "energie"},
                    "resultat": result
                })
                premier = result[0]
                dernier = result[-1]
                response_text = (
                    f"D'après les relevés récents du campus, le bâtiment ayant la plus forte consommation "
                    f"d'énergie est le **{premier['nom']}** ({premier['batiment_id']}) avec "
                    f"**{premier['consommation_kwh']} kWh** (Éco-score : {premier['eco_score']}/100).\n\n"
                    f"En comparaison, le bâtiment le plus sobre est le **{dernier['nom']}** "
                    f"avec **{dernier['consommation_kwh']} kWh** (Éco-score : {dernier['eco_score']}/100).\n\n"
                    f"💡 *Recommandation : Programmer un audit thermique et vérifier la programmation "
                    f"nocturne des équipements dans le {premier['nom']}.*"
                )

        # Cas 2 : Question sur les alertes ou anomalies
        elif any(w in q_lower for w in ["alerte", "incident", "fuite", "anomalie", "problème"]):
            tool = self.tool_map.get("alertes")
            if tool:
                result = tool.invoke({"statut": "ouverte"})
                tools_called.append({
                    "outil": "alertes",
                    "arguments": {"statut": "ouverte"},
                    "resultat": result
                })
                nb_alertes = len(result)
                alertes_str = "\n".join([f"- **{a['capteur_id']}** ({a['batiment_id']}) : {a['message']}" for a in result])
                response_text = (
                    f"Il y a actuellement **{nb_alertes} alerte(s) ouverte(s)** sur le campus :\n\n"
                    f"{alertes_str}\n\n"
                    f"⚠️ *Ces alertes ont été transmises aux équipes techniques.*"
                )

        # Cas 3 : Détails d'un bâtiment
        elif "bâtiment" in q_lower or "bat-" in q_lower:
            bat_id = "bat-a"
            for b in ["bat-a", "bat-b", "bat-c", "bat-d"]:
                if b in q_lower:
                    bat_id = b
                    break
            tool = self.tool_map.get("details_referentiel")
            if tool:
                result = tool.invoke({"type_entite": "batiment", "identifiant": bat_id})
                tools_called.append({
                    "outil": "details_referentiel",
                    "arguments": {"type_entite": "batiment", "identifiant": bat_id},
                    "resultat": result
                })
                response_text = (
                    f"Fiche du bâtiment **{result['nom']}** (Identifiant: {result['id']}) :\n"
                    f"- **Zone** : {result['zone']}\n"
                    f"- **Surface** : {result['surface']} m²\n"
                    f"- **Consommation moyenne** : {result['consommation_moyenne_kwh']} kWh\n"
                    f"- **Éco-score actuel** : {result['eco_score']}/100"
                )

        # Fallback par défaut
        else:
            tool = self.tool_map.get("classement_batiments")
            if tool:
                result = tool.invoke({"module": "energie"})
                tools_called.append({
                    "outil": "classement_batiments",
                    "arguments": {"module": "energie"},
                    "resultat": result
                })
            response_text = (
                "Voici les données d'énergie disponibles sur le campus. Vous pouvez m'interroger sur "
                "le classement des consommations, les détails des bâtiments ou les alertes en cours."
            )

        return {
            "reponse": response_text,
            "outils_appeles": tools_called,
        }

    def invoke(self, question: str) -> Dict[str, Any]:
        """Exécute une requête à l'assistant avec journalisation et mesure de latence."""
        start_time = time.time()
        logger.info(
            f"Question reçue par l'assistant pour le rôle [{self.role}]: '{question}'",
            extra={"extra_data": {"role": self.role, "question": question}}
        )

        model_provider = settings.LLM_MODEL.split(":")[0] if ":" in settings.LLM_MODEL else settings.LLM_MODEL

        # Tentative d'utilisation de LangChain avec un modèle réel si configuré
        if model_provider in ["openai", "ollama"] and settings.OPENAI_API_KEY:
            try:
                # Utilisation de LangChain chat model
                from langchain.chat_models import init_chat_model
                model = init_chat_model(settings.LLM_MODEL, temperature=0)
                model_with_tools = model.bind_tools(self.tools)
                messages = [
                    SystemMessage(content=CONSIGNE_SYSTEME),
                    HumanMessage(content=question)
                ]
                ai_msg = model_with_tools.invoke(messages)
                tools_called: List[Dict[str, Any]] = []

                if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
                    for tc in ai_msg.tool_calls:
                        tool_fn = self.tool_map.get(tc["name"])
                        if tool_fn:
                            res = tool_fn.invoke(tc["args"])
                            tools_called.append({
                                "outil": tc["name"],
                                "arguments": tc["args"],
                                "resultat": res
                            })

                duration_ms = int((time.time() - start_time) * 1000)
                reponse_content = ai_msg.content if isinstance(ai_msg, AIMessage) else str(ai_msg)
                return {
                    "question": question,
                    "reponse": reponse_content or "Analyse effectuée avec succès via les outils.",
                    "outils_appeles": tools_called,
                    "duree_ms": duration_ms,
                    "modele": settings.LLM_MODEL
                }
            except Exception as e:
                logger.warning(f"Fallback sur le moteur déterministe suite à l'erreur LLM : {e}")

        # Moteur autonome / mode secours (RNF10)
        result = self._execute_mock_or_deterministic(question)
        duration_ms = int((time.time() - start_time) * 1000)

        response_payload = {
            "question": question,
            "reponse": result["reponse"],
            "outils_appeles": result["outils_appeles"],
            "duree_ms": duration_ms,
            "modele": settings.LLM_MODEL
        }

        logger.info(
            f"Réponse assistant générée en {duration_ms} ms avec {len(result['outils_appeles'])} outil(s)",
            extra={"extra_data": {
                "duree_ms": duration_ms,
                "outils": [o["outil"] for o in result["outils_appeles"]]
            }}
        )

        return response_payload


def ask_assistant(question: str, role: str = "gestionnaire") -> Dict[str, Any]:
    """Point d'entrée utilitaire pour poser une question à l'assistant."""
    assistant = EcoSmartAssistant(role=role)
    return assistant.invoke(question)
