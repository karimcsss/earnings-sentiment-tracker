import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

FICHIER_RESULTATS = Path("data/resultats/backtest_complet.csv")
FICHIER_GRAPHIQUE = Path("data/resultats/sentiment_vs_rendement.png")


def generer_graphique():
    df = pd.read_csv(FICHIER_RESULTATS)

    fig, ax = plt.subplots(figsize=(9, 6))

    couleurs = {"AAPL": "#1f77b4", "MSFT": "#2ca02c", "GOOGL": "#d62728"}

    for ticker in df["ticker"].unique():
        sous_ensemble = df[df["ticker"] == ticker]
        ax.scatter(
            sous_ensemble["score_sentiment"],
            sous_ensemble["rendement_j5"],
            label=ticker,
            color=couleurs.get(ticker, "gray"),
            s=120,
            alpha=0.8,
            edgecolors="black",
        )
        # Annoter chaque point avec le trimestre
        for _, ligne in sous_ensemble.iterrows():
            ax.annotate(
                ligne["trimestre"],
                (ligne["score_sentiment"], ligne["rendement_j5"]),
                textcoords="offset points",
                xytext=(8, 5),
                fontsize=8,
            )

    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Score de sentiment (extrait par IA)", fontsize=11)
    ax.set_ylabel("Rendement à J+5 (%)", fontsize=11)
    ax.set_title("Sentiment des earnings calls vs rendement boursier (J+5)", fontsize=13, fontweight="bold")
    ax.legend(title="Entreprise")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FICHIER_GRAPHIQUE, dpi=150)
    print(f"Graphique sauvegardé : {FICHIER_GRAPHIQUE}")
    plt.show()


if __name__ == "__main__":
    generer_graphique()