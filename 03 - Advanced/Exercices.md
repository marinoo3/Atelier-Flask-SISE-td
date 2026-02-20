# Le "From-scratch"

> **Objectif** : Manipulation pour comprendre Flask avant d'attaquer le projet RAG.

## Features à Retirer et Faire Développer

### Gestion des API Keys

> Comprendre comment peuvent être générées et désactivées les clés API (peut être utile si un jour quelqu'un doit travailler sur une API).

**Retirer** :

- Model `ApiKey`
- Routes `/api-keys/generate` et `/api-keys/<id>/revoke`

**Faire développer** :

1. Model `ApiKey` avec FK vers User
2. Méthode `generate_key()` avec `secrets.token_hex(24)`
3. Routes pour générer/révoquer (soft delete avec `is_active`)

**Concepts** : Foreign Keys, relations, soft delete, génération de tokens

### Authentification Complète

> Comprendre l'importance de la sécurité dans des projets où on manipule des données utilisateurs, ou, des systèmes d'authentifications.

**Retirer** :

- Blueprint `auth.py` entier
- Décorateur `@login_required`
- Décorateur `@login_required` dans la route `test_db`

**Faire développer** :

1. Model User avec `password_hash`
2. Méthodes `set_password()` et `check_password()`
3. Routes register/login/logout
4. Décorateur `@login_required`

**Concepts** : Hashing bcrypt, sessions Flask, validation, sécurité
