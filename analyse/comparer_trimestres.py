from models.schema import AnalyseSentiment, ComparaisonTrimestrielle

SEUIL_SIGNIFICATIF = 0.3  # variation de score à partir de laquelle on considère le changement notable


def comparer_trimestres(
    analyse_precedente: AnalyseSentiment,
    analyse_actuelle: AnalyseSentiment,
) -> ComparaisonTrimestrielle:
    """
    Compare deux analyses de sentiment consécutives pour un même ticker
    et calcule la variation du score de sentiment.
    """
    if analyse_precedente.ticker != analyse_actuelle.ticker:
        raise ValueError("Les deux analyses doivent concerner le même ticker.")

    variation = analyse_actuelle.score_sentiment - analyse_precedente.score_sentiment

    return ComparaisonTrimestrielle(
        ticker=analyse_actuelle.ticker,
        trimestre_actuel=analyse_actuelle.trimestre,
        trimestre_precedent=analyse_precedente.trimestre,
        variation_score=round(variation, 3),
        changement_significatif=abs(variation) >= SEUIL_SIGNIFICATIF,
    )


if __name__ == "__main__":
    from collecte.recuperer_transcripts import recuperer_transcription
    from analyse.extraire_sentiment import extraire_sentiment

    # Test sur deux trimestres consécutifs d'Apple
    transcript_q2 = recuperer_transcription("AAPL", "2025Q2")
    transcript_q3 = recuperer_transcription("AAPL", "2025Q3")

    if transcript_q2 and transcript_q3:
        analyse_q2 = extraire_sentiment(transcript_q2)
        analyse_q3 = extraire_sentiment(transcript_q3)

        comparaison = comparer_trimestres(analyse_q2, analyse_q3)
        print(comparaison.model_dump_json(indent=2))