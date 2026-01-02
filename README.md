# Sentiment Analysis Web App (Flask)

Une **application web Flask** qui analyse le **sentiment d’un texte** (positif, négatif, neutre) via une interface web simple.  
Le projet peut fonctionner en **mode démo** ou en utilisant l’**API IBM Watson Natural Language Understanding**.

---

## Fonctionnalités

- Analyse de sentiment d’un texte saisi par l’utilisateur
- Affichage du résultat avec :
  - Sentiment : POSITIVE / NEGATIVE / NEUTRAL
  - Score et confiance
  - Mode utilisé : `demo` ou `watson`
- Interface web simple (HTML + JavaScript)
- Mode démo pour tester sans clé Watson
- Mode Watson pour une analyse plus précise (API cloud IBM)

---

## Structure du projet

sentiment-analysis-app/
```
│
├─ app.py # Application Flask principale
├─ requirements.txt # Dépendances Python
├─ .gitignore # Fichiers à ignorer
├─ README.md
├─ src/
│ ├─ utils.py # Fonctions utilitaires (validation, formatage)
│ └─ sentiment_analyzer.py # Intégration Watson
├─ static/
│ └─ js/
│ └─ app.js # JS pour l’UI
└─ templates/
└─ index.html # Interface utilisateur
```


## Mode de fonctionnement

L’utilisateur saisit un texte dans l’interface.

Le navigateur envoie une requête POST /analyze avec le texte en JSON.

Flask traite la requête :

Valide le texte

Si Watson configuré → appel API Watson

Sinon → mode démo (simulation)

Flask renvoie un JSON avec le résultat.

Le JS côté client affiche le résultat dans la page.

## Limitations et remarques

Mode démo : simulation basée sur des mots positifs/négatifs → moins fiable.

Mode Watson : dépend d’un service cloud IBM → nécessite clé API et connexion internet.

Les champs score et confidence sont à interpréter comme indicatifs, surtout en mode démo.

L’application ne contient pas de modèle ML local pour l’instant.

## Contributions

Les contributions sont les bienvenues !
Pour proposer des améliorations :

Forker le projet

Créer une branche (feature/ma-feature)

Committer vos changements

Ouvrir un Pull Request
