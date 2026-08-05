import os
import requests
from dotenv import load_dotenv

from collecte.cache import charger_depuis_cache, sauvegarder_dans_cache

load_dotenv()

CLE_API = os.getenv("ALPHA_VANTAGE_API_KEY")
URL_BASE = "https://www.alphavantage.co/query"


def recuperer_dates_earnings(ticker: str) -> dict[str, str]:
    """
    Récupère l'historique des dates de publication d'earnings pour un ticker.
    Retourne un dict {trimestre_fiscal: date_publication}, ex: {"2025Q3": "2025-07-31"}
    Un seul appel API par ticker (mis en cache), peu importe le nombre de trimestres utilisés.
    """
    cle_cache = f"dates_{ticker}"
    donnees_cache = charger_depuis_cache(ticker, "dates_earnings")
    if donnees_cache:
        print(f"Dates chargées depuis le cache : {ticker}")
        donnees = donnees_cache
    else:
        params = {
            "function": "EARNINGS",
            "symbol": ticker,
            "apikey": CLE_API,
        }
        reponse = requests.get(URL_BASE, params=params)
        reponse.raise_for_status()
        donnees = reponse.json()

        if "quarterlyEarnings" not in donnees:
            print(f"Aucune donnée d'earnings trouvée pour {ticker}")
            if "Information" in donnees:
                print(f"⚠️  {donnees['Information']}")
            return {}

        sauvegarder_dans_cache(ticker, "dates_earnings", donnees)

    mapping = {}
    for entree in donnees["quarterlyEarnings"]:
        fiscal_date = entree["fiscalDateEnding"]  # ex: "2025-06-28"
        date_reportee = entree["reportedDate"]      # ex: "2025-07-31"
        annee, mois, _ = fiscal_date.split("-")
        trimestre_num = (int(mois) - 1) // 3 + 1
        cle_trimestre = f"{annee}Q{trimestre_num}"
        mapping[cle_trimestre] = date_reportee

    return mapping


if __name__ == "__main__":
    dates = recuperer_dates_earnings("AAPL")
    for trimestre, date in list(dates.items())[:5]:
        print(f"{trimestre}: {date}")