# Guide RDF : Base de Données Graphe pour Données Complexes

## Table des Matières

### Partie 1-8 (Fondamentaux)
- [Introduction : Qu'est-ce que RDF et Pourquoi l'Utiliser ?](#partie-1-introduction)
- [Concepts Fondamentaux RDF](#partie-1-concepts-fondamentaux-rdf)
- [Formats de Sérialisation RDF](#partie-2-formats-de-sérialisation-rdf)
- [SPARQL - Le Langage de Requête](#partie-3-sparql---le-langage-de-requête)
- [Stockage RDF - Apache Jena Fuseki](#partie-4-stockage-rdf---apache-jena-fuseki)
- [Intégration FastAPI ↔ Fuseki](#partie-5-intégration-fastapi--fuseki)
- [Flux de Données Complet](#partie-6-flux-de-données-complet)
- [Comparaison PostgreSQL vs RDF](#partie-7-comparaison-postgresql-vs-rdf)
- [Checklist d'Implémentation](#partie-8-checklist-dimplémentation)

### Parties Avancées
- [Partie 9 : Ontologies et Vocabulaires](#partie-9--ontologies-et-vocabulaires)
- [Partie 10 : Patterns de Requêtes Avancées](#partie-10--patterns-de-requêtes-avancées)
- [Partie 11 : Performance et Optimisation](#partie-11--performance-et-optimisation)
- [Partie 12 : Versionning et Graphes Nommés](#partie-12--versionning-et-graphes-nommés)
- [Partie 13 : Intégration Frontend React](#partie-13--intégration-frontend-react)
- [Partie 14 : Tests et Validation](#partie-14--tests-et-validation)
- [Partie 15 : Production et Monitoring](#partie-15--production-et-monitoring)

---

## Partie 1: Introduction

### Le Problème des Bases Relationnelles pour Certaines Données

**Exemple : Modéliser un réseau électrique (IEC 61850)**

Avec PostgreSQL, vous devriez créer des dizaines de tables :
```sql
CREATE TABLE substations (...)
CREATE TABLE voltage_levels (...)
CREATE TABLE bays (...)
CREATE TABLE logical_devices (...)
CREATE TABLE logical_nodes (...)
CREATE TABLE data_objects (...)
CREATE TABLE data_attributes (...)
-- Et toutes les tables de jonction...
```

**Problèmes :**
- Structure rigide : ajouter un nouveau type d'équipement = modifier le schéma
- Requêtes complexes : naviguer de Substation → VoltageLevel → Bay → Equipment = 5 JOIN
- Versionning difficile : comment garder l'historique complet ?
- Relations multiples : un équipement peut être lié à plusieurs autres de différentes manières

### RDF : Une Base de Données "Graphe"

**RDF** = Resource Description Framework = Framework de Description de Ressources

C'est une façon de stocker des données comme **un réseau de connexions** (graphe) plutôt que comme des tableaux.

**Analogie :**
- **PostgreSQL** = classeur avec des feuilles Excel bien organisées
- **RDF** = tableau blanc avec des post-its reliés par des fils

---

## Partie 1: Concepts Fondamentaux RDF

### Le Triplet : Brique de Base

Toute information en RDF est exprimée en **triplets** :

```
<Sujet> <Prédicat> <Objet>
```

**Exemples concrets :**

```
<Marie>     <travaille_pour>    <Entreprise_A>
<Marie>     <habite_à>          <Paris>
<Paris>     <est_une>           <Ville>
<Ville>     <dans>              <France>
```

**Vocabulaire :**
- **Sujet** : de quoi on parle (Marie, Paris)
- **Prédicat** : la relation/propriété (travaille_pour, habite_à)
- **Objet** : la valeur ou l'entité liée (Entreprise_A, Paris)
- **Triplet** : une affirmation complète (sujet + prédicat + objet)

### Visualisation en Graphe

Les triplets forment un réseau :

```
    ┌─────────┐
    │  Marie  │
    └────┬────┘
         │
    travaille_pour
         │
         ↓
   ┌──────────────┐        habite_à       ┌────────┐
   │ Entreprise_A │   ←─────────────────   │  Paris │
   └──────────────┘                        └───┬────┘
                                               │
                                           est_une
                                               │
                                               ↓
                                          ┌────────┐
                                          │  Ville │
                                          └────────┘
```

### IRI : Identifiants Uniques

En RDF, chaque chose a un **identifiant unique** appelé IRI (Internationalized Resource Identifier).

**Format :**
```
http://example.com/entities#Marie
http://example.com/entities#Paris
http://example.com/vocab#travaille_pour
```

**Pourquoi des URLs ?**
- Uniques mondialement
- Peuvent pointer vers des définitions
- Namespace pour éviter les conflits

**Avec namespace (plus court) :**
```turtle
@prefix ex: <http://example.com/entities#> .
@prefix vocab: <http://example.com/vocab#> .

ex:Marie  vocab:travaille_pour  ex:Entreprise_A .
ex:Marie  vocab:habite_à        ex:Paris .
```

---

## Partie 2: Formats de Sérialisation RDF

### Turtle (.ttl) - Le Plus Lisible

```turtle
# Déclaration des namespaces
@prefix iec: <http://iec61850.org/vocab#> .
@prefix data: <http://myproject.com/data#> .

# Triplets
data:LD1  a  iec:LogicalDevice ;
          iec:hasName "LD1" ;
          iec:hasLogicalNode data:LN_MMXU1 .

data:LN_MMXU1  a  iec:LogicalNode ;
               iec:lnType "MMXU" ;
               iec:hasDataObject data:DO_Meas1 .

data:DO_Meas1  a  iec:DataObject ;
               iec:hasDataAttribute data:DA_InstMag .
```

**Vocabulaire :**
- **`@prefix`** : définit un raccourci pour un namespace
- **`a`** : raccourci pour "est de type" (rdf:type)
- **`;`** : continue avec le même sujet
- **`.`** : fin de la déclaration d'un sujet

### RDF/XML - Format Échange Standard

```xml
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:iec="http://iec61850.org/vocab#"
         xmlns:data="http://myproject.com/data#">

  <iec:LogicalDevice rdf:about="http://myproject.com/data#LD1">
    <iec:hasName>LD1</iec:hasName>
    <iec:hasLogicalNode rdf:resource="http://myproject.com/data#LN_MMXU1"/>
  </iec:LogicalDevice>

</rdf:RDF>
```

### JSON-LD - Intégration Web

```json
{
  "@context": {
    "iec": "http://iec61850.org/vocab#",
    "data": "http://myproject.com/data#"
  },
  "@id": "data:LD1",
  "@type": "iec:LogicalDevice",
  "iec:hasName": "LD1",
  "iec:hasLogicalNode": {
    "@id": "data:LN_MMXU1"
  }
}
```

---

## Partie 3: SPARQL - Le Langage de Requête

### Qu'est-ce que SPARQL ?

**SPARQL** = SQL pour RDF

C'est le langage pour interroger une base RDF, comme SQL pour PostgreSQL.

### Structure d'une Requête SPARQL

```sparql
# Définir les namespaces
PREFIX iec: <http://iec61850.org/vocab#>
PREFIX data: <http://myproject.com/data#>

# Sélectionner ce qu'on veut récupérer
SELECT ?ln ?type
WHERE {
  # Pattern de triplets à matcher
  data:LD1  iec:hasLogicalNode  ?ln .
  ?ln       iec:lnType           ?type .
}
```

**Vocabulaire :**
- **PREFIX** : définit un namespace (comme @prefix en Turtle)
- **SELECT** : colonnes à retourner
- **WHERE** : patterns de triplets à matcher
- **`?variable`** : variable qui va être remplie par les résultats

### Exemples de Requêtes SPARQL

**1. Lister tous les LogicalNodes**

```sparql
PREFIX iec: <http://iec61850.org/vocab#>

SELECT ?ln ?type
WHERE {
  ?ln  a  iec:LogicalNode ;
       iec:lnType  ?type .
}
```

**Résultat :**
```
?ln                              ?type
-------------------------------- ------
http://myproject.com/data#LN_MMXU1   MMXU
http://myproject.com/data#LN_XCBR1   XCBR
```

**2. Trouver les enfants d'un LogicalDevice**

```sparql
PREFIX iec: <http://iec61850.org/vocab#>
PREFIX data: <http://myproject.com/data#>

SELECT ?ln ?type
WHERE {
  data:LD1  iec:hasLogicalNode  ?ln .
  ?ln       iec:lnType           ?type .
}
```

**3. Navigation multi-niveaux**

```sparql
# Récupérer : LogicalDevice → LogicalNode → DataObject → DataAttribute
SELECT ?ld ?ln ?do ?da
WHERE {
  ?ld  iec:hasLogicalNode   ?ln .
  ?ln  iec:hasDataObject    ?do .
  ?do  iec:hasDataAttribute ?da .
  FILTER(?ld = data:LD1)
}
```

**4. Filtrer par condition**

```sparql
SELECT ?ln
WHERE {
  ?ln  a  iec:LogicalNode ;
       iec:lnType  ?type .
  FILTER(?type = "MMXU")
}
```

**5. Compter**

```sparql
SELECT (COUNT(?ln) AS ?total)
WHERE {
  ?ln  a  iec:LogicalNode .
}
```

### SPARQL UPDATE : Modifier les Données

**Insérer un triplet :**
```sparql
PREFIX iec: <http://iec61850.org/vocab#>
PREFIX data: <http://myproject.com/data#>

INSERT DATA {
  data:LN_NEW  a  iec:LogicalNode ;
               iec:lnType  "XCBR" .
}
```

**Supprimer un triplet :**
```sparql
DELETE DATA {
  data:LN_OLD  iec:lnType  "MMXU" .
}
```

**Modifier (DELETE + INSERT) :**
```sparql
DELETE { ?ln iec:lnType ?oldType }
INSERT { ?ln iec:lnType "MMXU_NEW" }
WHERE {
  ?ln  a  iec:LogicalNode ;
       iec:lnType  ?oldType .
  FILTER(?ln = data:LN_MMXU1)
}
```

---

## Partie 4: Stockage RDF - Apache Jena Fuseki

### Qu'est-ce que Fuseki ?

**Apache Jena Fuseki** est un serveur de base de données RDF avec :
- Stockage persistant de triplets
- Endpoint SPARQL (HTTP API)
- Interface web de requêtage
- Gestion de datasets (bases séparées)

**Analogie :**
- Fuseki pour RDF = PostgreSQL pour relationnel
- SPARQL = SQL
- Dataset = Database

### Installation avec Docker

**docker-compose.yml :**
```yaml
version: '3.8'

services:
  fuseki:
    image: stain/jena-fuseki
    ports:
      - "3030:3030"
    environment:
      ADMIN_PASSWORD: admin
    volumes:
      - fuseki_data:/fuseki
    command: /jena-fuseki/fuseki-server --loc=/fuseki/databases/mydb /mydb

volumes:
  fuseki_data:
```

**Démarrage :**
```bash
docker-compose up -d fuseki
```

**Accès :**
- Interface web : http://localhost:3030
- SPARQL endpoint : http://localhost:3030/mydb/sparql
- Update endpoint : http://localhost:3030/mydb/update

### Créer un Dataset

**Via l'interface web :**
1. Aller sur http://localhost:3030
2. "Manage datasets" → "Add new dataset"
3. Nom : `iec61850_project1`
4. Type : "Persistent (TDB2)"

**Via API :**
```bash
curl -X POST http://localhost:3030/$/datasets \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "dbName=iec61850_project1&dbType=tdb2"
```

### Charger des Données

**Upload d'un fichier Turtle :**
```bash
curl -X POST http://localhost:3030/iec61850_project1/data \
  -H "Content-Type: text/turtle" \
  --data-binary @data.ttl
```

---

## Partie 5: Intégration FastAPI ↔ Fuseki

### Structure du Projet

```
backend/
  rdf/
    __init__.py
    client.py          # Client SPARQL
    queries.py         # Requêtes SPARQL réutilisables
  routes/
    nodes.py           # Routes API pour les nœuds
  main.py
```

### Client SPARQL

**Fichier `rdf/client.py` :**

```python
import requests
from typing import Dict, List, Any
import os

# Configuration
FUSEKI_URL = os.getenv("FUSEKI_URL", "http://localhost:3030")
DATASET = os.getenv("FUSEKI_DATASET", "iec61850_project1")

class RDFClient:
    """Client pour interagir avec Fuseki"""

    def __init__(self):
        self.base_url = f"{FUSEKI_URL}/{DATASET}"
        self.sparql_endpoint = f"{self.base_url}/sparql"
        self.update_endpoint = f"{self.base_url}/update"

    def query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        Exécute une requête SPARQL SELECT

        Args:
            sparql_query: Requête SPARQL

        Returns:
            Liste de résultats (bindings)
        """
        response = requests.post(
            self.sparql_endpoint,
            data={"query": sparql_query},
            headers={"Accept": "application/sparql-results+json"}
        )
        response.raise_for_status()

        # Extraire les bindings
        results = response.json()
        return results.get("results", {}).get("bindings", [])

    def update(self, sparql_update: str) -> None:
        """
        Exécute une requête SPARQL UPDATE (INSERT/DELETE)

        Args:
            sparql_update: Requête SPARQL UPDATE
        """
        response = requests.post(
            self.update_endpoint,
            data={"update": sparql_update},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()

    def ask(self, sparql_query: str) -> bool:
        """
        Exécute une requête SPARQL ASK (vrai/faux)

        Args:
            sparql_query: Requête SPARQL ASK

        Returns:
            True si le pattern existe, False sinon
        """
        response = requests.post(
            self.sparql_endpoint,
            data={"query": sparql_query},
            headers={"Accept": "application/sparql-results+json"}
        )
        response.raise_for_status()

        results = response.json()
        return results.get("boolean", False)

# Instance globale
rdf_client = RDFClient()
```

**Vocabulaire :**
- **Endpoint** : URL où envoyer les requêtes
- **Bindings** : résultats d'une requête SELECT (variables → valeurs)
- **raise_for_status()** : lève une exception si erreur HTTP

### Requêtes SPARQL Réutilisables

**Fichier `rdf/queries.py` :**

```python
"""Templates de requêtes SPARQL"""

# Namespaces communs
PREFIXES = """
PREFIX iec: <http://iec61850.org/vocab#>
PREFIX data: <http://myproject.com/data#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

def get_logical_nodes(ld_id: str) -> str:
    """Récupère tous les LogicalNodes d'un LogicalDevice"""
    return f"""
    {PREFIXES}
    SELECT ?ln ?type
    WHERE {{
        data:{ld_id}  iec:hasLogicalNode  ?ln .
        ?ln           iec:lnType           ?type .
    }}
    """

def get_node_details(node_id: str) -> str:
    """Récupère tous les attributs d'un nœud"""
    return f"""
    {PREFIXES}
    SELECT ?property ?value
    WHERE {{
        data:{node_id}  ?property  ?value .
    }}
    """

def update_node_property(node_id: str, property_name: str, new_value: str) -> str:
    """Met à jour une propriété d'un nœud"""
    return f"""
    {PREFIXES}
    DELETE {{ data:{node_id} iec:{property_name} ?old }}
    INSERT {{ data:{node_id} iec:{property_name} "{new_value}" }}
    WHERE  {{ data:{node_id} iec:{property_name} ?old }}
    """

def search_nodes(search_term: str) -> str:
    """Recherche textuelle dans les nœuds"""
    return f"""
    {PREFIXES}
    SELECT ?node ?type ?name
    WHERE {{
        ?node  a  iec:LogicalNode ;
               iec:lnType  ?type ;
               iec:hasName ?name .
        FILTER(CONTAINS(LCASE(?name), LCASE("{search_term}")))
    }}
    """
```

### Routes FastAPI

**Fichier `routes/nodes.py` :**

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from rdf.client import rdf_client
from rdf.queries import (
    get_logical_nodes,
    get_node_details,
    update_node_property,
    search_nodes
)
from auth.dependencies import require_permission
from db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/nodes", tags=["nodes"])

@router.get("/ld/{ld_id}")
def list_logical_nodes(
    ld_id: str,
    user=Depends(require_permission("scd:view"))
) -> List[Dict[str, Any]]:
    """
    Liste tous les LogicalNodes d'un LogicalDevice

    Args:
        ld_id: ID du LogicalDevice (ex: "LD1")

    Returns:
        Liste des LogicalNodes avec leur type
    """
    # Construire la requête SPARQL
    query = get_logical_nodes(ld_id)

    # Exécuter
    bindings = rdf_client.query(query)

    # Transformer en JSON lisible
    results = []
    for binding in bindings:
        results.append({
            "id": binding["ln"]["value"],
            "type": binding["type"]["value"]
        })

    return results

@router.get("/{node_id}")
def get_node(
    node_id: str,
    user=Depends(require_permission("scd:view"))
) -> Dict[str, Any]:
    """
    Récupère les détails d'un nœud

    Args:
        node_id: ID du nœud (ex: "LN_MMXU1")

    Returns:
        Détails du nœud
    """
    query = get_node_details(node_id)
    bindings = rdf_client.query(query)

    if not bindings:
        raise HTTPException(404, detail="Node not found")

    # Construire un objet JSON
    node = {"id": node_id}
    for binding in bindings:
        prop = binding["property"]["value"].split("#")[-1]  # Extraire le nom court
        value = binding["value"]["value"]
        node[prop] = value

    return node

@router.patch("/{node_id}")
def update_node(
    node_id: str,
    updates: Dict[str, str],
    user=Depends(require_permission("scd:edit")),
    db: Session = Depends(get_db)
):
    """
    Met à jour les propriétés d'un nœud

    Args:
        node_id: ID du nœud
        updates: Dictionnaire {propriété: nouvelle_valeur}

    Returns:
        204 No Content
    """
    # Pour chaque propriété à mettre à jour
    for prop, value in updates.items():
        update_query = update_node_property(node_id, prop, value)
        rdf_client.update(update_query)

    # Audit dans PostgreSQL
    from db.models import AuditLog
    audit = AuditLog(
        user_id=user.id,
        action="UPDATE",
        resource_type="node",
        resource_id=node_id,
        payload_json=updates
    )
    db.add(audit)
    db.commit()

    return {"message": "Updated successfully"}

@router.get("/search/")
def search(
    q: str,
    user=Depends(require_permission("scd:view"))
) -> List[Dict[str, Any]]:
    """
    Recherche dans les nœuds

    Args:
        q: Terme de recherche

    Returns:
        Liste des nœuds correspondants
    """
    query = search_nodes(q)
    bindings = rdf_client.query(query)

    results = []
    for binding in bindings:
        results.append({
            "id": binding["node"]["value"],
            "type": binding["type"]["value"],
            "name": binding["name"]["value"]
        })

    return results
```

---

## Partie 6: Flux de Données Complet

### Diagramme d'Architecture

```
┌──────────────────────────────────────────────────┐
│ FRONTEND (React)                                 │
│                                                  │
│  Component → React Query → fetch(/api/nodes)    │
└───────────────────────┬──────────────────────────┘
                        │ HTTP
                        ↓
┌──────────────────────────────────────────────────┐
│ BACKEND (FastAPI)                                │
│                                                  │
│  Route → require_permission() → RDF Client       │
│                    ↓                             │
│              Audit → PostgreSQL                  │
└───────────────────────┬──────────────────────────┘
                        │ HTTP SPARQL
                        ↓
┌──────────────────────────────────────────────────┐
│ FUSEKI (RDF Store)                               │
│                                                  │
│  SPARQL Endpoint → Execute Query → Return JSON   │
│                                                  │
│  Triplets: <LN1> <hasType> "MMXU"               │
└──────────────────────────────────────────────────┘
```

### Exemple Complet : Afficher un LogicalNode

**1. Frontend - Composant React**

```tsx
import { useQuery } from '@tanstack/react-query'

function LogicalNodeDetails({ nodeId }: { nodeId: string }) {
  const { data: node, isLoading } = useQuery({
    queryKey: ['node', nodeId],
    queryFn: async () => {
      const response = await fetch(`/api/nodes/${nodeId}`, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      })
      return response.json()
    }
  })

  if (isLoading) return <div>Chargement...</div>

  return (
    <div>
      <h2>{node.id}</h2>
      <p>Type: {node.lnType}</p>
      <p>Description: {node.description}</p>
    </div>
  )
}
```

**2. Backend - Route FastAPI**

```python
@router.get("/{node_id}")
def get_node(node_id: str, user=Depends(require_permission("scd:view"))):
    # Construire la requête SPARQL
    query = f"""
    PREFIX iec: <http://iec61850.org/vocab#>
    PREFIX data: <http://myproject.com/data#>

    SELECT ?property ?value
    WHERE {{
        data:{node_id}  ?property  ?value .
    }}
    """

    # Exécuter via Fuseki
    bindings = rdf_client.query(query)

    # Transformer en JSON
    node = {"id": node_id}
    for binding in bindings:
        prop = binding["property"]["value"].split("#")[-1]
        value = binding["value"]["value"]
        node[prop] = value

    return node
```

**3. Fuseki - Exécution SPARQL**

```
Reçoit la requête :
SELECT ?property ?value WHERE { data:LN_MMXU1 ?property ?value }

Interroge le graphe de triplets :
data:LN_MMXU1  iec:lnType       "MMXU"
data:LN_MMXU1  iec:description  "Measurement Unit"

Retourne JSON :
{
  "results": {
    "bindings": [
      {"property": {"value": "...#lnType"}, "value": {"value": "MMXU"}},
      {"property": {"value": "...#description"}, "value": {"value": "Measurement Unit"}}
    ]
  }
}
```

**4. Réponse au Frontend**

```json
{
  "id": "LN_MMXU1",
  "lnType": "MMXU",
  "description": "Measurement Unit"
}
```

---

## Partie 7: Comparaison PostgreSQL vs RDF

| Aspect | PostgreSQL | RDF/Fuseki |
|--------|-----------|------------|
| **Structure** | Tables fixes | Graphe flexible |
| **Requêtes** | SQL avec JOIN | SPARQL avec patterns |
| **Schéma** | Rigide, migrations | Dynamique, ontologie |
| **Relations** | Clés étrangères | Triplets directs |
| **Navigation** | JOIN multiples | Patterns récursifs |
| **Usage** | Auth, RBAC, audit | Données métier complexes |
| **Performance lecture** | Très rapide (index) | Rapide (optimisé graphe) |
| **Performance écriture** | Très rapide | Rapide |
| **Versionning** | Difficile | Graphes nommés |

### Quand Utiliser Quoi ?

**PostgreSQL pour :**
- Utilisateurs, rôles, permissions
- Sessions, tokens
- Audit logs
- Configuration application
- Données structurées stables

**RDF/Fuseki pour :**
- Données fortement interconnectées
- Structures qui évoluent
- Navigation multi-niveaux
- Intégration avec d'autres systèmes (via ontologies)
- Versionning de graphes entiers

---

## Partie 8: Checklist d'Implémentation

### Setup Initial

- [ ] **Fuseki installé et démarré**
  - Docker ou installation locale
  - Interface accessible sur http://localhost:3030

- [ ] **Dataset créé**
  - Nom : `iec61850_project1`
  - Type : TDB2 (persistant)

- [ ] **Ontologie chargée**
  - Fichier avec définitions IEC 61850
  - Namespaces configurés

### Backend

- [ ] **Client RDF configuré**
  - `rdf/client.py` avec méthodes query/update
  - Variables d'environnement (FUSEKI_URL, DATASET)

- [ ] **Requêtes SPARQL écrites**
  - Templates réutilisables dans `rdf/queries.py`
  - Préfixes définis

- [ ] **Routes API créées**
  - GET /api/nodes/{id}
  - PATCH /api/nodes/{id}
  - GET /api/nodes/search?q=...

- [ ] **Protection RBAC**
  - `require_permission("scd:view")` sur routes lecture
  - `require_permission("scd:edit")` sur routes écriture

- [ ] **Audit logs**
  - Chaque UPDATE RDF → INSERT audit PostgreSQL

### Tests

- [ ] **Requêtes SPARQL testées**
  - Via interface Fuseki
  - Via client Python

- [ ] **Routes API testées**
  - Postman/curl
  - Tests automatisés

- [ ] **Performance vérifiée**
  - Temps de réponse < 200ms
  - Pagination si > 100 résultats

---

## Partie 9 : Ontologies et Vocabulaires

### Qu'est-ce qu'une Ontologie ?

Une **ontologie** en RDF est un **vocabulaire structuré** qui définit :
- Les **classes** (types d'entités)
- Les **propriétés** (relations entre entités)
- Les **contraintes** (règles de validation)

**Analogie :**
- **Ontologie** = schéma de base de données + documentation
- **Classes** = tables
- **Propriétés** = colonnes

### Standards d'Ontologies

**RDF Schema (RDFS)** - Basique :
```turtle
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix iec: <http://iec61850.org/vocab#> .

# Définir une classe
iec:LogicalNode  a  rdfs:Class ;
                 rdfs:label "Logical Node" ;
                 rdfs:comment "A functional unit within a device" .

# Définir une propriété
iec:hasLogicalNode  a  rdfs:Property ;
                    rdfs:domain  iec:LogicalDevice ;
                    rdfs:range   iec:LogicalNode .
```

**OWL (Web Ontology Language)** - Avancé :
```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix iec: <http://iec61850.org/vocab#> .

# Classe avec contraintes
iec:LogicalNode  a  owl:Class ;
                 rdfs:subClassOf  [
                     a  owl:Restriction ;
                     owl:onProperty  iec:lnType ;
                     owl:cardinality  1   # Exactement 1 type
                 ] .

# Propriété fonctionnelle (1 seul parent)
iec:hasParent  a  owl:FunctionalProperty .
```

### Créer votre Ontologie IEC 61850

**Fichier `ontology/iec61850.ttl` :**

```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix iec: <http://iec61850.org/vocab#> .

# ============================================
# Classes principales
# ============================================

iec:Substation  a  owl:Class ;
    rdfs:label "Substation"@en ;
    rdfs:comment "Physical site containing electrical equipment"@en .

iec:VoltageLevel  a  owl:Class ;
    rdfs:label "Voltage Level"@en ;
    rdfs:comment "Section with common voltage"@en .

iec:Bay  a  owl:Class ;
    rdfs:label "Bay"@en ;
    rdfs:comment "Functional group of equipment"@en .

iec:IED  a  owl:Class ;
    rdfs:label "Intelligent Electronic Device"@en ;
    rdfs:comment "Physical device with processing capability"@en .

iec:LogicalDevice  a  owl:Class ;
    rdfs:label "Logical Device"@en ;
    rdfs:comment "Logical grouping within an IED"@en .

iec:LogicalNode  a  owl:Class ;
    rdfs:label "Logical Node"@en ;
    rdfs:comment "Smallest functional unit"@en .

iec:DataObject  a  owl:Class ;
    rdfs:label "Data Object"@en .

iec:DataAttribute  a  owl:Class ;
    rdfs:label "Data Attribute"@en .

# ============================================
# Propriétés de structure (hiérarchie)
# ============================================

iec:hasVoltageLevel  a  owl:ObjectProperty ;
    rdfs:domain  iec:Substation ;
    rdfs:range   iec:VoltageLevel ;
    rdfs:label "has voltage level"@en .

iec:hasBay  a  owl:ObjectProperty ;
    rdfs:domain  iec:VoltageLevel ;
    rdfs:range   iec:Bay ;
    rdfs:label "has bay"@en .

iec:hasIED  a  owl:ObjectProperty ;
    rdfs:domain  iec:Bay ;
    rdfs:range   iec:IED ;
    rdfs:label "has IED"@en .

iec:hasLogicalDevice  a  owl:ObjectProperty ;
    rdfs:domain  iec:IED ;
    rdfs:range   iec:LogicalDevice ;
    rdfs:label "has logical device"@en .

iec:hasLogicalNode  a  owl:ObjectProperty ;
    rdfs:domain  iec:LogicalDevice ;
    rdfs:range   iec:LogicalNode ;
    rdfs:label "has logical node"@en .

iec:hasDataObject  a  owl:ObjectProperty ;
    rdfs:domain  iec:LogicalNode ;
    rdfs:range   iec:DataObject ;
    rdfs:label "has data object"@en .

iec:hasDataAttribute  a  owl:ObjectProperty ;
    rdfs:domain  iec:DataObject ;
    rdfs:range   iec:DataAttribute ;
    rdfs:label "has data attribute"@en .

# ============================================
# Propriétés de données (valeurs)
# ============================================

iec:name  a  owl:DatatypeProperty ;
    rdfs:label "name"@en ;
    rdfs:range  xsd:string .

iec:description  a  owl:DatatypeProperty ;
    rdfs:label "description"@en ;
    rdfs:range  xsd:string .

iec:lnType  a  owl:DatatypeProperty ;
    rdfs:domain  iec:LogicalNode ;
    rdfs:range   xsd:string ;
    rdfs:label "Logical Node Type"@en ;
    rdfs:comment "Type like MMXU, XCBR, etc."@en .

iec:value  a  owl:DatatypeProperty ;
    rdfs:domain  iec:DataAttribute ;
    rdfs:label "value"@en .

iec:timestamp  a  owl:DatatypeProperty ;
    rdfs:range  xsd:dateTime ;
    rdfs:label "timestamp"@en .

# ============================================
# Types de Logical Nodes (IEC 61850-7-4)
# ============================================

iec:MMXU  a  iec:LogicalNode ;
    rdfs:label "Measurement (MMXU)"@en ;
    rdfs:comment "Measurement unit for voltage, current, power"@en .

iec:XCBR  a  iec:LogicalNode ;
    rdfs:label "Circuit Breaker (XCBR)"@en .

iec:XSWI  a  iec:LogicalNode ;
    rdfs:label "Switch (XSWI)"@en .

iec:CSWI  a  iec:LogicalNode ;
    rdfs:label "Switch Control (CSWI)"@en .

iec:PDIS  a  iec:LogicalNode ;
    rdfs:label "Distance Protection (PDIS)"@en .
```

### Charger l'Ontologie dans Fuseki

```bash
curl -X POST http://localhost:3030/iec61850_project1/data \
  -H "Content-Type: text/turtle" \
  --data-binary @ontology/iec61850.ttl
```

### Validation avec SHACL

**SHACL** = Shapes Constraint Language = Langage pour valider les données RDF

**Fichier `validation/shapes.ttl` :**

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix iec: <http://iec61850.org/vocab#> .

# Contrainte : un LogicalNode doit avoir exactement 1 lnType
iec:LogicalNodeShape  a  sh:NodeShape ;
    sh:targetClass  iec:LogicalNode ;
    sh:property [
        sh:path  iec:lnType ;
        sh:minCount  1 ;
        sh:maxCount  1 ;
        sh:datatype  xsd:string ;
    ] ;
    sh:property [
        sh:path  iec:name ;
        sh:minCount  1 ;
    ] .
```

**Valider avec Python :**

```python
from pyshacl import validate

# Charger le graphe de données
data_graph = Graph()
data_graph.parse("data.ttl", format="turtle")

# Charger les contraintes
shapes_graph = Graph()
shapes_graph.parse("validation/shapes.ttl", format="turtle")

# Valider
conforms, results_graph, results_text = validate(
    data_graph,
    shacl_graph=shapes_graph
)

if not conforms:
    print("Erreurs de validation :")
    print(results_text)
```

---

## Partie 10 : Patterns de Requêtes Avancées

### 1. Navigation Récursive (Property Paths)

**Problème :** Trouver tous les ancêtres d'un nœud, peu importe le nombre de niveaux.

**Solution avec Property Paths :**

```sparql
PREFIX iec: <http://iec61850.org/vocab#>
PREFIX data: <http://myproject.com/data#>

SELECT ?ancestor
WHERE {
  data:LN_MMXU1  (^iec:hasLogicalNode | ^iec:hasLogicalDevice | ^iec:hasIED | ^iec:hasBay)+ ?ancestor .
}
```

**Vocabulaire :**
- **`^`** : inverse d'une propriété (parent au lieu d'enfant)
- **`+`** : 1 ou plusieurs fois
- **`*`** : 0 ou plusieurs fois
- **`|`** : OU

**Exemples de Property Paths :**

```sparql
# Tous les descendants (enfants, petits-enfants, etc.)
?substation  iec:hasVoltageLevel / iec:hasBay / iec:hasIED  ?descendant .

# Tous les niveaux (0 ou plus)
?root  iec:hasChild*  ?allNodes .

# Alternative entre 2 chemins
?node  (iec:hasParent | iec:isChildOf)  ?parent .
```

### 2. Agrégation et Groupement

**Compter les LogicalNodes par type :**

```sparql
PREFIX iec: <http://iec61850.org/vocab#>

SELECT ?type (COUNT(?ln) AS ?count)
WHERE {
  ?ln  a  iec:LogicalNode ;
       iec:lnType  ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
```

**Moyenne des valeurs :**

```sparql
SELECT ?ln (AVG(?value) AS ?avgValue)
WHERE {
  ?ln  iec:hasDataObject / iec:hasDataAttribute ?attr .
  ?attr  iec:value  ?value .
}
GROUP BY ?ln
```

**Fonctions d'agrégation :**
- `COUNT()` : compter
- `SUM()` : somme
- `AVG()` : moyenne
- `MIN()` / `MAX()` : min/max
- `GROUP_CONCAT()` : concaténer en chaîne

### 3. Sous-requêtes (Nested Queries)

**Trouver les LogicalDevices qui ont plus de 5 LogicalNodes :**

```sparql
PREFIX iec: <http://iec61850.org/vocab#>

SELECT ?ld ?count
WHERE {
  {
    SELECT ?ld (COUNT(?ln) AS ?count)
    WHERE {
      ?ld  iec:hasLogicalNode  ?ln .
    }
    GROUP BY ?ld
  }
  FILTER(?count > 5)
}
```

### 4. OPTIONAL : Données Facultatives

**Récupérer les nœuds avec leur description (si elle existe) :**

```sparql
SELECT ?node ?name ?description
WHERE {
  ?node  a  iec:LogicalNode ;
         iec:name  ?name .
  OPTIONAL { ?node  iec:description  ?description }
}
```

**Résultat :**
```
?node       ?name      ?description
----------- ---------- -------------------
data:LN1    "Node1"    "Measurement unit"
data:LN2    "Node2"    (vide)
```

### 5. UNION : Alternatives

**Trouver tous les nœuds de type MMXU ou XCBR :**

```sparql
SELECT ?node ?type
WHERE {
  ?node  a  iec:LogicalNode .
  {
    ?node  iec:lnType  "MMXU" .
    BIND("MMXU" AS ?type)
  }
  UNION
  {
    ?node  iec:lnType  "XCBR" .
    BIND("XCBR" AS ?type)
  }
}
```

### 6. BIND : Calculs et Transformations

**Créer une nouvelle variable calculée :**

```sparql
SELECT ?node ?name ?shortName
WHERE {
  ?node  iec:name  ?name .
  BIND(SUBSTR(?name, 1, 3) AS ?shortName)
}
```

**Fonctions utiles :**
- `CONCAT(?a, ?b)` : concaténer
- `SUBSTR(?str, start, length)` : sous-chaîne
- `STRLEN(?str)` : longueur
- `UCASE(?str)` / `LCASE(?str)` : maj/min
- `REPLACE(?str, "old", "new")` : remplacer

### 7. VALUES : Listes de Valeurs

**Filtrer sur plusieurs valeurs :**

```sparql
SELECT ?node ?type
WHERE {
  ?node  iec:lnType  ?type .
  VALUES ?type { "MMXU" "XCBR" "XSWI" }
}
```

### 8. CONSTRUCT : Créer un Nouveau Graphe

**Transformer la structure :**

```sparql
PREFIX iec: <http://iec61850.org/vocab#>
PREFIX new: <http://mynewmodel.com/vocab#>

CONSTRUCT {
  ?ld  new:contains  ?ln .
  ?ln  new:hasType   ?type .
}
WHERE {
  ?ld  iec:hasLogicalNode  ?ln .
  ?ln  iec:lnType          ?type .
}
```

**Utilité :** migration de schéma, export vers autre format.

---

## Partie 11 : Performance et Optimisation

### Indexation et Configuration Fuseki

**Configuration TDB2 (fichier `config.ttl`) :**

```turtle
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix tdb2: <http://jena.apache.org/2016/tdb#> .

<#service> a fuseki:Service ;
    fuseki:name "iec61850_project1" ;
    fuseki:endpoint [ fuseki:operation fuseki:query ] ;
    fuseki:endpoint [ fuseki:operation fuseki:update ] ;
    fuseki:dataset <#dataset> .

<#dataset> a tdb2:DatasetTDB2 ;
    tdb2:location "/fuseki/databases/project1" ;
    tdb2:unionDefaultGraph true .
```

### Stratégies de Pagination

**Mauvais (charge tout en mémoire) :**

```sparql
SELECT ?node
WHERE {
  ?node  a  iec:LogicalNode .
}
```

**Bon (pagination) :**

```sparql
SELECT ?node
WHERE {
  ?node  a  iec:LogicalNode .
}
ORDER BY ?node
LIMIT 20
OFFSET 0
```

**Implémentation Python :**

```python
def paginate_query(base_query: str, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    paginated = f"""
    {base_query}
    ORDER BY ?node
    LIMIT {page_size}
    OFFSET {offset}
    """
    return rdf_client.query(paginated)
```

### Mise en Cache

**Cache côté Backend (Redis) :**

```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_node_cached(node_id: str):
    # Vérifier le cache
    cached = cache.get(f"node:{node_id}")
    if cached:
        return json.loads(cached)

    # Si pas en cache, requête SPARQL
    query = get_node_details(node_id)
    bindings = rdf_client.query(query)

    # Transformer
    node = {"id": node_id}
    for binding in bindings:
        prop = binding["property"]["value"].split("#")[-1]
        value = binding["value"]["value"]
        node[prop] = value

    # Sauvegarder en cache (expire après 5 minutes)
    cache.setex(f"node:{node_id}", 300, json.dumps(node))

    return node
```

### Éviter les Requêtes N+1

**Mauvais (1 requête par nœud) :**

```python
for ld_id in logical_devices:
    nodes = get_logical_nodes(ld_id)  # N requêtes
```

**Bon (1 seule requête) :**

```sparql
SELECT ?ld ?ln ?type
WHERE {
  ?ld  iec:hasLogicalNode  ?ln .
  ?ln  iec:lnType          ?type .
  VALUES ?ld { data:LD1 data:LD2 data:LD3 }
}
```

```python
def get_nodes_batch(ld_ids: List[str]):
    lds_values = " ".join([f"data:{ld}" for ld in ld_ids])
    query = f"""
    PREFIX iec: <http://iec61850.org/vocab#>
    PREFIX data: <http://myproject.com/data#>

    SELECT ?ld ?ln ?type
    WHERE {{
        ?ld  iec:hasLogicalNode  ?ln .
        ?ln  iec:lnType          ?type .
        VALUES ?ld {{ {lds_values} }}
    }}
    """
    return rdf_client.query(query)
```

### Monitoring des Performances

**Logs de temps de requête :**

```python
import time
import logging

def query_with_timing(sparql_query: str):
    start = time.time()
    results = rdf_client.query(sparql_query)
    duration = time.time() - start

    logging.info(f"SPARQL query took {duration:.3f}s")

    if duration > 1.0:
        logging.warning(f"Slow query detected:\n{sparql_query}")

    return results
```

---

## Partie 12 : Versionning et Graphes Nommés

### Problème : Historique et Modifications

Avec PostgreSQL, le versionning est complexe :
- Tables de log
- Triggers
- Snapshots complets

Avec RDF, on peut utiliser des **graphes nommés**.

### Graphes Nommés : Concept

**Un dataset Fuseki peut contenir plusieurs graphes :**

```
Dataset "iec61850_project1"
  ├─ Graphe par défaut (données actuelles)
  ├─ Graphe "version_2024-01-01"
  ├─ Graphe "version_2024-02-01"
  └─ Graphe "version_2024-03-01"
```

**Syntaxe Turtle avec graphes nommés :**

```turtle
# Graphe par défaut
data:LN1  iec:lnType  "MMXU" .

# Graphe nommé (version du 2024-01-01)
GRAPH <http://myproject.com/versions/2024-01-01> {
  data:LN1  iec:lnType  "MMXU_OLD" .
}
```

### Requêtes avec Graphes Nommés

**Interroger un graphe spécifique :**

```sparql
PREFIX iec: <http://iec61850.org/vocab#>
PREFIX data: <http://myproject.com/data#>

SELECT ?type
WHERE {
  GRAPH <http://myproject.com/versions/2024-01-01> {
    data:LN1  iec:lnType  ?type .
  }
}
```

**Comparer deux versions :**

```sparql
SELECT ?node ?oldType ?newType
WHERE {
  GRAPH <http://myproject.com/versions/2024-01-01> {
    ?node  iec:lnType  ?oldType .
  }
  GRAPH <http://myproject.com/versions/2024-02-01> {
    ?node  iec:lnType  ?newType .
  }
  FILTER(?oldType != ?newType)
}
```

### Créer une Version (Snapshot)

**Python - Copier le graphe actuel dans un graphe nommé :**

```python
from datetime import datetime

def create_version_snapshot():
    # Nom du graphe de version
    timestamp = datetime.now().strftime("%Y-%m-%d")
    version_graph = f"http://myproject.com/versions/{timestamp}"

    # Requête pour copier toutes les données
    copy_query = f"""
    INSERT {{
        GRAPH <{version_graph}> {{
            ?s ?p ?o .
        }}
    }}
    WHERE {{
        ?s ?p ?o .
    }}
    """

    rdf_client.update(copy_query)

    # Sauvegarder les métadonnées de version
    metadata_query = f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>

    INSERT DATA {{
        <{version_graph}>  dcterms:created  "{datetime.now().isoformat()}"^^xsd:dateTime .
    }}
    """

    rdf_client.update(metadata_query)
```

### API de Versionning

**Fichier `routes/versions.py` :**

```python
from fastapi import APIRouter, Depends
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/versions", tags=["versions"])

@router.post("/")
def create_version(user=Depends(require_permission("admin"))):
    """Créer un snapshot de la version actuelle"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    version_graph = f"http://myproject.com/versions/{timestamp}"

    copy_query = f"""
    INSERT {{
        GRAPH <{version_graph}> {{
            ?s ?p ?o .
        }}
    }}
    WHERE {{
        ?s ?p ?o .
    }}
    """

    rdf_client.update(copy_query)

    return {"version": timestamp, "graph": version_graph}

@router.get("/")
def list_versions() -> List[str]:
    """Lister toutes les versions disponibles"""
    query = """
    SELECT DISTINCT ?graph
    WHERE {
        GRAPH ?graph { ?s ?p ?o }
    }
    """

    bindings = rdf_client.query(query)

    versions = [b["graph"]["value"] for b in bindings
                if "versions/" in b["graph"]["value"]]

    return versions

@router.get("/{version}/nodes/{node_id}")
def get_node_version(version: str, node_id: str):
    """Récupérer un nœud à une version donnée"""
    version_graph = f"http://myproject.com/versions/{version}"

    query = f"""
    PREFIX iec: <http://iec61850.org/vocab#>
    PREFIX data: <http://myproject.com/data#>

    SELECT ?property ?value
    WHERE {{
        GRAPH <{version_graph}> {{
            data:{node_id}  ?property  ?value .
        }}
    }}
    """

    bindings = rdf_client.query(query)

    node = {"id": node_id, "version": version}
    for binding in bindings:
        prop = binding["property"]["value"].split("#")[-1]
        value = binding["value"]["value"]
        node[prop] = value

    return node
```

---

## Partie 13 : Intégration Frontend React

### Hook Custom pour Requêtes RDF

**Fichier `frontend/src/hooks/useRDFQuery.ts` :**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

interface Node {
  id: string
  [key: string]: any
}

export function useNode(nodeId: string) {
  return useQuery<Node>({
    queryKey: ['node', nodeId],
    queryFn: async () => {
      const response = await fetch(`/api/nodes/${nodeId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (!response.ok) throw new Error('Failed to fetch node')
      return response.json()
    }
  })
}

export function useUpdateNode() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ nodeId, updates }: { nodeId: string, updates: Record<string, string> }) => {
      const response = await fetch(`/api/nodes/${nodeId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(updates)
      })
      if (!response.ok) throw new Error('Failed to update node')
      return response.json()
    },
    onSuccess: (_, { nodeId }) => {
      // Invalider le cache pour forcer un refresh
      queryClient.invalidateQueries({ queryKey: ['node', nodeId] })
    }
  })
}

export function useSearchNodes(searchTerm: string) {
  return useQuery<Node[]>({
    queryKey: ['nodes', 'search', searchTerm],
    queryFn: async () => {
      const response = await fetch(`/api/nodes/search?q=${encodeURIComponent(searchTerm)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (!response.ok) throw new Error('Search failed')
      return response.json()
    },
    enabled: searchTerm.length >= 3  // Ne requête que si >= 3 caractères
  })
}
```

### Composant d'Affichage de Nœud

**Fichier `frontend/src/components/NodeDetails.tsx` :**

```typescript
import React from 'react'
import { useNode, useUpdateNode } from '../hooks/useRDFQuery'
import { useState } from 'react'

interface NodeDetailsProps {
  nodeId: string
}

export function NodeDetails({ nodeId }: NodeDetailsProps) {
  const { data: node, isLoading, error } = useNode(nodeId)
  const updateMutation = useUpdateNode()

  const [editing, setEditing] = useState(false)
  const [description, setDescription] = useState('')

  if (isLoading) return <div>Chargement...</div>
  if (error) return <div>Erreur : {error.message}</div>
  if (!node) return <div>Nœud introuvable</div>

  const handleSave = async () => {
    await updateMutation.mutateAsync({
      nodeId: node.id,
      updates: { description }
    })
    setEditing(false)
  }

  return (
    <div className="node-details">
      <h2>{node.id}</h2>

      <div className="property">
        <strong>Type :</strong> {node.lnType}
      </div>

      <div className="property">
        <strong>Description :</strong>
        {editing ? (
          <div>
            <input
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
            <button onClick={handleSave}>Enregistrer</button>
            <button onClick={() => setEditing(false)}>Annuler</button>
          </div>
        ) : (
          <div>
            {node.description || '(aucune)'}
            <button onClick={() => {
              setDescription(node.description || '')
              setEditing(true)
            }}>
              Modifier
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
```

### Composant de Recherche

**Fichier `frontend/src/components/NodeSearch.tsx` :**

```typescript
import React, { useState } from 'react'
import { useSearchNodes } from '../hooks/useRDFQuery'

export function NodeSearch() {
  const [searchTerm, setSearchTerm] = useState('')
  const { data: results, isLoading } = useSearchNodes(searchTerm)

  return (
    <div className="node-search">
      <input
        type="text"
        placeholder="Rechercher un nœud..."
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
      />

      {isLoading && <div>Recherche en cours...</div>}

      {results && (
        <ul className="search-results">
          {results.map(node => (
            <li key={node.id}>
              <a href={`/nodes/${node.id}`}>
                {node.name} ({node.type})
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

### Visualisation en Arbre (Hiérarchie)

**Fichier `frontend/src/components/NodeTree.tsx` :**

```typescript
import React from 'react'
import { useQuery } from '@tanstack/react-query'

interface TreeNode {
  id: string
  name: string
  children?: TreeNode[]
}

export function NodeTree({ rootId }: { rootId: string }) {
  const { data: tree } = useQuery<TreeNode>({
    queryKey: ['tree', rootId],
    queryFn: async () => {
      const response = await fetch(`/api/nodes/${rootId}/tree`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      return response.json()
    }
  })

  if (!tree) return <div>Chargement...</div>

  return <TreeNodeComponent node={tree} level={0} />
}

function TreeNodeComponent({ node, level }: { node: TreeNode, level: number }) {
  const [expanded, setExpanded] = React.useState(true)

  return (
    <div style={{ marginLeft: level * 20 }}>
      <div onClick={() => setExpanded(!expanded)}>
        {node.children && (expanded ? '▼' : '▶')} {node.name}
      </div>

      {expanded && node.children && (
        <div>
          {node.children.map(child => (
            <TreeNodeComponent key={child.id} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  )
}
```

**Backend pour l'arbre :**

```python
@router.get("/{node_id}/tree")
def get_node_tree(node_id: str, user=Depends(require_permission("scd:view"))):
    """Récupère l'arbre des enfants d'un nœud"""
    query = f"""
    PREFIX iec: <http://iec61850.org/vocab#>
    PREFIX data: <http://myproject.com/data#>

    SELECT ?node ?child ?name
    WHERE {{
        data:{node_id}  iec:hasLogicalNode+  ?node .
        OPTIONAL {{ ?node  iec:hasLogicalNode  ?child }}
        OPTIONAL {{ ?node  iec:name  ?name }}
    }}
    """

    bindings = rdf_client.query(query)

    # Construire l'arbre
    nodes_map = {}
    for binding in bindings:
        node_id = binding["node"]["value"]
        if node_id not in nodes_map:
            nodes_map[node_id] = {
                "id": node_id,
                "name": binding.get("name", {}).get("value", node_id),
                "children": []
            }

        if "child" in binding:
            child_id = binding["child"]["value"]
            if child_id not in nodes_map:
                nodes_map[child_id] = {"id": child_id, "children": []}

            nodes_map[node_id]["children"].append(nodes_map[child_id])

    return nodes_map.get(f"http://myproject.com/data#{node_id}")
```

---

## Partie 14 : Tests et Validation

### Tests Unitaires des Requêtes SPARQL

**Fichier `tests/test_rdf_queries.py` :**

```python
import pytest
from rdf.client import rdf_client
from rdf.queries import get_logical_nodes, get_node_details

@pytest.fixture
def test_data():
    """Charge des données de test"""
    test_triples = """
    PREFIX iec: <http://iec61850.org/vocab#>
    PREFIX data: <http://myproject.com/data#>

    INSERT DATA {
        data:LD_TEST  a  iec:LogicalDevice .
        data:LN_TEST  a  iec:LogicalNode ;
                      iec:lnType  "MMXU" ;
                      iec:name  "Test Node" .
        data:LD_TEST  iec:hasLogicalNode  data:LN_TEST .
    }
    """
    rdf_client.update(test_triples)

    yield

    # Cleanup
    cleanup = """
    PREFIX data: <http://myproject.com/data#>
    DELETE WHERE {
        data:LD_TEST  ?p  ?o .
        data:LN_TEST  ?p2 ?o2 .
    }
    """
    rdf_client.update(cleanup)

def test_get_logical_nodes(test_data):
    """Test de la récupération des LogicalNodes"""
    query = get_logical_nodes("LD_TEST")
    bindings = rdf_client.query(query)

    assert len(bindings) == 1
    assert bindings[0]["type"]["value"] == "MMXU"

def test_get_node_details(test_data):
    """Test de la récupération des détails d'un nœud"""
    query = get_node_details("LN_TEST")
    bindings = rdf_client.query(query)

    properties = {b["property"]["value"].split("#")[-1]: b["value"]["value"]
                  for b in bindings}

    assert properties["lnType"] == "MMXU"
    assert properties["name"] == "Test Node"
```

### Tests d'Intégration des Routes

**Fichier `tests/test_node_routes.py` :**

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_node_unauthorized():
    """Test sans authentification"""
    response = client.get("/api/nodes/LN_TEST")
    assert response.status_code == 401

def test_get_node_with_auth(test_user_token):
    """Test avec authentification"""
    response = client.get(
        "/api/nodes/LN_TEST",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "LN_TEST"

def test_update_node(admin_token):
    """Test de mise à jour"""
    response = client.patch(
        "/api/nodes/LN_TEST",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"description": "Updated description"}
    )
    assert response.status_code == 200
```

### Validation de l'Ontologie

**Script `scripts/validate_ontology.py` :**

```python
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, OWL

def validate_ontology(ontology_file: str):
    """Valide qu'une ontologie est bien formée"""
    g = Graph()
    g.parse(ontology_file, format="turtle")

    errors = []

    # Vérifier que toutes les classes ont un label
    classes = g.subjects(RDF.type, OWL.Class)
    for cls in classes:
        if not (cls, RDFS.label, None) in g:
            errors.append(f"Class {cls} has no rdfs:label")

    # Vérifier que les propriétés ont domain et range
    properties = g.subjects(RDF.type, OWL.ObjectProperty)
    for prop in properties:
        if not (prop, RDFS.domain, None) in g:
            errors.append(f"Property {prop} has no rdfs:domain")
        if not (prop, RDFS.range, None) in g:
            errors.append(f"Property {prop} has no rdfs:range")

    return errors

if __name__ == "__main__":
    errors = validate_ontology("ontology/iec61850.ttl")
    if errors:
        print("Errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Ontology is valid!")
```

---

## Partie 15 : Production et Monitoring

### Configuration Production Fuseki

**docker-compose.production.yml :**

```yaml
version: '3.8'

services:
  fuseki:
    image: stain/jena-fuseki
    restart: always
    ports:
      - "3030:3030"
    environment:
      ADMIN_PASSWORD: ${FUSEKI_ADMIN_PASSWORD}
      JVM_ARGS: "-Xmx4G -Xms2G"  # Allouer plus de mémoire
    volumes:
      - fuseki_data:/fuseki
      - ./fuseki-config.ttl:/fuseki/config.ttl
    command: /jena-fuseki/fuseki-server --config=/fuseki/config.ttl
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3030/$/ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  fuseki_data:
    driver: local
```

### Monitoring avec Prometheus

**Wrapper pour métriques :**

```python
from prometheus_client import Counter, Histogram
import time

# Métriques
sparql_queries_total = Counter('sparql_queries_total', 'Total SPARQL queries', ['query_type'])
sparql_query_duration = Histogram('sparql_query_duration_seconds', 'SPARQL query duration')

class MonitoredRDFClient(RDFClient):
    def query(self, sparql_query: str):
        sparql_queries_total.labels(query_type='SELECT').inc()

        with sparql_query_duration.time():
            return super().query(sparql_query)

    def update(self, sparql_update: str):
        sparql_queries_total.labels(query_type='UPDATE').inc()

        with sparql_query_duration.time():
            return super().update(sparql_update)
```

### Backup et Restore

**Script `scripts/backup_rdf.sh` :**

```bash
#!/bin/bash

DATASET="iec61850_project1"
BACKUP_DIR="/backups/rdf"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Exporter toutes les données
curl -X GET "http://localhost:3030/${DATASET}/data" \
  -H "Accept: application/n-triples" \
  > "${BACKUP_DIR}/${DATASET}_${TIMESTAMP}.nt"

# Compresser
gzip "${BACKUP_DIR}/${DATASET}_${TIMESTAMP}.nt"

echo "Backup completed: ${DATASET}_${TIMESTAMP}.nt.gz"
```

**Script `scripts/restore_rdf.sh` :**

```bash
#!/bin/bash

DATASET="iec61850_project1"
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.nt.gz>"
    exit 1
fi

# Décompresser
gunzip -c "$BACKUP_FILE" > /tmp/restore.nt

# Charger dans Fuseki
curl -X POST "http://localhost:3030/${DATASET}/data" \
  -H "Content-Type: application/n-triples" \
  --data-binary @/tmp/restore.nt

rm /tmp/restore.nt

echo "Restore completed"
```

### Logging Avancé

**Fichier `rdf/client.py` (version production) :**

```python
import logging
from typing import Dict, List, Any
import time

logger = logging.getLogger(__name__)

class RDFClient:
    def query(self, sparql_query: str) -> List[Dict[str, Any]]:
        start_time = time.time()

        try:
            logger.debug(f"Executing SPARQL query:\n{sparql_query}")

            response = requests.post(
                self.sparql_endpoint,
                data={"query": sparql_query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=30
            )
            response.raise_for_status()

            duration = time.time() - start_time
            results = response.json()
            bindings = results.get("results", {}).get("bindings", [])

            logger.info(f"Query completed in {duration:.3f}s, returned {len(bindings)} results")

            if duration > 1.0:
                logger.warning(f"Slow query detected ({duration:.3f}s):\n{sparql_query}")

            return bindings

        except requests.exceptions.Timeout:
            logger.error("Query timeout after 30s")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
```

---

## Glossaire Complet RDF

**Concepts de base :**
- **RDF** : Resource Description Framework, modèle de données en triplets
- **Triplet** : unité de base (sujet, prédicat, objet)
- **Graphe** : ensemble de triplets interconnectés
- **IRI** : Internationalized Resource Identifier, identifiant unique
- **Namespace** : préfixe pour grouper des IRIs (ex: iec:, data:)

**Formats :**
- **Turtle** : format texte lisible (.ttl)
- **RDF/XML** : format XML standard
- **JSON-LD** : format JSON avec contexte
- **N-Triples** : format simple une ligne par triplet

**SPARQL :**
- **SELECT** : requête de lecture
- **INSERT** : ajout de triplets
- **DELETE** : suppression de triplets
- **ASK** : requête booléenne (existe/n'existe pas)
- **CONSTRUCT** : construit un nouveau graphe
- **FILTER** : condition de filtrage
- **LIMIT/OFFSET** : pagination
- **Property Path** : navigation récursive (ex: `+`, `*`, `^`)
- **OPTIONAL** : clause facultative
- **UNION** : alternative entre patterns
- **BIND** : création de variable calculée

**Stockage :**
- **Triple Store** : base de données RDF
- **Fuseki** : serveur RDF d'Apache Jena
- **Endpoint** : URL pour requêtes SPARQL
- **Dataset** : base de données nommée dans Fuseki
- **TDB2** : format de stockage persistant de Jena
- **Graphe nommé** : sous-graphe identifié (pour versionning)

**Ontologies :**
- **Ontologie** : vocabulaire de classes et propriétés
- **RDFS** : RDF Schema, ontologie basique
- **OWL** : Web Ontology Language, ontologie avancée
- **SHACL** : Shapes Constraint Language, validation
- **Domain** : classe du sujet d'une propriété
- **Range** : classe ou type de l'objet d'une propriété

**Architecture :**
- **Binding** : résultat d'une variable SPARQL
- **Prefixes** : déclaration de namespaces
- **Literal** : valeur brute (string, number, date)
- **Blank node** : nœud sans IRI (anonyme)

---

## Résumé : Quand Utiliser RDF ?

### ✅ RDF est Idéal Pour :

1. **Données fortement interconnectées**
   - Réseaux électriques (IEC 61850)
   - Graphes de connaissances
   - Systèmes complexes avec hiérarchies

2. **Structures évolutives**
   - Schéma qui change souvent
   - Ajout de nouveaux types sans migration

3. **Intégration de données**
   - Fusion de plusieurs sources
   - Ontologies standards (IEC, W3C)

4. **Navigation complexe**
   - Requêtes multi-niveaux
   - Chemins variables

5. **Versionning**
   - Historique complet
   - Comparaison entre versions

### ❌ RDF N'est PAS Idéal Pour :

1. **Données tabulaires simples**
   - Utilisateurs, produits
   - PostgreSQL est mieux

2. **Transactions ACID complexes**
   - RDF n'a pas de transactions multi-statements

3. **Données en temps réel haute fréquence**
   - RDF est plus lent que PostgreSQL

4. **Données textuelles**
   - Elasticsearch est mieux

---

## Conclusion

Ce guide couvre :
- ✅ Fondamentaux RDF (triplets, graphes, IRI)
- ✅ Formats (Turtle, RDF/XML, JSON-LD)
- ✅ SPARQL (SELECT, UPDATE, patterns avancés)
- ✅ Fuseki (installation, configuration)
- ✅ Intégration FastAPI + React
- ✅ Ontologies et validation
- ✅ Performance et optimisation
- ✅ Versionning avec graphes nommés
- ✅ Tests et production

Vous êtes maintenant équipé pour implémenter un système RDF dans votre architecture template !
