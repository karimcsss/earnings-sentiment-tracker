import json
from pathlib import Path

DOSSIER_CACHE = Path("data/transcripts")
DOSSIER_CACHE.mkdir(parents=True, exist_ok=True)


def chemin_cache(ticker: str, trimestre: str) -> Path:
    return DOSSIER_CACHE / f"{ticker}_{trimestre}.json"


def charger_depuis_cache(ticker: str, trimestre: str) -> dict | None:
    chemin = chemin_cache(ticker, trimestre)
    if chemin.exists():
        return json.loads(chemin.read_text(encoding="utf-8"))
    return None


def sauvegarder_dans_cache(ticker: str, trimestre: str, donnees: dict) -> None:
    chemin = chemin_cache(ticker, trimestre)
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")