import os
import json
from groq import Groq
from dotenv import load_dotenv

from models.schema import Transcription, AnalyseSentiment, Ton, ChangementGuidance

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODELE = "llama-3.3-70b-versatile"


def construire_texte_transcript(transcription: Transcription, max_interventions: int = 30) -> str:
    """
    Concatène les interventions en texte lisible pour le prompt.
    On limite le nombre d'interventions pour rester dans un contexte raisonnable
    et privilégier les remarques préparées (CEO/CFO) en début de call.
    """
    lignes = []
    for interv in transcription.interventions[:max_interventions]:
        lignes.append(f"[{interv.role} - {interv.intervenant}]: {interv.texte}")
    return "\n\n".join(lignes)


def construire_prompt(transcription: Transcription, texte: str) -> str:
    return f"""Tu es un analyste financier expert. Analyse cette transcription d'earnings call
pour {transcription.entreprise} ({transcription.ticker}), {transcription.trimestre}.

TRANSCRIPTION :
{texte}

Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ou après, respectant exactement ce format :

{{
  "ton_general": "confiant" | "prudent" | "neutre" | "inquiet",
  "score_sentiment": <float entre -1.0 et 1.0>,
  "changement_guidance": "relevee" | "maintenue" | "abaissee" | "non_mentionnee",
  "phrases_cles": ["phrase 1", "phrase 2", ...] (maximum 5, extraites du texte, illustrant le ton),
  "langage_couverture": ["expression 1", "expression 2", ...] (expressions de prudence type "nous pensons", "sous réserve de", peut être vide)
}}

Sois rigoureux : le score_sentiment doit refléter finement les nuances, pas seulement du positif/négatif binaire.
"""


def extraire_sentiment(transcription: Transcription) -> AnalyseSentiment:
    """Envoie la transcription à Groq et retourne une AnalyseSentiment validée."""
    texte = construire_texte_transcript(transcription)
    prompt = construire_prompt(transcription, texte)

    reponse = client.chat.completions.create(
        model=MODELE,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,  # faible température : on veut de la cohérence, pas de la créativité
    )

    contenu_brut = reponse.choices[0].message.content
    donnees = json.loads(contenu_brut)

    return AnalyseSentiment(
        ticker=transcription.ticker,
        trimestre=transcription.trimestre,
        ton_general=Ton(donnees["ton_general"]),
        score_sentiment=donnees["score_sentiment"],
        changement_guidance=ChangementGuidance(donnees["changement_guidance"]),
        phrases_cles=donnees.get("phrases_cles", []),
        langage_couverture=donnees.get("langage_couverture", []),
    )


if __name__ == "__main__":
    from collecte.recuperer_transcripts import recuperer_transcription

    transcript = recuperer_transcription("AAPL", "2025Q3")
    if transcript:
        analyse = extraire_sentiment(transcript)
        print(analyse.model_dump_json(indent=2))