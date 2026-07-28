# Image-Scraper-GUI
Script pour télécharger les images d'une page web via une interface graphique simple.

> DISCLAIMER : Le script a été créé partiellement avec l'aide de Google Gemini 2.5 Flash

## Résumé des fonctionnalités

- Interface graphique basée sur tkinter pour une utilisation simple et rapide.
- Extraction et téléchargement des images référencées sur une page web.
- Support des attributs modernes d'images : `src`, `data-src` et `srcset` (le premier candidat de `srcset` est choisi).
- Requêtes résilientes : la session HTTP utilise une stratégie de retry pour gérer les erreurs transitoires réseau.
- Annulation propre : bouton "Cancel" pour interrompre le téléchargement en cours et supprimer les fichiers partiels.
- Progression en temps réel : barre de progression et étiquettes de statut mises à jour pendant le téléchargement.
- Nommage sûr des fichiers : les noms sont nettoyés des caractères invalides et les collisions sont évitées en ajoutant un suffixe numérique.
- Détection d'extension : si le nom de fichier n'inclut pas d'extension, l'extension est devinée à partir de l'en-tête `Content-Type` de la réponse HTTP.
- Téléchargement en streaming pour limiter l'utilisation de la mémoire.
- Journalisation via le module `logging` pour obtenir des informations et les erreurs dans la console.

## Prérequis

- Python 3 (idéalement 3.7+)

## Dépendances

Le script utilise des bibliothèques externes :

- requests
- beautifulsoup4

Installez-les avec :

```
pip install requests beautifulsoup4
```

Note : `tkinter` est généralement inclus avec Python sur la plupart des plateformes. Sur certaines distributions Linux, vous devrez peut-être installer le paquet système `python3-tk` ou équivalent.

## Fichier principal

- `img.py` — application principale. Contient la classe `ImageScraperGUI` qui gère l'interface et le scraping.

## Comment exécuter

1. Exécutez le script :

```
python img.py
```

2. Dans l'interface :
   - Entrez l'URL de la page à scraper.
   - Cliquez sur "Browse" pour choisir le dossier de destination.
   - Cliquez sur "Scrape Images" pour démarrer le téléchargement.
   - Utilisez "Cancel" pour interrompre l'opération en cours.

## Comportement et limitations

- Les images encodées en data URI (`data:`) sont ignorées.
- Le script ne fait pas de crawling : il ne télécharge que les images présentes dans la page fournie.
- Les erreurs individuelles de téléchargement sont consignées dans la console et un résumé est affiché à la fin.
- Si l'utilisateur annule, les fichiers partiels sont supprimés.

## Fonctions et structure importantes

- `make_session(retries=..., backoff_factor=..., status_forcelist=...)` : crée une session `requests` avec stratégie de retry et entêtes (User-Agent).
- `sanitize_filename(name: str) -> str` : nettoie une chaîne pour en faire un nom de fichier sûr.
- `ensure_unique_path(folder: str, filename: str) -> str` : évite d'écraser des fichiers existants en ajoutant un suffixe numérique.
- `extension_from_content_type(content_type: str) -> str` : devine l'extension à partir d'un `Content-Type`.
- `ImageScraperGUI` : classe principale, méthodes clés :
  - `browse_folder(self)`
  - `start_scrape(self)`
  - `_scrape_thread(self, url, save_folder)`
  - `_extract_image_urls(self, soup, base_url)`
  - `_download_image(self, session, img_url, save_folder)`

## Remarques sur la sécurité et l'usage responsable

- Respectez les conditions d'utilisation et le `robots.txt` des sites web que vous scrappez.
- Ne téléchargez pas de contenu protégé par des droits d'auteur sans autorisation.

## Remerciements

Ce projet a été démarré avec une aide partielle fournie par un assistant IA.
