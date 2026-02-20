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
uv add flask sqlalchemy
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
- Importer `create_engine`, `Column`, `Integer`, `String` depuis sqlalchemy
- Importer `declarative_base`, `sessionmaker` depuis sqlalchemy.orm
- Configurer l'application Flask
- Créer un engine SQLAlchemy avec une base de données SQLite nommée `movies.db` dans le dossier instance
- Créer une Base déclarative et un sessionmaker

#### Modèle de données

Créer un modèle `Movie` héritant de `Base` avec :

- Un attribut `__tablename__` défini à `"movies"`
- Un champ `id` (Column Integer, clé primaire)
- Un champ `title` (Column String 200, non nullable)

#### Route principale

Créer une route `/` qui accepte les méthodes GET et POST :

- Créer une session SQLAlchemy au début de la fonction
- Utiliser un bloc try/finally pour garantir la fermeture de la session
- **GET** : Récupère tous les films avec `session.query(Movie).all()` et affiche la page
- **POST** : Récupère le titre du film depuis le formulaire, l'ajoute à la session avec `session.add()`, commit, puis redirige vers la page d'accueil

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
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = Flask(__name__)

# Configuration SQLAlchemy
engine = create_engine('sqlite:///instance/nom_base.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
```

### SQLAlchemy - Définition d'un modèle

```python
class NomModele(Base):
    __tablename__ = 'nom_table'

    id = Column(Integer, primary_key=True)
    champ_texte = Column(String(200), nullable=False)

    def __repr__(self):
        return f'<NomModele {self.champ_texte}>'
```

### SQLAlchemy - Opérations sur la base de données

```python
# Créer une session
session = Session()

# Récupérer tous les éléments
elements = session.query(NomModele).all()

# Créer un nouvel élément
nouvel_element = NomModele(champ_texte="valeur")

# Ajouter et enregistrer en base
session.add(nouvel_element)
session.commit()

# Fermer la session
session.close()

# Créer les tables au démarrage
Base.metadata.create_all(engine)
```

### Flask - Routes et méthodes HTTP

```python
@app.route('/', methods=['GET', 'POST'])
def nom_fonction():
    session = Session()
    try:
        if request.method == 'POST':
            # Traiter le formulaire
            valeur = request.form.get('nom_champ')
            # ... faire quelque chose ...
            session.commit()
            return redirect(url_for('nom_fonction'))

        # Méthode GET - afficher la page
        return render_template('fichier.html', variable=valeur)
    finally:
        session.close()
```

### Flask - Lancer l'application

```python
if __name__ == '__main__':
    Base.metadata.create_all(engine)
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
