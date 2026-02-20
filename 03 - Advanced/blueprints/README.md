# 📦 Blueprints - Organisation Modulaire

Un **Blueprint** organise les routes Flask en modules réutilisables par thématique.

## 🔧 Syntaxe de Base

### 1. Créer le Blueprint

```python
# blueprints/auth.py
from flask import Blueprint

auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route("/login")
def login():
    return "Page de login"

@auth.route("/register")
def register():
    return "Page d'inscription"
```

### 2. Enregistrer dans l'app

```python
# run.py
from blueprints.auth import auth

app = Flask(__name__)
app.register_blueprint(auth)
```

**Résultat** : `/login` devient `/auth/login`, `/register` devient `/auth/register`

## 📁 Structure de ce Projet

```
blueprints/
├── auth.py          # 🔐 Register, login, logout
├── main_routes.py   # 🏠 Dashboard, API keys, account
└── bonus_routes.py   # 🧪 API CRUD (GET, POST, PUT, DELETE)
```

## 🎯 Les 3 Blueprints

### 1. `auth` - Authentification

**Préfixe** : `/auth`

| Route            | Méthode | Action         |
| ---------------- | ------- | -------------- |
| `/auth/register` | POST    | Créer compte   |
| `/auth/login`    | POST    | Se connecter   |
| `/auth/logout`   | GET     | Se déconnecter |

**Features** : Validation, bcrypt, sessions

### 2. `main` - Pages Principales

**Préfixe** : Aucun (racine)

| Route                   | Méthode | Action           | Protection        |
| ----------------------- | ------- | ---------------- | ----------------- |
| `/`                     | GET     | Page d'accueil   | Non               |
| `/dashboard`            | GET     | Tableau de bord  | `@login_required` |
| `/test-db`              | GET     | Test database    | `@login_required` |
| `/api-keys/generate`    | POST    | Générer clé API  | `@login_required` |
| `/api-keys/<id>/revoke` | POST    | Révoquer clé API | `@login_required` |
| `/account/delete`       | POST    | Supprimer compte | `@login_required` |

**Features** : Gestion clés API, statistiques routes, delete account

### 3. `bonus` - API de Démonstration

**Préfixe** : `/api`

| Route                   | Méthode | Action              | Protection         |
| ----------------------- | ------- | ------------------- | ------------------ |
| `/api/routes`           | GET     | Liste métadata      | Non                |
| `/api/get-user/<id>`    | GET     | Récupérer user      | `@require_api_key` |
| `/api/post-user`        | POST    | Créer user          | `@require_api_key` |
| `/api/put-user/<id>`    | PUT     | Modifier user       | `@require_api_key` |
| `/api/delete-user/<id>` | DELETE  | Supprimer user      | `@require_api_key` |
| `/api/error-example`    | GET     | Test erreurs HTTP   | `@require_api_key` |
| `/api/request-info`     | GET     | Introspection Flask | `@require_api_key` |

**Features** : Rate limiting (5/IP sans clé, ∞ avec clé), CRUD complet

## 🔗 url_for() avec Blueprints

```python
# Syntaxe : url_for('blueprint_name.function_name')
url_for('auth.login')              # /auth/login
url_for('main.dashboard')          # /dashboard
url_for('bonus.get_user', id=123)   # /api/get-user/123
```

## 💡 Avantages

- **Organisation** : 1 fichier par domaine fonctionnel
- **Maintenance** : Facile de trouver une route
- **Travail équipe** : Moins de conflits Git
- **Réutilisable** : Blueprint exportable vers d'autres projets
