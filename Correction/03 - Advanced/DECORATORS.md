# 🎨 Décorateurs Flask

Un **décorateur** ajoute des fonctionnalités à une fonction sans modifier son code.

## 📖 Syntaxe

```python
@mon_decorateur
def ma_fonction():
    return "Hello"

# Équivalent à : ma_fonction = mon_decorateur(ma_fonction)
```

## 🔐 Les 2 Décorateurs du Projet

### 1. `@login_required` - Protection par Session

**Objectif** : Bloquer l'accès si l'utilisateur n'est pas connecté.

```python
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)  # ← Préserve le nom de la fonction (important!)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function
```

**Usage** :

```python
@app.route("/dashboard")
@login_required  # ← Vérifie la session
def dashboard():
    return render_template("dashboard.html")
```

**Routes protégées** : `/dashboard`, `/test-db`, `/api-keys/generate`, `/account/delete`

### 2. `@require_api_key` - Rate Limiting API

**Objectif** : Limiter les requêtes non-authentifiées, autoriser l'illimité avec clé API.

```python
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or \
                  request.headers.get("Authorization", "").replace("Bearer ", "")
        client_ip = request.remote_addr

        if not api_key:
            # Sans clé API : 5 max par IP
            if RequestLogNoAuth.query.filter_by(ip_address=client_ip).count() >= 5:
                return jsonify({"error": "Rate limit exceeded. Create an account!"}), 429
            # Log et continue
            response = make_response(f(*args, **kwargs))
            log = RequestLogNoAuth(ip_address=client_ip, endpoint=request.path, ...)
            db.session.add(log)
            db.session.commit()
            return response
        else:
            # Avec clé API : illimité
            key_obj = ApiKey.query.filter_by(key=api_key, is_active=True).first()
            if not key_obj:
                return jsonify({"error": "Invalid API key"}), 401
            # Log et continue (pas de limite!)
            response = make_response(f(*args, **kwargs))
            log = RequestLog(api_key_id=key_obj.id, endpoint=request.path, ...)
            db.session.add(log)
            db.session.commit()
            return response
    return decorated_function
```

**Usage** :

```python
@app.route("/api/get-user/<int:user_id>")
@require_api_key  # ← Vérifie clé + rate limiting
def get_user(user_id):
    return jsonify({"id": user_id, "name": "John"})
```

**Rate Limiting** :

| Utilisateur    | Limite     | Table                  |
| -------------- | ---------- | ---------------------- |
| Sans clé API   | 5/IP       | `request_logs_no_auth` |
| Avec clé valid | ∞ illimité | `request_logs`         |

**Tests** :

```bash
# Sans clé (5 max)
curl http://localhost:5000/api/get-user/1

# Avec clé (illimité)
curl -H "X-API-Key: bonus_abc123..." http://localhost:5000/api/get-user/1
```

## 🔧 Anatomie d'un Décorateur

```python
from functools import wraps

def mon_decorateur(f):
    @wraps(f)  # ← Garde le nom original (important pour Flask!)
    def wrapper(*args, **kwargs):
        # Code AVANT
        print("Avant")

        # Exécution fonction
        result = f(*args, **kwargs)

        # Code APRÈS
        print("Après")

        return result
    return wrapper
```

**Pourquoi `@wraps(f)` ?** Sans lui, Flask perd le nom de la fonction → erreur "endpoint already exists".

## 🎯 Ordre des Décorateurs

Les décorateurs s'appliquent **de bas en haut** :

```python
@app.route("/protected")
@login_required      # ← S'exécute en 2ème
@require_api_key     # ← S'exécute en 1er
def protected():
    return "Success"
```

**Important** : `@app.route` doit **toujours** être le premier (en haut).

## 🌐 Accès aux Données

### `request` - Données HTTP

```python
from flask import request

api_key = request.headers.get("X-API-Key")        # Header
delay = request.args.get("delay", type=int)       # Query param ?delay=5
data = request.get_json()                          # Body JSON
ip = request.remote_addr                           # IP client
```

### `session` - Cookies utilisateur

```python
from flask import session

if "user_id" in session:
    user_id = session["user_id"]       # Lire

session["user_id"] = 123               # Écrire
session.clear()                        # Supprimer
```

### `g` - Contexte de la requête

```python
from flask import g

# Dans le décorateur
g.user_id = 123

# Dans la route
@app.route("/profile")
@login_required
def profile():
    return f"User: {g.user_id}"
```

## 💡 Cas d'Usage

| Décorateur            | Utilité                      |
| --------------------- | ---------------------------- |
| `@login_required`     | Pages utilisateurs connectés |
| `@require_api_key`    | APIs avec rate limiting      |
| `@admin_required`     | Pages admin                  |
| `@cache(timeout=300)` | Cache 5 minutes              |
| `@validate_json`      | Valider body JSON            |
