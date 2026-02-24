# 🗄️ Models SQLAlchemy

Un **model** est une classe Python représentant une table de base de données. L'ORM SQLAlchemy mappe les objets Python aux lignes SQL.

## 📊 Les 4 Models

### 1. `User` - Comptes Utilisateurs

**Table** : `users`

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    api_keys = db.relationship('ApiKey', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

**Usage** :

```python
user = User(username="john", email="john@example.com")
user.set_password("secret123")
db.session.add(user)
db.session.commit()

# Login
if user.check_password("secret123"):
    print("OK!")
```

### 2. `ApiKey` - Clés API

**Table** : `api_keys`

```python
class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(200), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relations
    request_logs = db.relationship('RequestLog', backref='api_key', lazy=True)

    @staticmethod
    def generate_key():
        return f"bonus_{secrets.token_hex(24)}"  # bonus_abc123...
```

**Usage** :

```python
# Générer clé
api_key = ApiKey(user_id=user.id, key=ApiKey.generate_key())
db.session.add(api_key)
db.session.commit()

# Valider clé
key_obj = ApiKey.query.filter_by(key="bonus_abc...", is_active=True).first()
```

### 3. `RequestLog` - Logs Authentifiés

**Table** : `request_logs`

```python
class RequestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)  # GET, POST, etc.
    status_code = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(50))
```

**Utilité** : Statistiques par route/méthode, audit.

### 4. `RequestLogNoAuth` - Logs Anonymes

**Table** : `request_logs_no_auth`

```python
class RequestLogNoAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False, index=True)
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
```

**Utilité** : Rate limiting 5/IP pour utilisateurs sans clé API.

## 🔗 Relations

```
User (1) ───< ApiKey (N) ───< RequestLog (N)

RequestLogNoAuth (indépendant)
```

- Un `User` a plusieurs `ApiKey`
- Une `ApiKey` a plusieurs `RequestLog`
- `RequestLogNoAuth` sans FK (tracking par IP)

**Accès aux relations** :

```python
# User → ApiKeys
user = User.query.get(1)
for key in user.api_keys:
    print(key.key)

# ApiKey → User (backref)
api_key = ApiKey.query.first()
print(api_key.user.username)

# ApiKey → Logs
for log in api_key.request_logs:
    print(log.endpoint, log.method)
```

## 📝 CRUD Operations

### CREATE

```python
user = User(username="alice", email="alice@example.com")
db.session.add(user)
db.session.commit()
print(user.id)  # ID auto-généré
```

### READ

```python
# Tous
users = User.query.all()

# Par ID
user = User.query.get(123)  # ou .get_or_404(123)

# Filtrer
user = User.query.filter_by(username="alice").first()
users = User.query.filter_by(is_active=True).all()

# Compter
count = User.query.count()

# Ordonner
users = User.query.order_by(User.created_at.desc()).limit(10).all()
```

### UPDATE

```python
user = User.query.get(123)
user.email = "newemail@example.com"
db.session.commit()
```

### DELETE

```python
user = User.query.get(123)
db.session.delete(user)
db.session.commit()
```

## 🎯 Contraintes et Options

```python
# Primary key (auto-increment)
id = db.Column(db.Integer, primary_key=True)

# Unique (pas de doublons)
username = db.Column(db.String(80), unique=True)

# Not null (obligatoire)
email = db.Column(db.String(120), nullable=False)

# Valeur par défaut
is_active = db.Column(db.Boolean, default=True)
created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Index (recherche rapide)
api_key = db.Column(db.String(200), index=True)

# Foreign key
user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
```

## 💾 Session SQLAlchemy

```python
# Ajouter
db.session.add(user)
db.session.add_all([user1, user2])

# Valider (écriture en BDD)
db.session.commit()

# Annuler
db.session.rollback()

# Supprimer
db.session.delete(user)
db.session.commit()
```

**Important** : Sans `commit()`, rien n'est sauvegardé !

## 🔒 Sécurité Mots de Passe

**❌ JAMAIS en clair** :

```python
user.password = "secret123"  # DANGEREUX!
```

**✅ Toujours hasher** :

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash (bcrypt + salt)
user.password_hash = generate_password_hash("secret123")

# Vérifier
if check_password_hash(user.password_hash, "secret123"):
    print("OK!")
```

**Pourquoi ?**

- **bcrypt** : algorithme lent → résiste au brute force
- **salt** : même mot de passe → hash différent
- Impossible de retrouver le mot de passe original

## 🚨 Gestion d'Erreurs

```python
from sqlalchemy.exc import IntegrityError

try:
    user = User(username="alice", email="alice@example.com")
    db.session.add(user)
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    print("Erreur : Username/email déjà utilisé (UNIQUE constraint)")
```
