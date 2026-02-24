# RAGme

Créer une application dynamique avec Flask, structurée en services, utilisant des bases de données et une API Mistral.

> Demo de l'application accessible ici : https://marinnagy.com/projects/ragme

### Prérequis
- Exploration du TD ["01 - Hello world"](https://github.com/marinoo3/Atelier-Flask-SISE-td/tree/main/01%20-%20Hello%20world)
- Python 3.x installé
- `uv` installé

## Initialisation du projet

#### Environnement

1. Se déplacer dans le répertoire `02 - RAGme`
2. Synchroniser les dépendances avec `uv`
3. Activer l'environnement

#### Fichier `.env`

4. Dupliquer le fichier `.env-example` et le nommer `.env`
5. Renseigner une clé API Mistral
6. Lancer l'app et accéder son URL dans un navigateur internet 
```bash
python run.py
```
> Aucune route n'est pour l'instant exposée, d'où l'erreur **404 Not Found**.

## Route principale

L'application est composée d'une seule page. Il s'agit du fichier `chat.html` dans le dossier `templates`. Nous avons donc besoin d'une seule route exposée sur une seule URL. Cette page est dynamique, c'est-à-dire que l'on va modifier le contenu de chacun des blocs individuellement en fonction des actions de l'utilisateur.

#### Fichier `app/routes.py`

1. Créer une route à la racine de l'app (url = `/`)
2. Dans cette route, renvoyer le template `chat.html` à l'aide de la fonction `render_template`.
3. Recharger la page du navigateur, nous avons désormais le squelette de l'application.

> Le fichier `chat.html` contient le squelette de la page (barre de navigation et structure des sections). Le contenu de chaque bloc va être généré de manière dynamique.

Nous avons maintenant besoin d'implémenter notre ORM afin de pouvoir exploiter la base de données et continuer l'interface.

## Création de l'ORM et configuration de la base de donnée

Afin de préparer le modèle *SQLAlchemy* permettant de générer l'**O**bject **R**elational **M**apping: l'objet python permettant de mapper une classe à la table relationnelle contenant les documents.

>L'ORM permet de configurer une base de donnée SQL avec grande facilité, et permettre des intéractions avec cette dernière via des objets pythons tels que nous les connaissons. Nous évitons ainsi de gérer les connecteurs et les réequêts SQL.

### Module `app.models`

#### Fichier `app/models/base.py`

1. Dans le fichier `base.py` déclarer l'objet de base de SQLAlchemy. (Voir la partie `01 - Hello world`). Cet objet devra être héritée par tous les modèles `SQLAlchemy` afin d'enregistrer les classes mappées et les métadonnées.

#### Fichier `app/models/document.py`

Dans le fichier `document.py`:

2. Importez l'objet `Base` précédemment créé
3. Créez la classe `Document`: le modèle de document de la base de donnée.
    - Elle doit hériter de `Base` afin d'enregistrer la classe dans l'ORM.
    - Nommez la table `documents`
    - Configurez les champs de votre table:
    ```
    id (int): Unique identifier for the document.
    title (str): Title of the document.
    binary (bytes): Binary content of the document (e.g., PDF data).
    category (Optional[str]): Optional category or type of the document.
    url (Optio
    nal[str]): Optional URL where the document can be accessed.
    ```
    - Veillez à bien respecter le typage, et les contraintes d'unicités. Tous les imports de typage sont préchargés pour vous, et un exemple est proposé.
    
#### Fichier `app/models/__init__.py`

Dans le fichier initialisateur du module, exposez la classe Document:

4. Importez du fichier `document.py` la classe Document.
5. paramétrez l'attribut `__all__` pour exposer la classe. 

> 💡https://medium.com/@akshatgadodia/demystifying-all-in-python-a-closer-look-at-module-exports-f4d818a12bb6

### Module `app.database`

Les modèles sont prêts; il faut à présent paramétrer la base de donnée elle même. Dans le fichier `sql_db`, vous trouverez une classe `Database` dont il vous faudra finaliser l'implémentation.

> Cette classe possède plusieurs méthodes:
> - Une initialisation de l'engine SQLAlchemy permettant la lecture et ecriture dans la base de donnée locale
> - Un `contextmanager` permettant d'ouvrir une session gérant les objets pythons contenant les informations extraites de la base. Le contextmanager permet l'utilisation de la sessions dans un bloc `with` permettant une gestion automatique de l'ouverture, fermeture, erreur et rollback.
> - Une méthode `init_db` permettant la création de la base de donnée. 

#### Fichier `app/database/sql_db.py`

6. Importez l'objet `Base` contenant toutes les métadonnées des modèles SQLAlchemy. 
7. Complétez la propriété `engine`: il faut créer le moteur SQLAlchemy permettant la connection à la base de donnée locale et l'enregistrer dans l'attribut `self._engine`.
    - Utilisez une `f_string` pour insérer dynamiquement l'attribut `self.db_path` 
8. Compléter la méthode `session` pour instancier un `sessionmaker()`: associez la `factory` à l'engine de la classe `self._engine`

9. Compléter la méthode `init_db` pour permettre la création de la base de donnée

> 💡Besoin d'aide ? https://docs.sqlalchemy.org/en/21/orm/session_basics.html

### Module `app.schema`

#### Fichier `app/schemas/document_schema.py`

L'ORM est paramétré, et la base de donnée configurée. Lors de l'interaction avec la base de donnée, les objets SQLAlchemy qui sont générés via `models` sont liés à la session, et sont persistents dans le block `with` de requête de la base de donnée. Afin de structurer l'information, et de détacher l'objet de la base de donnée, nous allons utiliser un schema `Pydantic` pour pouvoir conserver les données de requête après lecture.

> ⚠️`Pydantic` permet une communication efficace entre les objets de l'ORM et la récupération de données; il faut bien veiller à avoir une correspondance parfaite entre le `model` et le `schema`.

10. Créer la classe `DocumentSchema`, qui doit présenter une parfaite symmétrie avec le `model` précédemment codé.
11. Configurer l'attribut `model_config` pour permettre une génération de l'objet directement via les attributs d'un autre objet (dans notre cas, les attributs de notre `model`)

> 💡Pour vous aider: https://docs.pydantic.dev/latest/#pydantic-examples

### Module `app.services`

Il est maintenant temps d'exploiter notre entrepôt de données ! Le fichier `document_services.py` contient toute la logique CRUD de la table document de notre entrepôt.

#### Fichier `app/schemas/document_service.py`

12. Implémenter la méthode `get_all()`
    - La méthode doit retourner une liste de tous les documents présent en base de donnée.
    - Les données doivent être générées dans l'objet `DocumentSchema` pydantic (il est possible de créé l'objet pydantic attribut par attribut, mais peut être que la méthode `model_validate()` peut vous aider)
    
14. Implémenter la méthode `get_by_id()`
    - La méthode doit renvoyer un unique `DocumentSchema`
    - La méthode doit lever une erreur si l'id ne correspond à aucun document.
    
16. Implémenter la méthode `create()`
    - La méthode doit pouvoir créer une nouvelle entrée dans la table à partir d'un fichier pdf.
    - la méthode doit renvoyer un `DocumentSchema` représentant la nouvelle entrée après insertion.
    - La synchronisation avec la chroma_db (pour la recherche vectorielle) est déjà implémentée.
    
## Communication services / client

Nos services sont fonctionnels et ne demandent plus qu'à être utilisés depuis notre interface. Il nous faut un pont entre notre backend et notre frontend, c'est le rôle de l'[AJAX](https://fr.wikipedia.org/wiki/Ajax_(informatique)). 

### Initialiser les services

Avant toute chose, il nous faut instancier nos services et initialiser notre base de données au lancement de l'app. Nous allons exposer deux services à notre interface :
1. `DocumentService` pour afficher et ajouter des documents dans la base de données
2. `RagService` pour faire des requêtes RAG au LLM.

#### Fichier `app/__init__.py`

3. Importer l'objet `db` de notre base de données SQLite
4. Importer nos deux services `RagService` et `DocumentService`
5. Appeler la méthode `init_db` après avoir créé l'app dans la méthode `create_app()`
6. Nous voulons instancier nos services dans le contexte de l'application Flask, pour que ceux-ci puissent être utilisés depuis l'AJAX.
    - Créer une instance pour chaque service dans `app.app_context()`.
    - Corriger le typage en définissant le type de ces instances dans la classe `AppContext`.
    
### Premiers endpoints

Nous allons créer dans le fichier ajax des endpoints sous forme de fonctions. Ces endpoints vont pouvoir être appelés depuis JavaScript pour modifier l'interface. 

#### Fichier `app/ajax.py`

Commençons par implémenter le bloc "conversations". Le endpoint `render_conversations` doit retourner le bloc de conversations. C'est une liste des conversations enregistrées dans l'app.

7. Créer un endpoint `GET` à l'adresse `render_conversations` :
```python
@ajax.route('render_conversations', methods=['GET'])
def render_conversations():
    ...
```
8. Utiliser le `RagService` du contexte de l'application pour récupérer la liste de toutes les sessions LLM. _Le `llm_handler` permet de gérer la création et la récupération des sessions._
9. Créer une liste `session_content` qui contient un dictionnaire pour chacune des sessions avec les clés :
```json
name: session.name
id: session.id
```
10. Aller voir la template `content-list.html` dans `app/templates/elements/` et observer les variables. Il y en a 5, sans compter les éléments de la liste.
11. Renvoyer cette template depuis le endpoint, en lui passant les variables nécessaires. _Vous retrouverez les icônes disponibles dans le dossier `app/static/images/`. Utiliser [url_for](https://flask.palletsprojects.com/en/stable/tutorial/static/) pour passer le lien des icônes_

#### Fichier `app/static/js/chat.js`

Ce script contient la logique de notre interface, c'est lui qui requête nos endpoints AJAX. 

12. Regarder la fonction `renderConversations()`, elle fait une requête au endpoint que nous venons de créer et crée le bloc de conversations depuis le HTML renvoyé.
13. En bas du script, ajouter un event listener sur l'événement [DOMContentLoaded](https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event). Cet événement est déclenché lorsque la page finit de charger. Appeler la fonction `renderConversations()` dans cet event listener.

Recharger la page sur votre navigateur et vérifier que le bloc de conversation s'affiche correctement.
> 💡 Nous travaillons avec deux langages et avons donc deux consoles. La première est notre terminal Python, que nous connaissons bien. La deuxième est le devtool, c'est la console JS intégrée à votre navigateur. Faites `Clic droit > Inspecter` et trouvez l'onglet `Console` pour y accéder.

**Refaire la même chose pour le bloc "documents" :**
- Créer un endpoint `render_documents`
- Collecter la liste des documents du `DocumentService`
- Renvoyer la template `content-list` adaptée au bloc "documents" cette fois-ci.
- Appeler la fonction `renderDocuments()` en JS quand le DOM est chargé.

### Afficher une conversation

Il faut implémenter le chargement des conversations (pour l'instant, rien ne se passe en cliquant sur une conversation). Comme pour les deux endpoints précédents, nous renvoyons une template HTML qui sera intégrée à la page depuis JS.

#### Fichier `app/ajax.py`

14. Créer un [endpoint dynamique](https://codesignal.com/learn/courses/introduction-to-flask-basics/lessons/using-path-parameters-in-dynamic-routes) `render_session/<session_id>`. Ici nous avons un paramètre dans le chemin de l'URL qui définit l'ID de la session à renvoyer.
15. Récupérer la session correspondant à l'ID depuis le `llm_handler`
16. Aller voir les templates `chat-tab.html` et `chat-conversation.html`. La première prend l'id et le nom de la session comme arguments, la deuxième prend l'id de session et la liste de messages.
17. Renvoyer un JSON contenant les deux templates, avec les clés `tab` et `conversation` :
    ```json
    tab: chat-tab (HTML)
    conversation: chat-conversation (HTML)
    ```
    > 💡 La fonction [jsonnify](https://www.geeksforgeeks.org/python/use-jsonify-instead-of-json-dumps-in-flask/) permet de renvoyer un objet JSON depuis un endpoint

#### Fichier `app/static/js/chat.js`

18. Retourner dans la fonction `renderConversations()`, elle appelle la fonction `openConversation()` lors d'un clic ou de la création d'une nouvelle conversation.
19. Finir l'implémentation de la fonction `openConversation()` :
    - Appeler le nouveau endpoint (`fetch`) et lire son contenu JSON (`.json()`). 
    > ⚠️ Attention, ces deux méthodes sont asynchrones, elles retournent une [Promise](https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Operators/await) et il nous faut donc attendre le résultat de cette `Promise`.
    - Créer l'élément `li`, changer son contenu HTML par le `chat-tab` template et ajouter ce nouvel élément à `chatHeader` [comme enfant](https://developer.mozilla.org/en-US/docs/Web/API/Node/appendChild)
    - Changer le contenu HTML de `chatConv` par le `chat-conversation` template

Recharger la page du navigateur, il est maintenant possible de cliquer sur les conversations pour les ouvrir.

### Envoyer et recevoir des messages

#### Fichier `app/templates/elements/chat-conversation.html`

20. Trouver le formulaire d'envoi de message (balise `<form>`)
21. Noter le nom des champs du formulaire (`session_id` et `query`)

#### Fichier `app/ajax.py`

22. Créer un endpoint `POST` `send_message`
23. Les champs du formulaire de `chat-conversation` seront envoyés, ils sont accessibles en python via `request.form.get('nom_du_champs')`. Vérifiez que les deux champs ne sont pas nuls, sinon retourner un [message d'erreur avec un status 400](https://www.geeksforgeeks.org/python/use-jsonify-instead-of-json-dumps-in-flask/)
24. Utiliser la méthode `make_query` du `RagService` pour faire tourner la pipeline de RAG et faire une requête au LLM
25. Renvoyer un JSON contenant la réponse et le contexte avec les clés `response` et `context` :
    ```json
    response: LLM response
    context: Context used for rag
    ```
> 💡 Utiliser `.model_dump()` pour transformer un objet pydantic en JSON

#### Fichier `app/static/js/chat.js`

26. Retourner dans la fonction `openConversation()`, on veut appeler la fonction `sendMessage()` lorsque le formulaire `chatForm` est envoyé (lorsqu'on envoie un message) :
    - Ajouter un event listener pour l'évènement `submit` sur l'élément `chatForm`.
    - Empêcher le rechargement de la page ([événement par défaut](https://developer.mozilla.org/fr/docs/Web/API/Event/preventDefault) lors d'un submit)
    - Appeler la fonction `sendMessage()` avec le formulaire comme argument
27. Dans la fonction `sendMessage()`, faire une requête à notre nouveau endpoint (méthode POST et le `formData` en tant que body).
28. Créer une fonction `displayMessage()` au-dessus de `sendMessage()`, cette fonction prend un `message` et un `role` comme arguments
29. Dans cette fonction:
    - [Sélectionner](https://developer.mozilla.org/fr/docs/Web/API/Document/querySelector) l'élément avec la classe **"chat-conversation"** et lui retirer la [classe](https://developer.mozilla.org/en-US/docs/Web/API/Element/classList) **"empty"**.
    - Créer un nouvel élément `li`, changer son inner HTML pour `message`, ajouter la variable `role` à sa liste de classes.
    - Sélectionner l'élément `ul` avec la classe **"messages"** et lui ajouter l'élément `li` comme enfant.
30. Appeler cette nouvelle fonction `displayMessage()` dans `sendMessage()` pour afficher le message de l'utilisateur puis la réponse du LLM

> 💡 L'utilisation de [sélecteurs CSS](https://www.w3schools.com/jsref/met_document_queryselector.asp) vous sera utile pour retrouver les éléments du DOM depuis JS

Poser une question au chatbot et vérifier le bon fonctionnement de l'application

### Créer une conversation / ajouter un document

Nous voulons faire apparaître une popup formulaire lors de la création d'une conversation ou de l'ajout d'un document.

#### Fichier `app/ajax.py`

31. Créer un endpoint `create_session_popup` qui renvoie la template `create-session-popup.html`
32. Créer un endpoint `POST` `create_session` qui permet de créer une session avec un nom spécifique et renvoie un JSON avec l'ID de la session créée sous la clé `session_id`.

> 💡 Le formulaire de la template `create-session-popup` sera utilisé pour requêter le deuxième endpoint. Allez voir le contenu de son formulaire pour connaître le nom des champs.

#### Fichier `app/static/js/popups.js`

La fonction `createConversationPopup()` implémente déjà les deux appels aux endpoints que vous venez de créer. Elle requête le HTML de la popup, l'ajoute à la page et attend que le formulaire soit envoyé pour créer une nouvelle conversation.

33. [Envoyer un événement](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent/CustomEvent) nommé `conversationCreated` une fois la session créée :
    - Ajouter l'ID de la session créée sous la clé `sessionId` du `detail` de l'événement
    - Activer les bubbles
    - Envoyer l'événement sur l'élément `popup`
34. Ajouter le keyword `export` devant la fonction afin de pouvoir l'utiliser dans notre script principal

#### Fichier `app/static/js/chat.js`

35. Importer la fonction `createConversationPopup()` au sommet du script :
```js
import { createConversationPopup } from './popups.js';
```
36. Dans la fonction `renderConversations()` :
    - Appeler la fonction `createConversationPopup()` au clic sur le bouton de création de conversation. 
    - Récupérer l'élément `popup` renvoyé par la fonction puis ajouter un event listener sur la popup afin de savoir quand une conversation est créée. 
    - Appeler alors `renderConversations()` et `openConversation()` avec l'ID de la nouvelle session.

> 💡 Attention avec les fonctions asynchrones, comme précédemment il faut utiliser le keyword `await` pour récupérer l'élément renvoyé.

**Refaire la même chose pour la popup de création de document** :
- Regarder les champs du formulaire de `create-doc-popup.html`
- Créer le endpoint `create_document_popup`
- Créer le endpoint `create_document` (utiliser `file.filename` et `file.read()` pour avoir le nom et le contenu binaire du fichier)
- Exporter et importer la fonction `createDocumentPopup()` en JS
- La fonction `renderDocuments()` est déjà implémentée.

### Servir un document PDF

La dernière étape est de permettre à l'utilisateur de cliquer sur un document pour l'afficher dans une nouvelle fenêtre. Il nous faut créer un dernier endpoint qui va renvoyer le contenu d'un PDF depuis son ID.

#### Fichier `app/static/js/chat.js`

37. Dans la fonction `openDocument()`, regarder la façon dont elle appelle le endpoint `serve_document` que nous allons devoir implémenter. Comment est passé l'ID du document à ouvrir ? Comment est-ce qu'on récupère le contenu du document (on utilise un blob) ?

#### Fichier `app/ajax.py`

38. Créer le endpoint `serve_document`
39. Retrouver un document depuis son ID avec `DocumentService`
40. Renvoyer le blob du document (la fonction [send_file](http://flask.palletsprojects.com/en/stable/api/#flask.send_file) va vous être utile)

## Fin du TD
