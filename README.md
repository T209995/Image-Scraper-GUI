# Image-Scraper-GUI
Script pour télécharger les images d'une page web.

# DISCLAIMER : Le script a été crée partiellement avec l'aide de Google Gemini 2.5 Flash

Fonctionnalités
Interface utilisateur intuitive : Construit avec tkinter pour une utilisation facile.

Téléchargement d'images : Extrait et télécharge les images d'une page web.

Sélection de dossier : Permet de choisir le dossier de destination pour les images téléchargées.

Statut en temps réel : Affiche la progression du téléchargement.

Prérequis
Assurez-vous d'avoir Python installé sur votre système.

Dépendances
Ce script utilise des bibliothèques Python standards qui sont généralement incluses avec l'installation de base de Python, donc aucune installation supplémentaire n'est requise.

tkinter : Utilisé pour créer l'interface graphique.

urllib.request : Utilisé pour faire des requêtes HTTP pour les pages web et les images.

re (Expressions régulières) : Utilisé pour extraire les URL d'images du contenu HTML.

os : Utilisé pour les opérations du système de fichiers, comme la création de dossiers.

Comment exécuter le script
Enregistrez le script : Enregistrez le code Python dans un fichier nommé img.py.

Ouvrez un terminal ou une invite de commande : Naviguez jusqu'au répertoire où vous avez enregistré le fichier.

Exécutez le script : Utilisez la commande suivante :

python img.py

Utilisation
Lancez le script.

Dans l'interface graphique qui s'ouvre :

Entrez l'URL de la page web que vous souhaitez scraper.

Cliquez sur le bouton "Browse" pour choisir le dossier où vous souhaitez enregistrer les images.

Cliquez sur "Scrape Images" pour commencer le téléchargement.

La barre de statut affichera la progression. Une boîte de dialogue de confirmation apparaîtra une fois le téléchargement terminé.

Structure du Code
Le script est organisé en une classe ImageScraperGUI qui gère l'interface utilisateur et les fonctionnalités de scraping.

ImageScraperGUI.__init__(self, master): Initialise l'interface utilisateur.

browse_folder(self): Ouvre une boîte de dialogue pour sélectionner un dossier.

scrape_images(self): Méthode principale qui gère la récupération du contenu de l'URL, l'extraction des URL d'images et le téléchargement des images.
