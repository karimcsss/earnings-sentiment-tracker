import os
import requests
from datetime import datetime
from dotenv import load_dotenv

from models.schema import Transcription, Intervention

load_dotenv()

CLE_API = os.getenv("ALPHA_VANTAGE_API_KEY")
URL_BASE = "https://www.alphavantage.co/query"


def recuperer_transcription(ticker: str, trimestre: str) -> Transcription | None:
    """
    Récupère la transcription d'un earnings call via Alpha Vantage.

    ticker: ex. "AAPL"
    trimestre: ex. "2025Q3" (format attendu par Alpha Vantage)
    """
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
        return None

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
        date_publication=datetime.now().date(),  # à affiner : Alpha Vantage ne renvoie pas toujours la date exacte
        interventions=interventions,
    )


if __name__ == "__main__":
    resultat = recuperer_transcription("AAPL", "2025Q3")
    if resultat:
        print(f"{resultat.entreprise} — {resultat.trimestre}")
        print(f"Nombre d'interventions : {len(resultat.interventions)}")
        print(resultat.interventions[0].texte[:300])