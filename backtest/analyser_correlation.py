import pandas as pd
from scipy import stats
from pathlib import Path

FICHIER_RESULTATS = Path("data/resultats/backtest_complet.csv")


def analyser_correlation():
    """
    Calcule la corrélation de Pearson entre le score de sentiment
    et les rendements boursiers (J+1 et J+5) sur l'ensemble de l'échantillon.
    """
    df = pd.read_csv(FICHIER_RESULTATS)

    print(f"Échantillon : {len(df)} observations sur {df['ticker'].nunique()} entreprises\n")
    print(df.to_string(index=False))
    print()

    # Statistiques descriptives
    print("--- Statistiques descriptives ---")
    print(f"Sentiment : moyenne={df['score_sentiment'].mean():.3f}, écart-type={df['score_sentiment'].std():.3f}")
    print(f"Rendement J+1 : moyenne={df['rendement_j1'].mean():.2f}%, écart-type={df['rendement_j1'].std():.2f}%")
    print(f"Rendement J+5 : moyenne={df['rendement_j5'].mean():.2f}%, écart-type={df['rendement_j5'].std():.2f}%\n")

    # Corrélation de Pearson
    print("--- Corrélation de Pearson (sentiment vs rendement) ---")
    for colonne_rendement in ["rendement_j1", "rendement_j5"]:
        correlation, p_value = stats.pearsonr(df["score_sentiment"], df[colonne_rendement])
        print(f"{colonne_rendement} : r={correlation:.3f}, p-value={p_value:.3f}")

        interpretation = interpreter_correlation(correlation, p_value)
        print(f"  → {interpretation}\n")


def interpreter_correlation(r: float, p_value: float) -> str:
    """Donne une interprétation lisible du résultat statistique."""
    if pd.isna(r) or pd.isna(p_value):
        return "Impossible à calculer : le score de sentiment est constant sur cet échantillon (pas assez de variance)."

    if p_value > 0.05:
        return f"Pas de corrélation statistiquement significative (p={p_value:.3f} > 0.05)."

    force = "faible" if abs(r) < 0.3 else "modérée" if abs(r) < 0.6 else "forte"
    direction = "positive" if r > 0 else "négative"
    return f"Corrélation {direction} {force} et statistiquement significative."


if __name__ == "__main__":
    analyser_correlation()