# TD Bonus - Authentification Flask (1h)

> **Objectif** : Implémenter un système d'authentification complet avec gestion de sessions, sécurité des mots de passe et protection de routes via des décorateurs.

## 🎯 Objectifs Pédagogiques

À la fin de ce TD, vous saurez :

- ✅ Créer un système d'inscription et de connexion
- ✅ Gérer les sessions Flask
- ✅ Sécuriser les mots de passe avec hashing
- ✅ Créer et utiliser des décorateurs personnalisés
- ✅ Protéger des routes avec `@login_required`

## 📚 Prérequis

- Python 3.x et `uv` installés
- Connaissance de base de Flask et SQLAlchemy
- Avoir complété le TD "Hello World"

## 🚀 Démarrage

### Installation

```bash
cd "03 - Advanced"
uv sync
```

### Lancer l'application

```bash
uv run python run.py
```

Accédez à `http://localhost:5000` pour voir l'interface de test.

## 📋 Structure du Projet

```
03 - Advanced/
├── run.py                    # Point d'entrée de l'application
├── database.py               # Configuration SQLAlchemy
├── models.py                 # Models (User, ApiKey, RequestLog)
├── decorators.py             # Décorateurs (@login_required à implémenter)
├── blueprints/
│   ├── auth.py              # Routes d'authentification (À IMPLÉMENTER)
│   ├── main_routes.py       # Routes principales (dashboard, etc.)
│   └── bonus_routes.py      # API routes (déjà fonctionnelles)
└── templates/
    ├── login.html           # Formulaire de connexion
    ├── register.html        # Formulaire d'inscription
    └── dashboard.html       # Page protégée
```

---

## 🏗️ Phase 1 : Authentification de Base (20 min)

### Objectif

Implémenter les routes d'inscription, de connexion et de déconnexion avec des **mots de passe en clair** (temporairement, pour comprendre la logique avant la sécurité).

### Fichier à Modifier : `blueprints/auth.py`

#### 🔨 Exercice 1.1 : Route `/register` (10 min)

Implémentez la route d'inscription qui :

**Méthode GET** :

- Affiche le formulaire d'inscription avec `render_template("register.html")`

**Méthode POST** :

1. Récupère les données du formulaire :

   ```python
   username = request.form.get("username")
   email = request.form.get("email")
   password = request.form.get("password")
   password_confirm = request.form.get("password_confirm")
   ```

2. Valide les données :
   - ✅ Tous les champs sont remplis
   - ✅ Les mots de passe correspondent
   - ✅ Le mot de passe fait au moins 6 caractères
   - ✅ Le username n'existe pas déjà : `User.query.filter_by(username=username).first()`
   - ✅ L'email n'existe pas déjà : `User.query.filter_by(email=email).first()`

3. En cas d'erreur, utilisez :

   ```python
   flash("Message d'erreur", "error")
   return render_template("register.html")
   ```

4. Si tout est valide, créez l'utilisateur **avec mot de passe en clair** :
   ```python
   new_user = User(username=username, email=email, password=password)
   db.session.add(new_user)
   db.session.commit()
   flash("Registration successful! Please login.", "success")
   return redirect(url_for("auth.login"))
   ```

**📝 Code Squelette** :

```python
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # TODO: Récupérer les données du formulaire

        # TODO: Valider les données

        # TODO: Vérifier que username et email n'existent pas

        # TODO: Créer le nouvel utilisateur

        # TODO: Rediriger vers login
        pass

    return render_template("register.html")
```

#### 🔨 Exercice 1.2 : Route `/login` (7 min)

Implémentez la route de connexion qui :

**Méthode GET** :

- Affiche le formulaire de connexion avec `render_template("login.html")`

**Méthode POST** :

1. Récupère username et password du formulaire
2. Trouve l'utilisateur : `user = User.query.filter_by(username=username).first()`
3. Vérifie que l'utilisateur existe et que le mot de passe correspond **en clair** :
   ```python
   if user and user.password == password:
       session["user_id"] = user.id
       session["username"] = user.username
       flash(f"Welcome back, {user.username}!", "success")
       return redirect(url_for("main.index"))
   ```
4. Sinon, affiche une erreur : `flash("Invalid username or password", "error")`

**📝 Code Squelette** :

```python
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # TODO: Récupérer username et password

        # TODO: Trouver l'utilisateur

        # TODO: Vérifier mot de passe (comparaison directe pour l'instant)

        # TODO: Créer la session

        pass

    return render_template("login.html")
```

#### 🔨 Exercice 1.3 : Route `/logout` (3 min)

Implémentez la route de déconnexion qui :

1. Vide la session : `session.clear()`
2. Redirige vers login avec un message

```python
@auth.route("/logout")
def logout():
    # TODO: Vider la session
    # TODO: Rediriger vers login
    pass
```

### ✅ Checkpoint Phase 1

Testez votre implémentation :

1. Allez sur `http://localhost:5000/auth/register`
2. Créez un compte (ex: `alice` / `alice@test.com` / `password123`)
3. Connectez-vous sur `http://localhost:5000/auth/login`
4. Vérifiez que vous voyez votre username en haut à droite

**⚠️ À ce stade, les mots de passe sont en CLAIR dans la base de données ! C'est temporaire.**

### 🚨 Démonstration du Problème de Sécurité

Avant de passer à la Phase 2, constatons **pourquoi** le hashing est crucial :

1. **Créez plusieurs comptes** :
   - Déconnectez-vous (bouton "Logout")
   - Créez 2-3 autres comptes : `bob` / `bob@test.com` / `secret456`, `charlie` / `charlie@test.com` / `pass789`, etc.

2. **Accédez à la page de test** :
   - Connectez-vous avec n'importe quel compte
   - Allez sur `http://localhost:5000/test-db`
   - Cette page affiche tous les utilisateurs de la base de données

3. **Constatez le problème** :
   - Actuellement, on affiche seulement l'ID, le username et l'email
   - **MAIS** : on pourrait facilement afficher la colonne `password` qui contient les mots de passe en clair !

4. **Pour le vérifier** (optionnel) :
   - Ouvrez le fichier `templates/test_db.html`
   - Cherchez la ligne qui affiche : `<td>{{ user.email }}</td>`
   - Ajoutez juste après : `<td>{{ user.password }}</td>`
   - Rechargez `/test-db` → vous verrez tous les mots de passe en clair !

**🎯 Conclusion** : Stocker des mots de passe en clair est une **faille de sécurité majeure**. Même si votre application ne les affiche pas, ils sont accessibles :

- En cas de vol de base de données (hack, backup compromis)
- Par les administrateurs système
- Par tout développeur ayant accès à la DB

**➡️ Solution : Le Hashing (Phase 2)**

---

## 🔐 Phase 2 : Sécurité - Hashing des Mots de Passe (15 min)

### Objectif

Remplacer le stockage en clair par un système de hashing sécurisé avec **werkzeug**.

### Fichier à Modifier : `models.py`

#### 🔨 Exercice 2.1 : Import et Changement de Colonne (2 min)

1. Décommentez l'import :

   ```python
   from werkzeug.security import generate_password_hash, check_password_hash
   ```

2. Dans la classe `User`, changez :

   ```python
   password = db.Column(db.String(255), nullable=False)  # ❌ Clair
   # EN
   password_hash = db.Column(db.String(255), nullable=False)  # ✅ Hashé
   ```

3. **Supprimez la base de données** pour recréer les tables :
   ```bash
   # Arrêtez le serveur (Ctrl+C)
   rm bonus.db  # ou del bonus.db sur Windows
   uv run python run.py  # Redémarrez
   ```

#### 🔨 Exercice 2.2 : Méthode `set_password()` (5 min)

Implémentez la méthode pour hasher et stocker un mot de passe :

```python
def set_password(self, password):
    """
    Hash and store the user's password.
    Uses werkzeug's secure password hashing.

    Args:
        password: Plain text password
    """
    # TODO: Utiliser generate_password_hash() pour hasher le password
    # TODO: Stocker le résultat dans self.password_hash
    pass
```

**💡 Aide** : `generate_password_hash(password)` retourne un hash sécurisé (bcrypt par défaut).

#### 🔨 Exercice 2.3 : Méthode `check_password()` (5 min)

Implémentez la méthode pour vérifier un mot de passe :

```python
def check_password(self, password):
    """
    Verify a password against the stored hash.

    Args:
        password: Plain text password to verify

    Returns:
        bool: True if password matches, False otherwise
    """
    # TODO: Utiliser check_password_hash() pour vérifier
    # TODO: Comparer self.password_hash avec le password fourni
    pass
```

**💡 Aide** : `check_password_hash(hash, password)` retourne `True` si le mot de passe est correct.

#### 🔨 Exercice 2.4 : Adaptation de `auth.py` (3 min)

Modifiez vos routes pour utiliser les nouvelles méthodes :

**Dans `/register`** :

```python
# Ancien code (à remplacer) :
new_user = User(username=username, email=email, password=password)

# Nouveau code :
new_user = User(username=username, email=email)
new_user.set_password(password)  # ← Utilise le hashing
```

**Dans `/login`** :

```python
# Ancien code (à remplacer) :
if user and user.password == password:

# Nouveau code :
if user and user.check_password(password):  # ← Vérifie le hash
```

### ✅ Checkpoint Phase 2

1. Recréez un compte (l'ancien ne fonctionne plus car la DB a changé)
2. Connectez-vous
3. Ouvrez `bonus.db` avec un viewer SQLite (ou DB Browser for SQLite)
4. Vérifiez que la colonne `password_hash` contient un hash (ex: `scrypt:32768:8:1$...`) et non le mot de passe en clair

Si vous avez ajouté les mots de passes sur la page test_db, vous pouvez y retourner et remplacer `password` par `password_hash`. Maintenant vous ne pouvez plus lire les mots de passe sans la clé de décryption.

**🎉 Vos mots de passe sont maintenant sécurisés !**

---

## 🛡️ Phase 3 : Protection de Routes - Décorateur `@login_required` (20 min)

### Objectif

Créer un décorateur personnalisé pour protéger les routes nécessitant une authentification.

### Fichier à Modifier : `decorators.py`

#### 🔨 Exercice 3.1 : Comprendre les Décorateurs (5 min - Lecture)

Un décorateur est une fonction qui modifie le comportement d'une autre fonction. Syntaxe :

```python
@mon_decorateur
def ma_fonction():
    return "Hello"

# Équivalent à :
ma_fonction = mon_decorateur(ma_fonction)
```

**Structure d'un décorateur Flask** :

```python
from functools import wraps

def mon_decorateur(f):
    @wraps(f)  # ← Préserve le nom original (important pour Flask!)
    def wrapper(*args, **kwargs):
        # Code AVANT l'exécution de la fonction
        print("Avant")

        # Exécution de la fonction originale
        result = f(*args, **kwargs)

        # Code APRÈS l'exécution
        print("Après")

        return result
    return wrapper
```

#### 🔨 Exercice 3.2 : Implémenter `@login_required` (15 min)

Implémentez le décorateur qui vérifie si l'utilisateur est connecté :

**Cahier des Charges** :

1. Vérifier si `"user_id"` existe dans `session`
2. Si **NON** :
   - Pour les routes API (`/api/*`) : retourner un JSON d'erreur 401
   - Pour les autres : rediriger vers `auth.login`
3. Si **OUI** : exécuter la fonction normalement

**📝 Code Squelette** :

```python
def login_required(f):
    """
    Decorator to protect routes that require authentication.

    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "You are logged in!"
    """

    @wraps(f)  # ← Ne pas oublier !
    def decorated_function(*args, **kwargs):
        # TODO: Vérifier si "user_id" est dans session

        # TODO: Si non authentifié et route API → JSON 401
        # Aide : request.path.startswith("/api/")
        # return jsonify({"error": "Authentication required"}), 401

        # TODO: Si non authentifié et route web → redirect login
        # return redirect(url_for("auth.login"))

        # TODO: Si authentifié → exécuter fonction
        # return f(*args, **kwargs)

        pass

    return decorated_function
```

**💡 Aide** :

```python
# Vérifier la session
if "user_id" not in session:
    # Non authentifié

# Vérifier si route API
if request.path.startswith("/api/"):
    return jsonify({"error": "Authentication required"}), 401
```

#### 🔨 Exercice 3.3 : Appliquer le Décorateur (Bonus)

Dans `main_routes.py`, décommentez l'import :

```python
from decorators import login_required
```

Puis ajoutez `@login_required` sur les routes avec TODOs :

- `/dashboard`
- `/test-db`
- `/api-keys/generate`
- `/api-keys/<int:key_id>/revoke`
- `/account/delete`

**Exemple** :

```python
@main.route("/dashboard")
@login_required  # ← Ajoutez cette ligne
def dashboard():
    # ...
```

**⚠️ Ordre Important** : `@app.route` doit toujours être **au-dessus** des autres décorateurs !

### ✅ Checkpoint Phase 3

1. **Sans être connecté** :
   - Allez sur `http://localhost:5000/dashboard` → doit rediriger vers login
   - Allez sur `http://localhost:5000/test-db` → doit rediriger vers login

2. **En étant connecté** :
   - Connectez-vous sur `/auth/login`
   - Allez sur `/dashboard` → doit afficher le dashboard
   - Vérifiez que vous voyez vos API keys et statistiques

3. **Déconnectez-vous** :
   - Cliquez sur "Logout"
   - Tentez d'accéder à `/dashboard` → doit rediriger vers login

**🎉 Vos routes sont maintenant protégées !**

---

## 🏆 Synthèse et Concepts Clés

### Ce que vous avez appris

#### 1. **Sessions Flask**

```python
# Écrire
session["user_id"] = 123
session["username"] = "alice"

# Lire
user_id = session.get("user_id")

# Vérifier
if "user_id" in session:
    # Utilisateur connecté

# Effacer
session.clear()
```

#### 2. **Hashing de Mots de Passe**

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Stocker
password_hash = generate_password_hash("secret123")

# Vérifier
if check_password_hash(password_hash, "secret123"):
    print("Correct!")
```

**⚠️ Règle d'Or** : **JAMAIS** stocker de mots de passe en clair !

#### 3. **Décorateurs Python**

```python
from functools import wraps

def mon_decorateur(f):
    @wraps(f)  # ← Garde le nom original
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

#### 4. **Validation de Formulaires**

```python
# Récupérer les données
username = request.form.get("username")

# Valider
if not username:
    flash("Username required", "error")
    return render_template("form.html")

# Vérifier unicité
if User.query.filter_by(username=username).first():
    flash("Username already exists", "error")
```

#### 5. **Flash Messages**

```python
# Dans la route
flash("Message de succès", "success")
flash("Message d'erreur", "error")
flash("Message d'info", "info")

# Dans le template (déjà fait)
{% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
        <div class="alert alert-{{ category }}">{{ message }}</div>
    {% endfor %}
{% endwith %}
```

---

## 📚 Ressources

- [Documentation Flask - Sessions](https://flask.palletsprojects.com/en/latest/quickstart/#sessions)
- [Documentation Werkzeug - Security](https://werkzeug.palletsprojects.com/en/latest/utils/#module-werkzeug.security)
- [Documentation Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Python Decorators Explained](https://realpython.com/primer-on-python-decorators/)

---

## 🎯 Checklist Finale

Avant de terminer, vérifiez que :

- [ ] Vous pouvez créer un compte via `/auth/register`
- [ ] Vous pouvez vous connecter via `/auth/login`
- [ ] Les mots de passe sont hashés dans la base de données
- [ ] Le dashboard est inaccessible sans connexion
- [ ] Le décorateur `@login_required` fonctionne
- [ ] Vous pouvez générer une API key depuis le dashboard
- [ ] Vous pouvez vous déconnecter via `/auth/logout`

**🎉 Félicitations ! Vous avez implémenté un système d'authentification complet et sécurisé !**
