# Exercice 1 - Hello World Flask

## Objectif

Créer une première application Flask simple permettant d'ajouter et d'afficher des films depuis une base de données.

## Prérequis

- Python 3.x installé
- `uv` installé (gestionnaire de paquets Python moderne)
- Connaissance basique de HTML

## Consignes

### 0. Initialisation du projet avec uv

Avant de commencer, initialisez le projet avec uv :

```bash
uv init
```

Puis ajoutez les dépendances nécessaires :

```bash
uv add flask flask-sqlalchemy
```

Synchronisez les dépendances :

```bash
uv sync
```

### 1. Structure du projet

Créez la structure suivante :

```
01 - Hello world/
├── app.py
├── templates/
│   └── index.html
└── README.md
```

### 2. Créer le fichier Flask (app.py)

Votre application doit contenir :

#### Configuration de Flask et SQLAlchemy

- Importer les modules nécessaires : `Flask`, `render_template`, `request`, `redirect`, `url_for` depuis flask
- Importer `SQLAlchemy` depuis flask_sqlalchemy
- Configurer l'application Flask
- Configurer SQLAlchemy avec une base de données SQLite nommée `movies.db`
- Désactiver le tracking des modifications (`SQLALCHEMY_TRACK_MODIFICATIONS = False`)

#### Modèle de données

Créer un modèle `Movie` avec :

- Un champ `id` (entier, clé primaire)
- Un champ `title` (chaîne de caractères, 200 max, non nullable)

#### Route principale

Créer une route `/` qui accepte les méthodes GET et POST :

- **GET** : Récupère tous les films de la base de données et affiche la page
- **POST** : Récupère le titre du film depuis le formulaire, l'ajoute à la base de données, puis redirige vers la page d'accueil

#### Lancement de l'application

- Créer les tables de la base de données au démarrage
- Lancer l'application en mode debug

### 3. Créer le template HTML (templates/index.html)

Votre page HTML doit contenir :

#### Structure de base

- Doctype HTML5
- Une balise `<head>` avec :
  - L'encodage UTF-8
  - Un titre de page approprié
  - Du CSS pour styliser la page (optionnel mais recommandé)

#### Contenu de la page

- Un titre principal (`<h1>`)
- Un formulaire avec :
  - La méthode POST
  - Un champ input de type text avec l'attribut `name="title"`
  - Un placeholder explicite
  - Un bouton de type submit
- Une section d'affichage avec :
  - Un sous-titre (`<h2>`)
  - Une liste non ordonnée (`<ul>`)
  - Utiliser Jinja2 pour boucler sur la variable `movies` et afficher chaque film dans un `<li>`

#### Syntaxe Jinja2

Rappel de la syntaxe de boucle Jinja2 :

```jinja
{% for item in items %}
  {{ item.property }}
{% endfor %}
```

### 4. Lancer l'application

Pour démarrer votre application :

```bash
uv run app.py
```

Accédez ensuite à `http://127.0.0.1:5000` dans votre navigateur.

## Fonctionnalités attendues

✅ La page s'affiche correctement  
✅ Le formulaire permet d'ajouter un film  
✅ Les films ajoutés apparaissent dans la liste  
✅ Les données persistent (rechargez la page, les films sont toujours là)

## Points d'attention

- N'oubliez pas de créer le dossier `templates/` pour vos fichiers HTML
- Utilisez `request.form.get('nom_du_champ')` pour récupérer les données du formulaire
- Pensez à faire un `db.session.add()` puis `db.session.commit()` pour enregistrer en base
- La redirection évite le double envoi de formulaire lors du rafraîchissement de la page
- Le fichier de base de données `movies.db` sera créé automatiquement au premier lancement

## Aide / Codes utiles

### Flask - Imports et Configuration

```python
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nom_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

### SQLAlchemy - Définition d'un modèle

```python
class NomModele(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    champ_texte = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<NomModele {self.champ_texte}>'
```

### SQLAlchemy - Opérations sur la base de données

```python
# Récupérer tous les éléments
elements = NomModele.query.all()

# Créer un nouvel élément
nouvel_element = NomModele(champ_texte="valeur")

# Ajouter et enregistrer en base
db.session.add(nouvel_element)
db.session.commit()

# Créer les tables au démarrage
with app.app_context():
    db.create_all()
```

### Flask - Routes et méthodes HTTP

```python
@app.route('/', methods=['GET', 'POST'])
def nom_fonction():
    if request.method == 'POST':
        # Traiter le formulaire
        valeur = request.form.get('nom_champ')
        # ... faire quelque chose ...
        return redirect(url_for('nom_fonction'))

    # Méthode GET - afficher la page
    return render_template('fichier.html', variable=valeur)
```

### Flask - Lancer l'application

```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

### HTML - Formulaire

```html
<form method="POST">
  <input type="text" name="nom_champ" placeholder="Texte" required />
  <button type="submit">Envoyer</button>
</form>
```

### Jinja2 - Syntaxe de template

```jinja
{# Afficher une variable #}
{{ variable }}

{# Afficher une propriété d'un objet #}
{{ objet.propriete }}

{# Boucle for #}
{% for item in liste %}
    <li>{{ item.propriete }}</li>
{% endfor %}

{# Condition if #}
{% if condition %}
    <p>Vrai</p>
{% else %}
    <p>Faux</p>
{% endif %}
```
