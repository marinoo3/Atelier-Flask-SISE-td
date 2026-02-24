# 🧪 Flask Bonus - TD Application Web

Mini-projet bonus Flask : authentification, blueprints, API REST, rate limiting, SQLAlchemy.

## 🎯 Concepts Couverts

- **Blueprints** - Organisation modulaire (3 blueprints)
- **Authentification** - Sessions + bcrypt
- **Décorateurs** - `@login_required`, `@require_api_key`
- **SQLAlchemy** - 4 models avec relations
- **API REST** - CRUD complet avec rate limiting
- **Templates** - Jinja2 + JavaScript/AJAX

## 🚀 Installation

```bash
uv venv                           # Créer venv
.venv\Scripts\Activate.ps1        # Activer (Windows)
uv sync                           # Installer dépendances
uv run python run.py             # Lancer
```

**URLs** : http://localhost:5000 → `/auth/register` → `/dashboard` → `/bonus`

## 📁 Structure

```
03 - Advanced/
├── run.py                  # Point d'entrée
├── database.py             # Config SQLite
├── models.py               # 4 models SQLAlchemy
├── decorators.py           # Protection de routes
├── blueprints/
│   ├── auth.py            # 🔐 Register/login/logout
│   ├── main_routes.py     # 🏠 Dashboard, index
│   └── bonus_routes.py     # 🧪 API de démonstration
├── templates/              # Jinja2 HTML
└── static/                 # CSS + JavaScript
```

**Guides détaillés** : [blueprints/README.md](blueprints/README.md) | [DECORATORS.md](DECORATORS.md) | [MODELS.md](MODELS.md)

## 🔑 Fonctionnalités

### 1. Authentification

- `/auth/register` - Création de compte (username unique, email unique, bcrypt)
- `/auth/login` - Connexion avec session
- `/auth/logout` - Déconnexion
- `/dashboard` - Gestion compte + clés API + statistiques

### 2. API REST (7 routes)

| Méthode | Endpoint                    | Description              | Protection |
| ------- | --------------------------- | ------------------------ | ---------- |
| GET     | `/api/routes`               | Liste métadata routes    | Non        |
| GET     | `/api/get-user/<id>`        | Récupérer utilisateur    | API Key    |
| POST    | `/api/post-user`            | Créer utilisateur        | API Key    |
| PUT     | `/api/put-user/<id>`        | Modifier utilisateur     | API Key    |
| DELETE  | `/api/delete-user/<id>`     | Supprimer utilisateur    | API Key    |
| GET     | `/api/error-example?code=X` | Tester erreurs HTTP      | API Key    |
| GET     | `/api/request-info`         | Introspection de request | API Key    |

**Usage** :

```bash
# Sans clé API (5 requêtes max par IP)
curl http://localhost:5000/api/get-user/1

# Avec clé API (illimité)
curl -H "X-API-Key: bonus_abc123..." http://localhost:5000/api/get-user/1
```

### 3. Rate Limiting

| Utilisateur        | Limite     | Tracking                     |
| ------------------ | ---------- | ---------------------------- |
| Sans clé API       | 5/IP       | Table `request_logs_no_auth` |
| Avec clé API valid | ∞ illimité | Table `request_logs`         |

**En quoi c'est utile ?** : Un visiteur va pouvoir tester autant qu'il veut votre API sans que vous ayez la possibilité de le garder comme "client". Plutôt que de bloquer votre service aux personnes non enregistrées, en lui permettant d'utiliser le service avec un nombre limité de requête, il est plus simple pour vous, de réussir à "fidéliser" cette personne. Si l'utilisateur apprécie ce service, il aura plus de chance de s'enregistrer.

### 4. Dashboard (`/dashboard`)

- Infos compte (username, email, date)
- **Gestion clés API** : générer, copier, révoquer
- **Statistiques routes** : compteur requêtes par endpoint + méthode HTTP
- **Danger Zone** : supprimer compte + toutes données

## 🗄️ Base de Données

**Fichier** : `03 - Advanced/bonus.db` (auto-créé au démarrage)

**4 Models** :

1. `User` - Comptes (username, email, password_hash)
2. `ApiKey` - Clés API (user_id FK, key, is_active)
3. `RequestLog` - Logs requêtes authentifiées (api_key_id FK, endpoint, method, IP)
4. `RequestLogNoAuth` - Logs requêtes anonymes (IP, endpoint, method)

**Relations** :

```
User (1) ───< ApiKey (N) ───< RequestLog (N)
RequestLogNoAuth (indépendant, tracking par IP)
```

## 📚 Pour Aller Plus Loin

**Concepts détaillés** :

- [blueprints/README.md](blueprints/README.md) - Organisation modulaire Flask
- [DECORATORS.md](DECORATORS.md) - Décorateurs `@login_required` et `@require_api_key`
- [MODELS.md](MODELS.md) - SQLAlchemy models et CRUD

**Technologies** :

- Flask 3.1.2+ - Framework web
- Flask-SQLAlchemy 3.1.1+ - ORM
- Werkzeug 3.1.3+ - Bcrypt
- SQLite - Base de données
- Jinja2 - Templates
- uv - Package manager
