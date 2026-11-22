# Documentation technique — Agent Windows V4

## 1. Présentation du projet

L'agent Windows est une composante du projet universitaire *Ethical Hacking*, développé en Python dans un environnement de laboratoire VMware.

Il établit une connexion TCP avec un serveur de test exécuté sur Kali Linux. Les machines échangent des messages au format JSON selon un protocole commun défini dans `shared/protocol.py`.

L'objectif de cette composante est de démontrer la communication entre machines, la récupération d'informations système, l'exécution contrôlée de diagnostics et la gestion des erreurs réseau.

Les essais ont été réalisés dans un environnement de laboratoire autorisé.

## 2. Architecture du laboratoire

| Machine | Adresse IPv4 | Fonction |
|---|---|---|
| Windows 11 — ordinateur hôte | `192.168.109.1` | Agent Windows |
| Kali Linux — VMware | `192.168.109.129` | Serveur TCP de test |
| Debian Linux — VMware | `192.168.109.133` | Client Linux de test |

Le réseau VMware VMnet1 utilise le mode *Host-only* et le masque `255.255.255.0`.

Ce réseau permet aux machines du laboratoire de communiquer localement sans dépendre d'une connexion Internet.

### Fonctionnement général

1. Le serveur Kali démarre et écoute sur le port TCP `5001`.
2. L'agent Windows est lancé manuellement.
3. Windows établit une connexion TCP avec Kali.
4. L'agent envoie un message `HELLO` contenant son nom, son système d'exploitation et ses adresses IPv4.
5. Le serveur retourne `HELLO_ACK`.
6. Le serveur transmet des demandes compatibles avec le protocole.
7. L'agent traite les demandes autorisées et renvoie les réponses JSON correspondantes.
8. Lorsque le serveur ferme normalement la connexion, l'agent termine sa session.

Les messages JSON sont séparés par des retours à la ligne pour permettre leur lecture sur le flux TCP.

## 3. Organisation des fichiers

| Fichier | Fonction |
|---|---|
| `agents/windows/main.py` | Programme principal de l'agent Windows V4 |
| `agents/windows/commandes_locales.py` | Diagnostics PowerShell autorisés |
| `agents/windows/registry.py` | Modification locale d'une valeur du registre |
| `agents/windows/security_audit.py` | Capture d'écran locale avec encodage Base64 |
| `agents/windows/sam_audit.py` | Module expérimental relatif aux ruches SAM et SYSTEM |
| `shared/protocol.py` | Définition du protocole JSON commun |
| `docs/WINDOWS_AGENT.md` | Documentation technique de l'agent |

Des versions antérieures du programme ont également été conservées pour faciliter les vérifications.

## 4. Fonctionnalités développées et validées

### 4.1 Connexion TCP

L'agent utilise le module Python `socket` pour établir une connexion avec le serveur Kali.

Une connexion réelle entre Windows et Kali a été validée sur le réseau VMware VMnet1.

Les échanges suivants ont été testés :

| Message | Utilité | Résultat |
|---|---|---|
| `HELLO` | Identification de l'agent | Réussi |
| `HELLO_ACK` | Confirmation du serveur | Réussi |
| `PING` | Vérification de la connexion | Réussi |
| `PONG` | Réponse au message PING | Réussi |
| `SYSINFO` | Demande d'informations système | Réussi |
| `RESULT` | Transmission d'un résultat | Réussi |
| `CMD` | Demande d'un diagnostic autorisé | Réussi |
| `ERROR` | Réponse à une demande non autorisée | Réussi |

### 4.2 Récupération des adresses IPv4

La fonction `get_real_ips()` récupère les adresses IPv4 disponibles sur les interfaces réseau de Windows.

Elle utilise `psutil` lorsqu'il est disponible et exclut les adresses de bouclage commençant par `127.`.

Les essais ont notamment confirmé la présence des interfaces :

- Wi-Fi : `192.168.1.187`
- VMware VMnet1 : `192.168.109.1`
- VMware VMnet8 : `192.168.104.1`

D'autres adresses locales ont également été détectées.

La fonction énumère les interfaces IPv4, mais ne filtre pas toutes les interfaces virtuelles ni les adresses de liaison locale `169.254.x.x`.

### 4.3 Informations système

Lorsque l'agent reçoit `SYSINFO`, il récupère des informations générales sur Windows grâce au module Python `platform`.

Les informations retournées comprennent :

- Le système d'exploitation.
- La version du système.
- Le nom de l'ordinateur.

Ces informations sont transmises sous forme de réponse JSON de type `RESULT`.

### 4.4 Diagnostics PowerShell contrôlés

La version V3 a introduit le traitement des messages `CMD`.

Pour limiter les opérations exécutables, l'agent n'accepte que trois diagnostics prédéfinis :

| Diagnostic | Fonction |
|---|---|
| `date` | Afficher la date et l'heure du système |
| `ordinateur` | Afficher le nom de l'ordinateur |
| `windows` | Afficher la version de Windows |

Le module `commandes_locales.py` exécute ces diagnostics avec PowerShell.

Les commandes arbitraires et les arguments non autorisés sont rejetés.

Lorsqu'une demande est refusée, l'agent renvoie un message de type `ERROR` avec le code `COMMAND_NOT_ALLOWED`.

Les tests Windows–Kali ont confirmé la réussite du diagnostic `date` et le rejet d'une commande inconnue.

### 4.5 Gestion des erreurs réseau — Version V4

La version V4 ajoute un mécanisme limité de nouvelles tentatives de connexion.

Paramètres utilisés :

- Nombre maximal de tentatives : **3**
- Délai entre les tentatives : **3 secondes**
- Délai maximal de connexion TCP : **10 secondes**

Si le serveur refuse une connexion, l'agent affiche l'erreur et effectue une nouvelle tentative, jusqu'à atteindre la limite prévue.

Après trois échecs, le programme s'arrête sans afficher de trace d'erreur Python non gérée.

Ce fonctionnement a été vérifié en tentant de joindre `127.0.0.1` sur le port `59999`, sans serveur à l'écoute.

Une fermeture normale de connexion par Kali termine la session sans provoquer de nouvelle tentative.

Le mécanisme de reprise après coupure d'une session déjà établie n'a pas fait l'objet d'un test distinct.

## 5. Fonctionnalités Windows spécifiques

### 5.1 Modification locale du registre

Le fichier `registry.py` utilise le module Python `winreg`.

Il permet de créer une clé dans :

`HKEY_CURRENT_USER\Software\MonProjetTP`

La valeur suivante a été utilisée lors du test :

`Status = Actif`

La création et la lecture de cette valeur ont été validées localement.

Dans `main.py`, le message `REGISTRY` retourne uniquement un statut informatif. Il ne déclenche pas une modification distante du registre.

### 5.2 Capture d'écran locale

Le fichier `security_audit.py` utilise la bibliothèque Pillow et la fonction `ImageGrab.grab()`.

Le module peut :

1. Capturer l'écran dans une session locale.
2. Convertir l'image en PNG en mémoire.
3. Encoder les données de l'image en Base64.
4. Retourner le résultat dans une structure Python.

Cette fonctionnalité a été testée localement.

L'encodage Base64 ne constitue pas une méthode de chiffrement.

Dans `main.py`, le message `SCREENSHOT` retourne un statut informatif et ne déclenche aucune capture distante.

### 5.3 Audit des protections SAM

Le fichier `sam_audit.py` contient une procédure expérimentale liée aux ruches du registre Windows `SAM` et `SYSTEM`.

Ces données sont sensibles et protégées par Windows.

Les vérifications réalisées ont notamment montré que l'accès au fichier SAM était refusé depuis la session de terminal utilisée.

La récupération effective des ruches SAM et SYSTEM n'a pas été démontrée.

Le module expérimental n'est pas intégré au traitement des messages distants de l'agent principal.

### 5.4 Vérification de Microsoft Defender

Une vérification locale de Microsoft Defender a indiqué que les protections suivantes étaient activées au moment du test :

- Antivirus
- Protection en temps réel
- Protection contre les logiciels espions

Ces résultats documentent l'état observé pendant l'essai. Ils ne constituent pas un audit complet de sécurité Windows.

## 6. Compilation et exécution

### 6.1 Exécution du script Python

Depuis la racine du projet, dans CMD Windows :

```cmd
.\venv\Scripts\python.exe agents\windows\main.py --ip 192.168.109.129 --port 5001
```

Le serveur de test doit être démarré sur Kali avant cette commande.

### 6.2 Compilation avec PyInstaller

L'exécutable V4 a été généré avec PyInstaller.

Commande utilisée :

```cmd
.\venv\Scripts\python.exe -m PyInstaller --onefile --clean --noconfirm --name agent-windows-v4 --paths . agents\windows\main.py
```

Résultat :

`dist\agent-windows-v4.exe`

La compilation s'est terminée avec succès.

### 6.3 Exécution de l'exécutable V4

Commande de lancement :

```cmd
.\dist\agent-windows-v4.exe --ip 192.168.109.129 --port 5001
```

L'exécutable V4 a été testé avec succès sur une connexion TCP réelle entre Windows et Kali.

Il a correctement traité les messages d'identification, de diagnostic et de contrôle utilisés par le serveur de test.

## 7. Résultats des tests

| Test effectué | Résultat |
|---|---|
| Communication IP Windows–Kali | Réussi |
| Connexion TCP Windows–Kali | Réussi |
| Échange `HELLO` / `HELLO_ACK` | Réussi |
| Échange `PING` / `PONG` | Réussi |
| Échange `SYSINFO` / `RESULT` | Réussi |
| Diagnostic PowerShell `date` | Réussi |
| Refus d'une commande non autorisée | Réussi |
| Gestion d'une connexion refusée | Réussi |
| Trois tentatives espacées de 3 secondes | Réussi |
| Compilation de l'exécutable V3 | Réussi |
| Test TCP de l'exécutable V3 | Réussi |
| Compilation de l'exécutable V4 | Réussi |
| Test TCP de l'exécutable V4 | Réussi |
| Modification locale du registre | Réussi |
| Capture d'écran locale | Réussi |
| Vérification des protections Defender | Réalisée |
| Vérification des permissions SAM | Accès refusé |
| Démarrage automatique dans la VM | Non validé |
| Intégration au serveur principal | Non réalisée |

Les résultats indiqués comme réussis correspondent uniquement aux scénarios effectivement testés.

## 8. Gestion des versions et GitHub

Le projet utilise Git pour conserver les modifications du code.

Dépôt :

`https://github.com/Idi18/projet-ethical-hacking`

Branche consacrée à l'intégration Windows :

`windows-integration`

Parmi les commits réalisés :

- `b31a146` : intégration des diagnostics CMD contrôlés.
- `372885d` : amélioration de la gestion des erreurs et des tentatives de connexion.

Les deux commits ont été envoyés sur GitHub.

Les exécutables compilés sont disponibles localement dans le dossier `dist`. Leur présence dans le dépôt distant n'a pas été confirmée.

## 9. Preuves et captures

Des captures d'écran documentent les principales étapes du développement et des tests.

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
| 34 | Test CMD Windows–Kali |
| 35 | Test de l'exécutable V3 côté Windows |
| 36 | Validation de l'exécutable V3 côté Kali |
| 37 | Test des trois tentatives de connexion V4 |
| 38 | Test de l'exécutable V4 côté Windows |

Les fichiers de preuve doivent être regroupés et leurs noms vérifiés avant la remise.

Une capture constitue une preuve d'observation, mais ne garantit pas à elle seule la conformité de l'ensemble du projet.

## 10. Limites et éléments à finaliser

Plusieurs limites subsistent.

**Serveur principal :** le dossier `serveur` contient cinq fichiers Python vides dans la copie locale et sur la branche distante `origin/main`, au moment de la vérification. Le serveur de test Kali utilisé pour les validations est distinct du serveur principal.

**Intégration Linux :** la communication avec un client Debian de test a été vérifiée précédemment, mais l'intégration complète de l'agent Linux et du serveur principal reste à confirmer avec le coéquipier.

**Fonctions Windows sensibles :** les messages `REGISTRY` et `SCREENSHOT` ne déclenchent aucune action distante. Le module SAM expérimental n'est pas intégré au protocole distant.

**Démarrage automatique :** le fonctionnement automatique au démarrage d'une machine virtuelle n'a pas été validé.

**Sécurité réseau :** les échanges TCP du laboratoire ne disposent pas d'un mécanisme d'authentification et de chiffrement applicatif démontré. Les tests doivent rester dans l'environnement isolé et autorisé.

**Ancien processus Windows :** un processus utilisant un ancien exécutable Windows avait été observé. Son origine et son mode de lancement n'ont pas été établis.

**Conformité finale :** toutes les exigences officielles doivent encore être vérifiées lors de l'intégration des différentes composantes.

## 11. Conclusion

Le développement de l'agent Windows a permis de mettre en œuvre et de tester la communication TCP/JSON entre Windows 11 et Kali Linux dans un environnement VMware.

La version V4 dispose de fonctions d'identification, de collecte d'informations système, de diagnostics PowerShell contrôlés, de rejet des commandes non autorisées et de gestion limitée des tentatives de connexion.

L'exécutable V4 a été compilé et testé avec succès.

Les fonctions locales liées au registre Windows, à la capture d'écran et à certaines protections du système ont également été étudiées.

Le travail restant concerne principalement l'intégration au serveur principal, la coordination avec l'agent Linux, la vérification des exigences officielles et la préparation de la remise finale.