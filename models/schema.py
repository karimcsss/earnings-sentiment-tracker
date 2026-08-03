from pydantic import BaseModel, Field
from datetime import date
from enum import Enum


class Ton(str, Enum):
    CONFIANT = "confiant"
    PRUDENT = "prudent"
    NEUTRE = "neutre"
    INQUIET = "inquiet"


class ChangementGuidance(str, Enum):
    RELEVEE = "relevee"
    MAINTENUE = "maintenue"
    ABAISSEE = "abaissee"
    NON_MENTIONNEE = "non_mentionnee"


class Intervention(BaseModel):
    """Une prise de parole individuelle dans le call."""
    intervenant: str
    role: str  # ex: "CEO", "CFO", "Analyste"
    texte: str


class Transcription(BaseModel):
    """Une transcription brute d'earnings call, découpée par intervenant."""
    ticker: str
    entreprise: str
    trimestre: str  # ex: "Q3 2025"
    date_publication: date
    interventions: list[Intervention]


class AnalyseSentiment(BaseModel):
    """Sortie structurée de l'analyse LLM sur une transcription."""
    ticker: str
    trimestre: str
    ton_general: Ton
    score_sentiment: float = Field(ge=-1.0, le=1.0, description="De -1 (très négatif) à +1 (très positif)")
    changement_guidance: ChangementGuidance
    phrases_cles: list[str] = Field(description="Extraits illustrant le ton (max 5)")
    langage_couverture: list[str] = Field(
        default_factory=list,
        description="Expressions de prudence type 'nous pensons', 'sous réserve de'"
    )


class ComparaisonTrimestrielle(BaseModel):
    """Résultat du diff entre deux trimestres consécutifs."""
    ticker: str
    trimestre_actuel: str
    trimestre_precedent: str
    variation_score: float  # score_actuel - score_precedent
    changement_significatif: bool


class ResultatBacktest(BaseModel):
    """Lien entre sentiment et rendement boursier."""
    ticker: str
    trimestre: str
    score_sentiment: float
    rendement_j1: float  # rendement à J+1 en %
    rendement_j5: float  # rendement à J+5 en %