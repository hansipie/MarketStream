# MarketStream

Application Python qui streame en temps réel les prix des cryptomonnaies depuis l'API WebSocket de CoinMarketCap. Elle utilise les websockets, le multithreading et les queues pour récupérer et afficher les données de marché.

## Architecture

L'application suit un modèle producteur/consommateur :

- **`streammarket.py`** — Classe `StreamMarket` (producteur) : se connecte au WebSocket `wss://push.coinmarketcap.com`, s'abonne aux mises à jour de prix et alimente une `Queue` avec des données structurées (nom, symbole, timestamp, prix).
- **`app.py`** — Interface web Streamlit (consommateur) : lance le WebSocket dans un thread daemon, poll la queue chaque seconde et affiche les données dans un tableau dynamique.
- **`main_cli.py`** — Interface CLI via Typer (consommateur) : même principe avec affichage dans le terminal et export CSV.

## Installation

```bash
git clone <repository url>
cd MarketStream
uv sync
```

## Utilisation

### Interface web (Streamlit)

```bash
uv run streamlit run app.py
```

### CLI

```bash
uv run python main_cli.py --token "BTC,ETH" --ouputfile output.csv
```

Options CLI :
- `--token` : liste de symboles séparés par des virgules (défaut : `BTC,ETH`)
- `--ouputfile` : chemin du fichier CSV de sortie (défaut : `output.csv`)

## Dépendances

Les dépendances sont gérées avec [uv](https://docs.astral.sh/uv/) via `pyproject.toml` :
- `streamlit` — interface web
- `websockets` — connexion WebSocket
- `pandas` — manipulation des données
- `typer` — interface CLI
- `beautifulsoup4` — scraping des tokens depuis CoinMarketCap
- `requests` — requêtes HTTP pour le scraping

Pour ajouter une dépendance :

```bash
uv add <package>
```

## Licence

Ce projet est sous licence MIT.
