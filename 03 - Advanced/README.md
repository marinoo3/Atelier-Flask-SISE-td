# Exercice 3 - Authentification Flask (Avancé)

## 📋 Vue d'Ensemble

Ce TD bonus vous permet d'implémenter un système d'authentification complet pour une application Flask. Vous apprendrez à gérer les sessions, sécuriser les mots de passe et protéger des routes avec des décorateurs personnalisés.

**⏱️ Durée estimée** : 1 heure

## 🎯 Objectifs

À la fin de ce TD, vous aurez implémenté :

1. ✅ **Système d'inscription et de connexion** (routes `/register` et `/login`)
2. ✅ **Hashing sécurisé des mots de passe** (werkzeug)
3. ✅ **Décorateur personnalisé** `@login_required` pour protéger les routes
4. ✅ **Gestion de sessions Flask** pour maintenir l'état de connexion

## 📚 Prérequis

- TDs "Hello World" et "RAGme" complétés
- Python 3.x et `uv` installés

## 🚀 Démarrage Rapide

### 1. Installation

```bash
cd "03 - Advanced"
uv sync
```

### 2. Lancer l'application

```bash
uv run python run.py
```

### 3. Ouvrir les consignes

**➡️ Consultez le fichier [TD.md](TD.md) pour les consignes détaillées**

**Bon courage ! 🎉**

## 📁 Structure du Projet

```
03 - Advanced/
├── TD.md                     # ⭐ CONSIGNES DÉTAILLÉES DU TD
├── run.py                    # Point d'entrée de l'application
├── database.py               # Configuration SQLAlchemy
├── models.py                 # Models (User, ApiKey, RequestLog)
├── decorators.py             # Décorateurs (@login_required à implémenter)
├── blueprints/
│   ├── auth.py              # 🔨 Routes authentification (À IMPLÉMENTER)
│   ├── main_routes.py       # Routes principales (dashboard)
│   └── bonus_routes.py      # API routes (fonctionnelles)
├── templates/
│   ├── login.html           # Formulaire de connexion
│   ├── register.html        # Formulaire d'inscription
│   ├── dashboard.html       # Page protégée
│   └── bonus.html           # Interface de test
└── static/
    ├── bonus.css
    └── bonus.js
```

## 🏗️ Progression du TD

### Phase 1 : Authentification Basique (20 min)

Implémentez les routes d'inscription, de connexion et de déconnexion avec des mots de passe en clair (temporairement).

**Fichier** : `blueprints/auth.py`

- Route `/register` (GET, POST)
- Route `/login` (GET, POST)
- Route `/logout` (GET)

### Phase 2 : Sécurité (15 min)

Ajoutez le hashing sécurisé des mots de passe avec werkzeug.

**Fichier** : `models.py`

- Méthode `set_password()`
- Méthode `check_password()`
- Changement de colonne : `password` → `password_hash`

### Phase 3 : Protection de Routes (20 min)

Créez un décorateur `@login_required` pour protéger les routes.

**Fichier** : `decorators.py`

- Décorateur `@login_required`
- Application sur les routes du dashboard

## ✅ Checklist de Validation

Vous avez terminé quand vous pouvez :

- [ ] Créer un compte sur `/auth/register`
- [ ] Vous connecter sur `/auth/login`
- [ ] Voir votre username affiché après connexion
- [ ] Accéder au dashboard `/dashboard` (connecté uniquement)
- [ ] Être redirigé vers login si non connecté
- [ ] Générer une API key depuis le dashboard
- [ ] Vous déconnecter avec `/auth/logout`

## 🔧 Concepts Flask Couverts

- **Blueprints** : Organisation modulaire du code
- **Sessions** : Maintien de l'état utilisateur
- **Password Hashing** : Sécurité avec werkzeug
- **Décorateurs** : Fonctions modifiant le comportement d'autres fonctions
- **Flash Messages** : Notifications utilisateur
- **SQLAlchemy** : Relations et foreign keys
- **Templating Jinja2** : Affichage dynamique

## 🎓 Ce Qui Est Déjà Fait (Ne Pas Toucher)

Pour vous concentrer sur l'authentification, ces fonctionnalités sont **déjà implémentées** :

✅ **Système d'API Keys** (génération, révocation, soft delete)  
✅ **Rate Limiting API** (5 requêtes gratuites par IP, illimité avec clé)  
✅ **Logs de Requêtes** (tracking des appels API)  
✅ **Routes API de Test** (`/api/get-user`, `/api/post-user`, etc.)  
✅ **Dashboard Statistiques** (affichage des API keys et usage)  
✅ **Templates HTML/CSS** (login, register, dashboard)

Vous allez implémenter uniquement la **couche d'authentification** qui manque.

## 📚 Documentation Utile

### Flask - Sessions

```python
# Écrire
session["user_id"] = 123

# Lire
user_id = session.get("user_id")

# Vérifier
if "user_id" in session:
    # Connecté

# Effacer
session.clear()
```

### Werkzeug - Security

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hasher
hash = generate_password_hash("password123")

# Vérifier
if check_password_hash(hash, "password123"):
    print("Correct!")
```

### Décorateurs

```python
from functools import wraps

def mon_decorateur(f):
    @wraps(f)  # Important!
    def wrapper(*args, **kwargs):
        # Avant
        result = f(*args, **kwargs)
        # Après
        return result
    return wrapper

@mon_decorateur
def ma_fonction():
    pass
```
