# Documentation technique — Agent Windows V4

## 1. Présentation du projet

L'agent Windows V4 fait partie d'un projet universitaire d'Ethical Hacking développé en Python dans un laboratoire VMware autorisé.

L'objectif est de construire une architecture client/serveur permettant :

- La communication entre plusieurs systèmes d'exploitation.
- L'identification des agents connectés.
- La récupération des informations système.
- L'exécution de diagnostics prédéfinis.
- La gestion des connexions et des erreurs.
- L'étude de certaines fonctionnalités de sécurité Windows.

Le projet comprend un serveur Kali Linux V5, un agent Windows 11 V4 et un agent Debian Linux.

Les communications utilisent des sockets TCP et des messages JSON.

## 2. Architecture du laboratoire

| Machine | Adresse IPv4 | Fonction |
|---|---|---|
| Windows principal | `192.168.109.1` | Développement et Git |
| Windows 11 VMware | `192.168.109.134` | Agent Windows V4 |
| Kali Linux VMware | `192.168.109.129` | Serveur TCP V5 |
| Debian Linux VMware | `192.168.109.133` | Agent Linux |

Le réseau de laboratoire principal est VMware VMnet1, configuré en mode Host-only.

Le serveur Kali écoute sur le port TCP `5001`.

Ces adresses IP sont propres à notre environnement de test et peuvent changer selon la configuration des machines virtuelles.

### Fonctionnement général

1. Le serveur Kali V5 est démarré.
2. L'agent Windows V4 est lancé manuellement dans la VM.
3. Windows établit une connexion TCP avec Kali.
4. Windows transmet un message `HELLO`.
5. Kali répond avec `HELLO_ACK`.
6. Kali envoie les demandes de diagnostic.
7. Windows traite les demandes autorisées.
8. Kali reçoit et vérifie les résultats.
9. La session se termine normalement.

Les messages sont transmis en JSON, encodés en UTF-8 et séparés par un retour à la ligne.

## 3. Organisation des fichiers

| Fichier | Fonction |
|---|---|
| `agents/windows/main.py` | Programme principal Windows V4 |
| `agents/windows/commandes_locales.py` | Diagnostics PowerShell autorisés |
| `agents/windows/registry.py` | Écriture locale dans le registre |
| `agents/windows/security_audit.py` | Capture d'écran locale et encodage Base64 |
| `agents/windows/sam_audit.py` | Module expérimental d'audit SAM |
| `shared/protocol.py` | Protocole JSON commun |
| `agent-windows-v4.spec` | Configuration de compilation PyInstaller |
| `serveur/main.py` | Serveur Kali V5 |
| `docs/WINDOWS_AGENT.md` | Documentation technique Windows |

Les anciens fichiers de sauvegarde sont conservés localement, mais ne sont pas inclus dans le dépôt Git final.

## 4. Fonctionnalités Windows validées

### 4.1 Connexion TCP

L'agent utilise le module Python `socket` pour communiquer avec le serveur Kali Linux V5.

Les tests ont confirmé les échanges suivants :

| Message | Fonction | Résultat |
|---|---|---|
| `HELLO` | Identification de l'agent | Réussi |
| `HELLO_ACK` | Confirmation du serveur | Réussi |
| `PING` | Test de communication | Réussi |
| `PONG` | Réponse au serveur | Réussi |
| `SYSINFO` | Demande d'informations système | Réussi |
| `RESULT` | Transmission des résultats | Réussi |
| `CMD` | Diagnostic Windows autorisé | Réussi |
| `ERROR` | Signalement des commandes refusées | Réussi |

Une nouvelle session complète Windows–Kali a été validée le 25 novembre 2026.

Le serveur a reçu les informations de Windows 11 ainsi que le résultat de la commande `date`.

La session s'est terminée avec le message de réussite du serveur Kali V5.

### 4.2 Récupération des adresses IPv4

La fonction `get_real_ips()` récupère les adresses IPv4 à partir des interfaces réseau disponibles.

Le programme utilise `psutil` et exclut les adresses commençant par `127.`.

Pendant les tests sur le Windows principal, plusieurs adresses ont été observées :

- Wi-Fi : `192.168.1.187`.
- VMware VMnet1 : `192.168.109.1`.
- VMware VMnet8 : `192.168.104.1`.

Dans la VM Windows 11, l'agent a correctement identifié l'adresse `192.168.109.134`.

La fonction ne filtre pas nécessairement toutes les interfaces virtuelles ni toutes les adresses de liaison locale.

### 4.3 Informations système

Lorsque Windows reçoit une demande `SYSINFO`, le programme collecte des informations générales sur le système.

Les informations transmises comprennent notamment :

- Le système d'exploitation.
- Sa version.
- Le nom de l'ordinateur.
- Les adresses IPv4 disponibles.

La réponse est envoyée au serveur Kali sous forme d'un message JSON `RESULT`.

Le fonctionnement a été validé pendant les tests de connexion entre Windows 11 et Kali V5.

### 4.4 Exécution contrôlée de commandes PowerShell

Le fichier `commandes_locales.py` utilise une liste de commandes autorisées.

Les trois diagnostics disponibles sont :

| Commande | Fonction |
|---|---|
| `date` | Afficher la date et l'heure |
| `ordinateur` | Afficher le nom de l'ordinateur |
| `windows` | Afficher la version de Windows |

Les commandes sont exécutées avec `subprocess.run()` et `shell=False`.

Un délai maximal de dix secondes est prévu.

Une commande absente de la liste autorisée est refusée.

#### Résultats des tests du 25 novembre 2026

Les trois commandes ont été exécutées localement sur le Windows principal.

- `date` : réussite, code de retour `0`.
- `ordinateur` : réussite, nom retourné `MESDI`.
- `windows` : réussite, version Windows retournée.
- `commande_inconnue` : refusée avec le message `Commande non autorisee`.

Le diagnostic `date` a également été validé de bout en bout entre l'agent Windows 11 et Kali V5.

Les commandes `ordinateur` et `windows` n'ont pas fait l'objet d'une nouvelle validation distante pendant cette session.

### 4.5 Gestion des erreurs réseau

La version V4 prévoit un mécanisme limité de nouvelles tentatives de connexion.

Les paramètres utilisés sont :

- Nombre maximal de tentatives : **3**.
- Intervalle entre les tentatives : **3 secondes**.
- Délai maximal de connexion : **10 secondes**.

Une tentative de connexion vers `127.0.0.1:59999`, sans serveur disponible, avait permis de tester le traitement d'un refus de connexion.

Après plusieurs tentatives infructueuses, l'agent s'arrête.

Une fermeture normale par Kali ne provoque pas de nouvelle connexion automatique.

La reconnexion après une coupure d'une session déjà établie n'a pas été validée séparément.

## 5. Fonctionnalités Windows spécifiques

### 5.1 Modification locale du registre

Le module `registry.py` utilise la bibliothèque Python `winreg`.

La clé de test est :

`HKEY_CURRENT_USER\Software\MonProjetTP`

La valeur configurée est :

- Nom : `Status`.
- Type : `REG_SZ`.
- Donnée : `Actif`.

Le module Python avait déjà été testé sur le Windows principal.

Le 25 novembre 2026, une création manuelle de cette clé a également été réalisée dans la VM Windows 11 avec la commande `reg add`.

Une interrogation avec `reg query` a confirmé que la valeur `Status REG_SZ Actif` était bien présente.

**Limite :** le traitement du message `REGISTRY` dans `main.py` renvoie actuellement une réponse informative. Il n'appelle pas la fonction `add_registry_key()`.

L'intégration de cette opération à l'agent réseau n'est donc pas validée.

### 5.2 Capture d'écran locale

Le module `security_audit.py` utilise `PIL.ImageGrab` pour capturer l'écran.

Il effectue les opérations suivantes :

1. Capture de l'écran local.
2. Conversion de l'image au format PNG en mémoire.
3. Encodage de l'image en Base64.
4. Retour d'un dictionnaire contenant le statut et l'image encodée.

Le 25 novembre 2026, un nouveau test local a donné :

```text
Statut: success
Image generee: True
```

Ce résultat confirme le fonctionnement du module sur le Windows principal.

L'encodage Base64 ne constitue pas une protection cryptographique.

**Limite :** la capture dans la VM Windows 11 n'a pas été validée. Le message `SCREENSHOT` de l'agent principal renvoie actuellement une information de disponibilité sans exécuter la capture.

### 5.3 Module expérimental SAM

Le fichier `sam_audit.py` contient une procédure expérimentale concernant les ruches protégées `SAM` et `SYSTEM` du registre Windows.

Ces données sont sensibles et leur accès est soumis aux protections du système d'exploitation.

Le code prévoit le traitement des erreurs et le nettoyage des fichiers temporaires.

La vérification de syntaxe du module a réussi le 25 novembre 2026.

Cependant :

- La récupération effective de la base SAM n'a pas été démontrée.
- Les restrictions d'accès Windows restent applicables.
- Le module n'est pas appelé par le programme principal Windows V4.

La présence du code et la réussite de sa compilation ne constituent pas une preuve de récupération de données SAM.

### 5.4 Vérification de Microsoft Defender

Des vérifications locales antérieures ont montré que plusieurs protections Microsoft Defender étaient activées au moment des tests :

- Protection antivirus.
- Protection en temps réel.
- Protection contre les logiciels espions.

Ces observations ne constituent pas un audit complet de la sécurité Windows.

## 6. Démarrage de l'agent Windows

### 6.1 Lancement manuel

L'agent Windows V4 peut être lancé depuis la VM avec le fichier :

`lancer-agent.bat`

Ce fichier exécute l'agent en utilisant :

- Serveur : `192.168.109.129`.
- Port : `5001`.

Le lancement manuel a été testé avec succès le 25 novembre 2026.

Windows a transmis ses réponses et Kali V5 les a correctement reçues.

### 6.2 Vérification du démarrage automatique

Plusieurs vérifications ont été réalisées dans Windows 11 :

- Recherche dans les tâches planifiées : aucune entrée trouvée sous le nom de l'agent.
- Dossier de démarrage utilisateur : vide.
- Clé `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` : seule une entrée OneDrive était présente.
- Recherche d'un service Windows portant le nom de l'agent : aucun résultat.
- Niveau d'intégrité du CMD : moyen.

**Conclusion : le démarrage automatique de l'agent Windows au lancement de la VM n'est pas configuré ni validé.**

Le lancement manuel ne doit pas être présenté comme un démarrage automatique.

## 7. Compilation avec PyInstaller

### 7.1 Environnement de compilation

Le 25 novembre 2026, une nouvelle compilation a été réalisée sur le Windows principal avec :

- Python : **3.15.2**.
- PyInstaller : **6.22.3**.
- Système : Windows 11.

Le fichier de configuration utilisé est :

`agent-windows-v4.spec`

### 7.2 Commande de compilation

Depuis la racine du dépôt :

```cmd
python -m PyInstaller --noconfirm --clean agent-windows-v4.spec
```

La compilation s'est terminée avec le message :

`Build complete!`

Le nouvel exécutable a été généré dans :

`dist\agent-windows-v4.exe`

Taille du nouvel exécutable : **9 722 365 octets**.

### 7.3 Comparaison avec la version déjà testée

| Version | Taille | État |
|---|---:|---|
| V4 présente dans VMware | 9 723 009 octets | Communication Kali validée |
| Nouvelle V4 recompilée | 9 722 365 octets | Compilation validée |

La nouvelle version a également répondu à l'option `--help`, démontrant que l'exécutable pouvait être lancé localement.

Elle n'a pas encore fait l'objet d'un test complet de communication dans la VM.

L'ancienne version reste celle qui a été validée entre Windows 11 et Kali V5.

### 7.4 Dépendances

Le fichier `requirements.txt` indique :

- `psutil`.
- `Pillow`.
- `pyinstaller`.

La commande `python -m pip check` exécutée sur le Windows principal a retourné :

`No broken requirements found.`

Cela confirme l'absence de conflits détectés entre les paquets installés dans cet environnement.

## 8. Intégration avec Kali et Debian

### 8.1 Intégration Windows–Kali

Le serveur Kali V5 possède les composants suivants :

- Gestion des connexions TCP.
- Gestion des clients.
- Interprétation des diagnostics.
- Traitement des erreurs.
- Gestion de plusieurs connexions par threads.

Les tests ont validé la communication entre le serveur Kali V5 et l'agent Windows V4.

Le serveur utilise `ThreadPoolExecutor` avec une capacité configurée de quatre sessions simultanées.

Deux connexions TCP parallèles ont été testées avec succès.

La capacité de quatre connexions simultanées reste à valider.

### 8.2 Intégration Debian–Kali

L'intégration de base de l'agent Debian a été effectuée et testée.

Le 25 novembre 2026, le serveur Kali V5 a reçu les résultats suivants :

- Identification `HELLO / HELLO_ACK`.
- Diagnostic `PING / PONG`.
- Informations système `SYSINFO`.
- Diagnostic `interfaces`.

La réponse au diagnostic `interfaces` comprenait :

| Interface | Adresse IPv4 |
|---|---|
| `lo` | 127.0.0.1 |
| `ens33` | 192.168.109.133 |
| `ens37` | 192.168.104.135 |

Le serveur a confirmé la réussite de la session.

Les autres fonctionnalités Linux, notamment les traitements relatifs aux fichiers système, aux parcours de répertoires et à la capture d'écran, nécessitent encore une validation individuelle.

## 9. Résultats des tests

| Test effectué | Résultat |
|---|---|
| Communication Windows 11 ↔ Kali V5 | Réussi |
| Identification HELLO / HELLO_ACK | Réussi |
| PING / PONG | Réussi |
| SYSINFO / RESULT | Réussi |
| Diagnostic Windows `date` via Kali | Réussi |
| Diagnostics locaux `date`, `ordinateur`, `windows` | Réussi |
| Refus local d'une commande inconnue | Réussi |
| Gestion d'une connexion refusée | Testée |
| Trois tentatives de connexion V4 | Testées |
| Exécution de la V4 dans VMware | Réussi |
| Création manuelle d'une clé de registre dans la VM | Réussi |
| Fonction Python `registry.py` sur Windows principal | Réussi |
| Intégration distante du registre | Non validée |
| Capture d'écran locale sur Windows principal | Réussi |
| Capture d'écran dans la VM | Non validée |
| Capture déclenchée par Kali | Non validée |
| Module SAM | Syntaxe validée uniquement |
| Récupération effective SAM | Non validée |
| Démarrage automatique Windows | Non validé |
| Communication Debian ↔ Kali | Réussi |
| Diagnostic Linux `interfaces` | Réussi |
| Deux sessions TCP parallèles | Réussi |
| Quatre sessions simultanées | Non validé |
| Compilation PyInstaller V4 | Réussi |
| Lancement local du nouvel EXE avec `--help` | Réussi |
| Test réseau du nouvel EXE recompilé | Non validé |

## 10. Gestion des versions et GitHub

Le code est conservé dans le dépôt GitHub :

https://github.com/Idi18/projet-ethical-hacking

La branche actuellement utilisée pour l'intégration est :

`integration-finale`

Des branches et versions antérieures ont été utilisées pendant le développement, notamment `windows-integration`.

Parmi les commits importants figurent :

- `b31a146` : intégration des diagnostics Windows contrôlés.
- `372885d` : amélioration de la gestion des erreurs Windows.
- `b23e3a0` : actualisation du README.
- `44b6696` : ajout du message `INTERFACES` au protocole.
- `ef6b44a` : ajout du fichier de configuration PyInstaller V4.

Dernier commit confirmé lors de la rédaction de ce document : **`ef6b44a`**.

Une archive nommée `projet-ethical-hacking-final.zip` a été générée à partir de la branche `integration-finale`.

Elle contient le code source et la configuration de compilation PyInstaller V4.

Le fichier exécutable compilé n'est pas inclus dans cette archive Git à ce stade.

L'archive devra être régénérée après toute nouvelle modification enregistrée dans le dépôt.

## 11. Preuves et captures

Des captures d'écran ont été réalisées tout au long du développement.

Les preuves historiques comprennent notamment :

| Numéro | Preuve |
|---|---|
| 23 | Communication TCP Windows–Kali côté serveur |
| 24 | Communication TCP Windows–Kali côté agent |
| 27 | Vérification des permissions SAM |
| 28 | Vérification du registre Windows |
| 29 | État des protections Microsoft Defender |
| 30 | Gestion d'une connexion refusée |
| 31 | Gestion d'une commande inconnue |
| 32 | Diagnostics PowerShell locaux |
| 33 | Refus d'une commande non autorisée |
| 34 | Diagnostic CMD Windows–Kali |
| 35 | Exécutable Windows V3 côté Windows |
| 36 | Exécutable Windows V3 côté Kali |
| 37 | Tentatives de connexion Windows V4 |
| 38 | Exécutable Windows V4 côté Windows |
| 58 | Interfaces réseau Debian reçues par Kali V5 |
| 59 | Communication Windows V4 et résultats reçus par Kali V5 |

Les numéros correspondent au suivi des tests effectué pendant le projet.

La présence effective de toutes les images dans le dossier de livraison doit être vérifiée séparément.

## 12. Limites et éléments à finaliser

Les principales limites du projet sont les suivantes :

**Démarrage automatique Windows :** non validé. Le lancement de l'agent est actuellement manuel.

**Capture d'écran Windows :** le module fonctionne localement sur le Windows principal, mais son exécution par l'agent réseau et son fonctionnement dans la VM ne sont pas démontrés.

**Registre Windows :** création manuelle réussie dans la VM et fonction Python testée sur le Windows principal, mais déclenchement par l'agent non intégré.

**Audit SAM :** module expérimental présent, récupération effective des données non démontrée.

**Agent Debian :** connexion et diagnostic réseau validés. Les autres traitements Linux nécessitent les confirmations et preuves du second membre du groupe.

**Connexions simultanées :** deux sessions TCP parallèles ont été testées ; la capacité maximale configurée de quatre n'a pas été vérifiée.

**Sécurité réseau :** aucune authentification applicative ni protection TLS n'a été démontrée.

**Documentation et remise :** la branche d'intégration et l'archive ZIP doivent être actualisées après les dernières modifications.

Toutes les expérimentations ont été limitées à un environnement VMware autorisé.

## 13. Conclusion

Le projet a permis de développer et de tester une architecture client/serveur Python entre Windows 11, Kali Linux et Debian.

L'agent Windows V4 assure l'identification, la récupération d'informations système, l'exécution de diagnostics contrôlés et la gestion des erreurs réseau.

Le serveur Kali V5 reçoit et valide les réponses de l'agent Windows. Les tests ont confirmé le fonctionnement des diagnostics `PING`, `SYSINFO` et `date`.

La communication Debian–Kali et la récupération des interfaces réseau ont également été validées.

La recompilation de l'exécutable Windows V4 avec PyInstaller 6.22.3 a réussi le 25 novembre 2026.

Les fonctionnalités restant à vérifier sont distinguées des résultats validés afin que la documentation reflète fidèlement l'état réel du projet avant la remise du 27 novembre 2026.