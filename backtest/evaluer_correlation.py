import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

from models.schema import AnalyseSentiment, ResultatBacktest
from collecte.recuperer_dates_earnings import recuperer_dates_earnings


import time

def calculer_rendements(ticker: str, date_publication: str, max_tentatives: int = 3) -> tuple[float, float]:
    """
    Calcule le rendement (%) à J+1 et J+5 après la date de publication des résultats.
    """
    date_pub = datetime.strptime(date_publication, "%Y-%m-%d")
    debut = date_pub - timedelta(days=3)
    fin = date_pub + timedelta(days=10)

    historique = None
    for tentative in range(max_tentatives):
        historique = yf.Ticker(ticker).history(start=debut, end=fin)
        if not historique.empty:
            break
        print(f"Tentative {tentative + 1}/{max_tentatives} échouée pour {ticker}, nouvel essai...")
        time.sleep(2)

    if historique is None or historique.empty:
        raise ValueError(f"Aucune donnée de cours trouvée pour {ticker} autour de {date_publication}")

    # Retirer le fuseau horaire pour pouvoir comparer avec date_pub (naive)
    historique.index = historique.index.tz_localize(None)

    if isinstance(historique.columns, pd.MultiIndex):
        historique.columns = historique.columns.get_level_values(0)

    serie_close = historique["Close"]

    prix_avant = float(serie_close.asof(date_pub))

    date_j1 = date_pub + timedelta(days=1)
    date_j5 = date_pub + timedelta(days=5)
    prix_j1 = float(serie_close.asof(date_j1))
    prix_j5 = float(serie_close.asof(date_j5))

    rendement_j1 = round((prix_j1 - prix_avant) / prix_avant * 100, 2)
    rendement_j5 = round((prix_j5 - prix_avant) / prix_avant * 100, 2)

    return rendement_j1, rendement_j5

def evaluer_backtest(analyse: AnalyseSentiment) -> ResultatBacktest:
    """Lie une analyse de sentiment au rendement boursier réel qui a suivi."""
    dates = recuperer_dates_earnings(analyse.ticker)
    date_publication = dates.get(analyse.trimestre)

    if not date_publication:
        raise ValueError(f"Date de publication introuvable pour {analyse.ticker} {analyse.trimestre}")

    rendement_j1, rendement_j5 = calculer_rendements(analyse.ticker, date_publication)

    return ResultatBacktest(
        ticker=analyse.ticker,
        trimestre=analyse.trimestre,
        score_sentiment=analyse.score_sentiment,
        rendement_j1=rendement_j1,
        rendement_j5=rendement_j5,
    )


if __name__ == "__main__":
    from collecte.recuperer_transcripts import recuperer_transcription
    from analyse.extraire_sentiment import extraire_sentiment

    transcript = recuperer_transcription("AAPL", "2025Q3")
    if transcript:
        analyse = extraire_sentiment(transcript)
        resultat = evaluer_backtest(analyse)
        print(resultat.model_dump_json(indent=2))