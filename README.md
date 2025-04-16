
# API E-commerce (Flask + SQLAlchemy)

## Description
Cette API RESTful propulse la gestion d’une boutique en ligne : inscription/authentification, produits, commandes, gestion des rôles, sécurité JWT, tout est prévu pour une expérience robuste, évolutive et éducative.

---

## Prérequis
- Python 3.8+
- pip
- Virtualenv (optionnel)
- Base de données compatible SQLAlchemy (SQLite, PostgreSQL, MySQL...)
- git

---

## Installation
1. Cloner le dépôt :  
   ```bash
   git clone https://github.com/votre-utilisateur/api-ecommerce.git
   ```
2. Créer un environnement virtuel (optionnel) :  
   ```bash
   python -m venv venv && source venv/bin/activate
   ```
3. Installer les dépendances :  
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration
- Créer un fichier `.env` à la racine avec les clés nécessaires (`SECRET_KEY`, `DATABASE_URL`…)

---

## Lancement
- Lancer l’API :  
   ```bash
   flask run
   ```
- Par défaut, l'API est disponible sur : [http://localhost:5000](http://localhost:5000)

---

## Authentification
- Après inscription/connexion, récupérer un token **JWT**.
- Utiliser le header suivant pour vos requêtes protégées :
  ```
  Authorization: Bearer <VOTRE_TOKEN>
  ```
- Protection d’accès selon le rôle (admin ou utilisateur).

---

## Endpoints

### Utilisateurs / Auth
| Méthode | Chemin                | Description                        |
|:--------|:-----------------------|:-----------------------------------|
| POST    | `/auth/register`        | Créer un utilisateur               |
| POST    | `/auth/login`           | Connexion et obtention du token JWT |

### Produits
| Méthode | Chemin                           | Description                        |
|:--------|:----------------------------------|:-----------------------------------|
| GET     | `/products`                       | Lister les produits                |
| GET     | `/product/<product_id>`            | Détail d’un produit                |
| POST    | `/product`                         | Ajouter un produit (admin)         |
| PUT     | `/product/<product_id>`            | Modifier un produit (admin)        |
| DELETE  | `/product/<product_id>`            | Supprimer un produit (admin)       |

### Commandes
| Méthode | Chemin                            | Description                                      |
|:--------|:-----------------------------------|:-------------------------------------------------|
| GET     | `/commands`                        | Lister les commandes de l’utilisateur (admin : toutes) |
| GET     | `/command/<command_id>`             | Détail d’une commande                           |
| GET     | `/command/<command_id>/lign`         | Lignes d’une commande                           |
| POST    | `/command/`                         | Passer une commande                             |
| PATCH   | `/command/<command_id>`              | Changer le statut (admin)                       |

---

## Exemples

### Authentification

**Inscription**
```bash
  curl -X POST http://localhost:5000/auth/register      -H "Content-Type: application/json"      -d '{"email": "user@example.com", "password": "SuperMotDePasse42"}'
```

**Connexion**
```bash
  curl -X POST http://localhost:5000/auth/login      -H "Content-Type: application/json"      -d '{"email": "user@example.com", "password": "SuperMotDePasse42"}'
```
Réponse :
```json
  {"token":"eyJ0eXAiOiJKV1Q..."}
```

---

### Produits

**Voir tous les produits**
```bash
  curl http://localhost:5000/products
```

**Ajouter un produit (admin)**
```bash
  curl -X POST http://localhost:5000/product      -H "Authorization: Bearer <TOKEN_ADMIN>"      -H "Content-Type: application/json"      -d '{"name": "RTX 4090","description": "Carte graphique haut de gamme","category": "Composant","price": 2000,"stock": 5}'
```

---

### Commandes

**Lister ses commandes**
```bash
  curl http://localhost:5000/commands -H "Authorization: Bearer <VOTRE_TOKEN>"
```

---

## Gestion des erreurs
| Code | Description                              |
|:-----|:-----------------------------------------|
| 401  | Authentification manquante/invalide       |
| 403  | Droits insuffisants                      |
| 404  | Ressource non trouvée                    |
| 400  | Mauvaise requête                         |
| 409  | Conflit (ex: compte déjà existant)        |

**Note :** Toutes les erreurs sont retournées au format JSON.

---

## Contribution
- Forkez ce dépôt
- Créez une branche pour vos changements
- Ouvrez une Pull Request
- Vos contributions sont les bienvenues !

---

## Licence
Projet open source, licence **MIT**

---

© 2025 — Projet pédagogique API E-commerce Flask
