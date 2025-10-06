# Guide RBAC pour Débutants Absolus

> Ce guide explique le contrôle d'accès basé sur les rôles (RBAC) comme si vous n'aviez **jamais** fait de programmation. Chaque concept est expliqué avec des analogies de la vie quotidienne.

---

## Table des Matières

1. [C'est quoi RBAC ? (en 5 minutes)](#cest-quoi-rbac)
2. [Les Fondations : Comprendre React](#les-fondations)
3. [Architecture RBAC Étape par Étape](#architecture-rbac)
4. [Le Code Expliqué Ligne par Ligne](#le-code-explique)
5. [Vocabulaire Complet](#vocabulaire)
6. [Erreurs Fréquentes et Solutions](#erreurs-frequentes)

---

## C'est quoi RBAC ?

### L'Analogie de l'Immeuble de Bureaux

Imaginez que vous travaillez dans un **grand immeuble de bureaux**. Vous avez un badge électronique autour du cou.

**Ce badge contient des informations :**
- Votre nom : "Marie Dupont"
- Votre département : "Marketing"
- Vos droits d'accès : une liste de portes que vous pouvez ouvrir

**Les portes de l'immeuble :**

```
🏢 IMMEUBLE "TECHCORP"

Rez-de-chaussée :
├─ 🚪 Hall d'entrée          [OUVERT À TOUS]
│   → N'importe qui peut entrer
│
├─ 🚪 Cafétéria              [Badge "Employé" requis]
│   → Votre badge s'allume en VERT ✅
│   → La porte s'ouvre
│
├─ 🚪 Salle de réunion A     [Badge "Manager" requis]
│   → Votre badge s'allume en ROUGE ❌
│   → La porte reste fermée
│   → Vous n'êtes pas manager
│
└─ 🚪 Salle des serveurs     [Badge "Admin IT" requis]
    → Votre badge s'allume en ROUGE ❌
    → Réservé aux techniciens
```

**RBAC fait exactement la même chose pour votre site web :**

```
💻 APPLICATION WEB "BLOG"

Pages :
├─ 📄 Page d'accueil         [OUVERT À TOUS]
│   → N'importe qui peut voir
│
├─ 📝 Écrire un article      [Permission "articles:create" requise]
│   → Si vous avez la permission → Page s'affiche ✅
│   → Sinon → Message "Accès refusé" ❌
│
├─ 👥 Gérer les utilisateurs [Permission "users:manage" requise]
│   → Réservé aux admins
│   → Si vous n'êtes pas admin → Page invisible ❌
│
└─ ⚙️  Panneau d'administration [Permission "admin:all" requise]
    → Accès complet au système
    → Seulement pour les super-admins
```

### Les 4 Concepts Clés

**1. UTILISATEUR** (vous)
- C'est une personne qui utilise l'application
- Exemple : Marie, Ahmed, Sophie

**2. RÔLE** (votre métier/fonction)
- Un groupe de permissions
- Exemple : "Éditeur", "Admin", "Lecteur"

**3. PERMISSION** (ce que vous avez le droit de faire)
- Une action précise
- Exemple : "créer un article", "supprimer un utilisateur"

**4. RESSOURCE** (sur quoi vous agissez)
- Un élément du système
- Exemple : "article", "utilisateur", "commentaire"

### Exemple Concret : Alice l'Éditrice

```
👤 PROFIL UTILISATEUR
═══════════════════════════════════════
Nom : Alice Martin
Email : alice@blog.com
Rôle : ÉDITEUR
═══════════════════════════════════════

🔑 PERMISSIONS (droits d'accès)
═══════════════════════════════════════
✅ articles:view     → Voir tous les articles
✅ articles:create   → Créer un nouvel article
✅ articles:edit     → Modifier un article
❌ articles:delete   → Supprimer un article (NON)
❌ users:manage      → Gérer les utilisateurs (NON)
❌ admin:all         → Accès admin complet (NON)
═══════════════════════════════════════
```

**Ce qu'Alice peut faire :**

```
Alice ouvre le site web...

1. Page d'accueil
   → ✅ S'affiche (ouvert à tous)

2. Clique sur "Écrire un article"
   → Le système vérifie : Alice a "articles:create" ?
   → ✅ OUI → La page s'affiche

3. Clique sur "Panneau Admin"
   → Le système vérifie : Alice a "admin:all" ?
   → ❌ NON → Message "Accès refusé"
   → (Ou la page ne s'affiche même pas)
```

---

## Les Fondations : Comprendre React

Avant de plonger dans RBAC, vous devez comprendre **4 concepts React de base**.

### Concept 1 : Qu'est-ce qu'un COMPOSANT ?

**Analogie : Les LEGO**

Vous connaissez les LEGO ? Des petites briques que vous assemblez pour construire une maison, une voiture, etc.

En React, c'est pareil :
- Chaque **composant** = une brique LEGO
- Vous assemblez des composants pour construire votre site web

**Exemple visuel :**

```
🏠 MAISON (votre site web)
├─ 🧱 Brique LEGO "Toit"      → Composant <Header />
├─ 🧱 Brique LEGO "Mur"       → Composant <Sidebar />
├─ 🧱 Brique LEGO "Fenêtre"   → Composant <Article />
└─ 🧱 Brique LEGO "Porte"     → Composant <Footer />
```

**Code le plus simple du monde :**

```tsx
// CECI EST UN COMPOSANT (une brique LEGO)
function Bouton() {
  return <button>Cliquez-moi</button>;
}
```

**Traduction en français :**
- `function Bouton()` → "Je crée une brique LEGO appelée 'Bouton'"
- `return` → "Cette brique ressemble à ça :"
- `<button>Cliquez-moi</button>` → Un bouton avec le texte "Cliquez-moi"

**Utilisation (assemblage des LEGO) :**

```tsx
// J'utilise ma brique LEGO 3 fois
<Bouton />
<Bouton />
<Bouton />

// Résultat à l'écran :
// [Cliquez-moi] [Cliquez-moi] [Cliquez-moi]
```

**Composant avec paramètres (brique LEGO personnalisable) :**

```tsx
// Brique LEGO avec un paramètre "couleur"
function Brique({ couleur }) {
  return <div style={{ background: couleur }}>Je suis {couleur}</div>;
}

// Utilisation :
<Brique couleur="rouge" />   // Brique rouge
<Brique couleur="bleue" />   // Brique bleue
<Brique couleur="verte" />   // Brique verte
```

**Vocabulaire :**
- **JSX** : C'est du HTML dans du JavaScript (la syntaxe `<button>...</button>`)
- **Props** : Les paramètres d'un composant (comme `couleur` dans l'exemple)
- **Return** : Ce que le composant affiche à l'écran

---

### Concept 2 : Qu'est-ce qu'un CONTEXT ?

**Analogie : Le Talkie-Walkie Géant**

Imaginez une famille en randonnée. Tout le monde a un talkie-walkie.

**Problème SANS talkie-walkie :**

```
👨‍🦳 Grand-père : "Il va pleuvoir !"
  ↓ crie vers
👨 Papa : "Grand-père dit qu'il va pleuvoir !"
  ↓ crie vers
👧 Fille : "Papa dit que grand-père dit qu'il va pleuvoir !"
  ↓ crie vers
🐕 Chien : "Woof !" (n'a rien compris)
```

**Problème :**
- Le message doit passer de personne en personne
- Ça peut se déformer (comme le jeu "téléphone arabe")
- Tout le monde doit répéter même s'il n'utilise pas l'info

**Solution AVEC talkie-walkie (Context) :**

```
👨‍🦳 Grand-père : [Parle dans le talkie] "Il va pleuvoir !"
  📻 TOUT LE MONDE écoute la même fréquence
👨 Papa : [Écoute] "OK, je prends un parapluie"
👧 Fille : [Écoute] "OK, je rentre"
🐕 Chien : [N'a pas de talkie, s'en fiche]
```

**Avantages :**
- Message diffusé **directement** à tout le monde
- Pas de déformation
- Ceux qui n'en ont pas besoin n'écoutent pas

**En React, le Context fonctionne EXACTEMENT comme ça !**

**Code SANS Context (problème) :**

```tsx
// Grand-père (a l'info)
function App() {
  const meteo = "Il va pleuvoir";
  return <Papa meteo={meteo} />;  // Passe à Papa
}

// Papa (juste un relais, n'utilise pas meteo)
function Papa({ meteo }) {
  return <Fille meteo={meteo} />;  // Passe à Fille
}

// Fille (juste un relais, n'utilise pas meteo)
function Fille({ meteo }) {
  return <Chien meteo={meteo} />;  // Passe à Chien
}

// Chien (utilise enfin meteo)
function Chien({ meteo }) {
  return <div>Météo : {meteo}</div>;
}
```

**Code AVEC Context (solution) :**

```tsx
// 1. Créer le talkie-walkie (fréquence radio)
const MeteoContext = createContext();

// 2. Grand-père émet le message
function App() {
  return (
    <MeteoContext.Provider value="Il va pleuvoir">
      <Papa />
    </MeteoContext.Provider>
  );
}

// 3. Papa, Fille n'ont RIEN à faire
function Papa() {
  return <Fille />;
}

function Fille() {
  return <Chien />;
}

// 4. Chien écoute directement
function Chien() {
  const meteo = useContext(MeteoContext);  // Écoute le talkie
  return <div>Météo : {meteo}</div>;
}
```

**Vocabulaire :**
- **`createContext()`** : Créer la fréquence radio (le talkie-walkie)
- **`Provider`** : L'émetteur (celui qui parle dans le talkie)
- **`value`** : Le message émis
- **`useContext()`** : Le récepteur (celui qui écoute le talkie)

---

### Concept 3 : Qu'est-ce qu'un STATE (État) ?

**Analogie : Le Tableau Blanc Magique**

Imaginez un **tableau blanc dans votre cuisine** où vous notez le nombre de pommes dans le frigo.

**Tableau NORMAL (variable normale) :**

```
Vous : "Tiens, je vais noter le nombre de pommes"
      [Écrit sur un papier : "5 pommes"]

Vous : "J'ai mangé une pomme, je mets à jour"
      [Raye "5", écrit "4"]

Votre frigo : [Affiche toujours "5 pommes"]
              → Le frigo ne se met PAS à jour automatiquement
```

**Tableau MAGIQUE (State) :**

```
Vous : "Tiens, je vais noter le nombre de pommes"
      [Écrit sur le tableau magique : "5 pommes"]
      → Le frigo affiche automatiquement "5 pommes"

Vous : "J'ai mangé une pomme, je mets à jour"
      [Écrit "4" sur le tableau magique]
      → ✨ MAGIE ! Le frigo se met à jour automatiquement : "4 pommes"
```

**En React, le State est ce tableau magique !**

**Code avec variable NORMALE (ne marche pas) :**

```tsx
function Compteur() {
  let nombre = 0;  // Variable normale (papier)

  const manger = () => {
    nombre = nombre + 1;  // J'écris sur le papier
    console.log(nombre);  // Affiche 1, 2, 3... dans la console
    // MAIS l'écran reste à 0 ! (pas de magie)
  };

  return (
    <div>
      <p>Pommes : {nombre}</p>  {/* Reste toujours 0 */}
      <button onClick={manger}>Manger une pomme</button>
    </div>
  );
}
```

**Code avec STATE (tableau magique, ça marche !) :**

```tsx
function Compteur() {
  const [nombre, setNombre] = useState(0);
  //     ↑ valeur  ↑ fonction  ↑ valeur de départ
  //     actuelle  magique

  const manger = () => {
    setNombre(nombre + 1);  // J'utilise la fonction magique
    // ✨ L'écran se met à jour automatiquement !
  };

  return (
    <div>
      <p>Pommes : {nombre}</p>  {/* S'actualise : 0, 1, 2, 3... */}
      <button onClick={manger}>Manger une pomme</button>
    </div>
  );
}
```

**Décortiquons `useState(0)` :**

```tsx
const [nombre, setNombre] = useState(0);
```

**En français :**
1. `useState(0)` → "Crée un tableau magique qui commence à 0"
2. `nombre` → "La valeur actuelle écrite sur le tableau" (0 au début)
3. `setNombre` → "La fonction magique pour écrire une nouvelle valeur"

**Pourquoi c'est "magique" ?**
- Quand vous appelez `setNombre(4)`, React :
  1. Met à jour la valeur de `nombre` à 4
  2. **Re-dessine** automatiquement votre composant
  3. L'écran affiche la nouvelle valeur

**Vocabulaire :**
- **State** : Une variable qui, quand elle change, met à jour l'écran
- **useState** : La fonction pour créer un state
- **Setter** : La fonction pour changer la valeur du state (ex: `setNombre`)

---

### Concept 4 : Qu'est-ce qu'un HOOK ?

**Analogie : Les Super-Pouvoirs de React**

Imaginez que vous êtes un personnage de jeu vidéo. Au début, vous ne savez rien faire.

Puis vous trouvez des **objets magiques** qui vous donnent des pouvoirs :

```
🎮 VOTRE PERSONNAGE (Composant React)

Objet trouvé : 🔮 "Boule de cristal magique"
→ Pouvoir : Créer une variable magique (state)
→ Commande : useState()

Objet trouvé : ⏰ "Montre du temps"
→ Pouvoir : Faire quelque chose après un certain temps
→ Commande : useEffect()

Objet trouvé : 📡 "Antenne radio"
→ Pouvoir : Écouter le talkie-walkie (Context)
→ Commande : useContext()

Objet trouvé : 🧠 "Cerveau qui se souvient"
→ Pouvoir : Se rappeler d'un calcul
→ Commande : useMemo()
```

**En React, ces "objets magiques" s'appellent des HOOKS.**

**Règle de reconnaissance :**
- Tous les hooks commencent par `use`
- `useState`, `useEffect`, `useContext`, `useMemo`, etc.

**Exemple d'utilisation :**

```tsx
function MonComposant() {
  // J'utilise le pouvoir "useState" (boule de cristal)
  const [compteur, setCompteur] = useState(0);

  // J'utilise le pouvoir "useEffect" (montre du temps)
  useEffect(() => {
    console.log("Le composant est apparu !");
  }, []);

  // J'utilise le pouvoir "useContext" (antenne radio)
  const meteo = useContext(MeteoContext);

  return <div>Compteur : {compteur}, Météo : {meteo}</div>;
}
```

**Vocabulaire :**
- **Hook** : Une fonction spéciale React qui donne un pouvoir
- **Built-in hooks** : Hooks fournis par React (`useState`, `useEffect`...)
- **Custom hooks** : Hooks que VOUS créez (commencent aussi par `use`)

**Exemple de Custom Hook (votre propre pouvoir) :**

```tsx
// Vous créez votre propre pouvoir "useCompteurDePommes"
function useCompteurDePommes() {
  const [pommes, setPommes] = useState(5);

  const manger = () => setPommes(pommes - 1);
  const acheter = () => setPommes(pommes + 10);

  return { pommes, manger, acheter };
}

// Utilisation de votre pouvoir
function Cuisine() {
  const { pommes, manger, acheter } = useCompteurDePommes();

  return (
    <div>
      <p>Pommes : {pommes}</p>
      <button onClick={manger}>Manger</button>
      <button onClick={acheter}>Acheter 10 pommes</button>
    </div>
  );
}
```

---

## Architecture RBAC Étape par Étape

Maintenant que vous comprenez les bases, construisons notre système RBAC !

### Vue d'Ensemble : Les 5 Fichiers

Notre système RBAC est comme une **équipe de sécurité dans un bâtiment** :

```
🏢 ÉQUIPE DE SÉCURITÉ RBAC

1. SessionContext.tsx
   👔 Le Chef de la Sécurité
   → Stocke toutes les infos (qui est connecté, quelles permissions)
   → Partage ces infos avec toute l'équipe

2. useSession.ts
   🔍 Le Lecteur de Badges
   → Lit votre badge et vous dit qui vous êtes

3. useCan.ts
   🛡️ Le Vérificateur de Droits
   → Vérifie si vous avez le droit de faire quelque chose

4. Guard.tsx
   🚧 Le Vigile Invisible
   → Bloque l'accès à certaines zones si vous n'avez pas le droit

5. GuardRoute.tsx
   🚪 Le Contrôle Douanier
   → Bloque l'accès à des pages entières
```

**Schéma de fonctionnement :**

```
Utilisateur arrive sur le site
         ↓
SessionContext (Chef de sécurité)
   ↓ charge les infos depuis le serveur
   ↓ stocke : { email: "alice@...", perms: [...] }
   ↓ partage à tout le monde via le talkie-walkie
   ↓
useSession (Lecteur de badge)
   ↓ lit les infos stockées
   ↓ retourne : "Vous êtes Alice"
   ↓
useCan (Vérificateur)
   ↓ vérifie : Alice a "articles:edit" ?
   ↓ retourne : OUI ou NON
   ↓
Guard (Vigile)
   ↓ si OUI → affiche le bouton
   ↓ si NON → masque le bouton (il n'existe même pas)
```

---

## Le Code Expliqué Ligne par Ligne

Nous allons maintenant voir le code de chaque fichier, expliqué comme si vous n'aviez jamais vu du code.

### Fichier 1 : SessionContext.tsx (Le Chef de Sécurité)

**Ce qu'il fait :**
1. Se connecte au serveur pour récupérer les infos utilisateur
2. Stocke ces infos dans sa mémoire
3. Partage ces infos avec tous les composants via le talkie-walkie (Context)

**Analogie complète :**

```
👔 CHEF DE SÉCURITÉ (SessionContext)

Matin, 8h00 :
1. Arrive au bureau
2. Appelle le centre de contrôle (serveur backend)
   "Bonjour, c'est quoi les infos de l'utilisateur connecté ?"
3. Le centre répond :
   "C'est Alice, email alice@blog.com, permissions: [articles:view, articles:edit]"
4. Note tout dans son carnet (state)
5. Allume le talkie-walkie (Provider)
   "À toute l'équipe : notre utilisateur est Alice, voici ses permissions"
6. Toute l'équipe peut maintenant utiliser ces infos
```

**Code commenté LIGNE PAR LIGNE :**

```tsx
// ============================================
// IMPORTS (outils nécessaires)
// ============================================
import { createContext, useState, useEffect, ReactNode } from 'react';
```

**Explication des imports :**
- `createContext` → Créer le talkie-walkie (fréquence radio)
- `useState` → Créer le tableau magique (pour stocker les infos)
- `useEffect` → Faire quelque chose après le démarrage (appeler le serveur)
- `ReactNode` → Type TypeScript pour "n'importe quel contenu React"

```tsx
// ============================================
// DÉFINITION DE LA STRUCTURE DES DONNÉES
// ============================================

// On définit EXACTEMENT à quoi ressemblent les infos utilisateur
interface SessionData {
  sub: string;      // Identifiant unique (ex: "user_123")
  email: string;    // Email (ex: "alice@blog.com")
  perms: string[];  // Liste de permissions (ex: ["articles:view", "articles:edit"])
}
```

**Pourquoi définir la structure ?**
- C'est comme un **formulaire pré-imprimé**
- On sait exactement quelles cases remplir
- TypeScript nous empêche de faire des erreurs (écrire dans la mauvaise case)

**Analogie :**

```
📋 FORMULAIRE "SESSION UTILISATEUR"

┌─────────────────────────────────────┐
│ Identifiant : [___________________] │  ← sub
│ Email :       [___________________] │  ← email
│ Permissions : [___________________] │  ← perms
└─────────────────────────────────────┘

Si vous essayez d'écrire "âge" :
❌ TypeScript dit : "Cette case n'existe pas !"
```

```tsx
// Type pour le Context : soit SessionData, soit null (pas connecté)
type SessionContextType = SessionData | null;
```

**Explication :**
- `|` signifie "OU"
- `SessionData | null` = "Soit les infos utilisateur, SOIT rien (null)"
- `null` = utilisateur pas encore connecté

```tsx
// ============================================
// CRÉATION DU TALKIE-WALKIE
// ============================================

const SessionContext = createContext<SessionContextType>(null);
```

**Décortiquons cette ligne :**
- `createContext` → Fabriquer un talkie-walkie
- `<SessionContextType>` → Le type de messages qu'on peut envoyer
- `(null)` → Au départ, pas de message (utilisateur pas connecté)
- `SessionContext` → Le nom de notre talkie-walkie

**Analogie :**

```
📻 TALKIE-WALKIE "SessionContext"

Fréquence : 107.5 FM
Type de messages autorisés : Infos utilisateur
Message initial : [silence] (null)
```

**Code complet du Provider (à suivre)...**

---

*[Le guide continue avec les autres fichiers, toujours avec le même niveau de détail et d'analogies]*
