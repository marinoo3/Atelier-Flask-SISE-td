# Atelier Flask — Master 2 SISE

Cet atelier a pour objectif de vous initier au développement d'applications web avec **Flask**, un framework Python léger et flexible. Il est structuré en **3 niveaux progressifs**, du "Hello World" jusqu'à la mise en place d'une authentification sécurisée en passant par une application RAG connectée à un LLM.

## Prérequis

- Python 3.x installé
- [`uv`](https://docs.astral.sh/uv/) installé (gestionnaire de paquets Python moderne)
- Connaissance basique de Python et HTML

## Structure du dépôt

```
Atelier-Flask-SISE-td/
├── 01 - Hello world/   # Niveau 1 — Introduction à Flask et SQLAlchemy
├── 02 - RAGme/         # Niveau 2 — Application structurée avec RAG et LLM
├── 03 - Advanced/      # Niveau 3 — Authentification et blueprints (bonus)
├── Correction/         # Corrections des 3 exercices
└── Atelier_Flask_presentation.pdf
```

---

## Niveau 1 — Hello World

**Objectif** : créer une première application Flask permettant d'ajouter et d'afficher des films depuis une base de données SQLite.

**Concepts abordés** :
- Routes Flask (GET / POST)
- Templates Jinja2
- Modèles et sessions SQLAlchemy

**Démarrage :**
```bash
cd "01 - Hello world"
uv init
uv add flask sqlalchemy
uv run app.py
```

Consulter le [README du niveau 1](./01%20-%20Hello%20world/README.md) pour les consignes détaillées.

---

## Niveau 2 — RAGme

**Objectif** : construire une application de chat dynamique exploitant le **Retrieval-Augmented Generation (RAG)** avec l'API Mistral. L'utilisateur peut charger des documents PDF et poser des questions au LLM en contexte.

**Concepts abordés** :
- Architecture Flask en services (`models`, `database`, `services`, `schemas`)
- ORM SQLAlchemy et schémas Pydantic
- Communication AJAX entre le frontend JS et le backend Python
- Intégration d'une API LLM (Mistral) et d'une base vectorielle (ChromaDB)

**Démarrage :**
```bash
cd "02 - RAGme"
uv sync
cp .env-example .env   # Renseigner votre clé API Mistral dans .env
uv run python run.py
```

> Une démo de l'application est accessible ici : https://marinnagy.com/projects/ragme

Consulter le [README du niveau 2](./02%20-%20RAGme/README.md) pour les consignes détaillées.

---

## Niveau 3 — Advanced (Bonus)

**Objectif** : implémenter un système d'authentification complet (inscription, connexion, protection de routes) pour une application Flask existante.

**Concepts abordés** :
- Blueprints Flask pour l'organisation modulaire du code
- Hashing sécurisé des mots de passe avec `werkzeug`
- Sessions Flask pour la gestion de l'état utilisateur
- Décorateurs personnalisés (`@login_required`)
- Système de clés API avec rate limiting

**Démarrage :**
```bash
cd "03 - Advanced"
uv sync
uv run python run.py
```

Consulter le [README du niveau 3](./03%20-%20Advanced/README.md) pour les consignes détaillées.

---

## Corrections

Les corrections complètes des trois exercices sont disponibles dans le dossier [`Correction/`](./Correction/).
