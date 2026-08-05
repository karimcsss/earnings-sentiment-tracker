import os
import requests
from datetime import datetime
from dotenv import load_dotenv

from models.schema import Transcription, Intervention
from collecte.cache import charger_depuis_cache, sauvegarder_dans_cache

load_dotenv()

CLE_API = os.getenv("ALPHA_VANTAGE_API_KEY")
URL_BASE = "https://www.alphavantage.co/query"


def recuperer_transcription(ticker: str, trimestre: str) -> Transcription | None:
    """
    Récupère la transcription d'un earnings call via Alpha Vantage.
    Vérifie d'abord le cache local pour éviter de consommer le quota inutilement.
    """
    donnees_cache = charger_depuis_cache(ticker, trimestre)
    if donnees_cache:
        print(f"Chargé depuis le cache : {ticker} {trimestre}")
        donnees = donnees_cache
    else:
        params = {
            "function": "EARNINGS_CALL_TRANSCRIPT",
            "symbol": ticker,
            "quarter": trimestre,
            "apikey": CLE_API,
        }

        reponse = requests.get(URL_BASE, params=params)
        reponse.raise_for_status()
        donnees = reponse.json()
        

        if "transcript" not in donnees or not donnees["transcript"]:
            print(f"Aucune transcription trouvée pour {ticker} {trimestre}")
            if "Information" in donnees:
                print(f"⚠️  {donnees['Information']}")
            return None

        sauvegarder_dans_cache(ticker, trimestre, donnees)

    interventions = [
        Intervention(
            intervenant=item.get("speaker", "Inconnu"),
            role=item.get("title", "Non précisé"),
            texte=item.get("content", ""),
        )
        for item in donnees["transcript"]
    ]

    return Transcription(
        ticker=ticker,
        entreprise=donnees.get("symbol", ticker),
        trimestre=trimestre,
        date_publication=datetime.now().date(),
        interventions=interventions,
    )


if __name__ == "__main__":
    resultat = recuperer_transcription("AAPL", "2025Q3")
    if resultat:
        print(f"{resultat.entreprise} — {resultat.trimestre}")
        print(f"Nombre d'interventions : {len(resultat.interventions)}")
        print(resultat.interventions[0].texte[:300])