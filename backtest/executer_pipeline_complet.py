import csv
import time
from pathlib import Path

from collecte.recuperer_transcripts import recuperer_transcription
from analyse.extraire_sentiment import extraire_sentiment
from backtest.evaluer_correlation import evaluer_backtest

TICKERS = ["MSFT"]
TRIMESTRES = ["2025Q1", "2025Q2", "2025Q3"]

FICHIER_RESULTATS = Path("data/resultats/backtest_complet.csv")
FICHIER_RESULTATS.parent.mkdir(parents=True, exist_ok=True)


def executer_pipeline():
    resultats = []

    for ticker in TICKERS:
        for trimestre in TRIMESTRES:
            print(f"\n--- Traitement : {ticker} {trimestre} ---")
            try:
                transcript = recuperer_transcription(ticker, trimestre)
                if not transcript:
                    print(f"Skip : pas de transcription pour {ticker} {trimestre}")
                    continue

                analyse = extraire_sentiment(transcript)
                resultat = evaluer_backtest(analyse)

                resultats.append(resultat)
                print(f"✅ {ticker} {trimestre} : sentiment={resultat.score_sentiment}, "
                      f"rendement_j1={resultat.rendement_j1}%, rendement_j5={resultat.rendement_j5}%")

            except Exception as e:
                print(f"❌ Erreur sur {ticker} {trimestre} : {e}")
                continue

            time.sleep(1)  # respecte la limite Alpha Vantage (1 req/seconde max)

    # Sauvegarde en CSV pour analyse ultérieure
    with open(FICHIER_RESULTATS, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ticker", "trimestre", "score_sentiment", "rendement_j1", "rendement_j5"])
        for r in resultats:
            writer.writerow([r.ticker, r.trimestre, r.score_sentiment, r.rendement_j1, r.rendement_j5])

    print(f"\n{len(resultats)} résultats sauvegardés dans {FICHIER_RESULTATS}")
    return resultats


if __name__ == "__main__":
    executer_pipeline()