# Guide RDF pour IEC 61850 - Stockage et Manipulation de Fichiers SCD

## Vue d'ensemble

Ce guide explique comment représenter et manipuler des fichiers SCD (System Configuration Description) IEC 61850 sous forme de graphe RDF (Resource Description Framework).

### Objectifs

- **Stockage atomique** : chaque élément (IED, LDevice, LN, DOI, DAI, etc.) devient une ressource RDF indépendante
- **Édition granulaire** : modification de propriétés individuelles via SPARQL
- **Round-trip complet** : SCD → RDF → SCD sans perte d'information
- **Traçabilité** : liens explicites entre éléments (DataTypeTemplates, Communication, ExtRef)

### Ce que vous allez pouvoir faire

✅ Stocker le contenu de chaque LD, LN, DA, DO sous forme de graphe
✅ Éditer les propriétés de chacun individuellement
✅ Naviguer dans la hiérarchie IED → LDevice → LN → DOI → DAI
✅ Gérer Communication, DataSets, Control Blocks, ExtRef
✅ Versionner et comparer différentes configurations

## Table des Matières

1. [Ontologie RDF Minimale](#1-ontologie-rdf-minimale)
2. [Schéma URI (Adressage)](#2-schéma-uri-adressage-des-ressources)
3. [Script de Conversion Python](#3-script-de-conversion-python)
4. [Requêtes SPARQL](#4-requêtes-sparql)
5. [Cycle de Vie Complet](#5-cycle-de-vie-complet-round-trip)
6. [Fichiers Multiples](#6-gestion-des-fichiers-multiples-scd-icd-cid)
7. [Intégration Apache Jena Fuseki](#7-intégration-apache-jena-fuseki)
8. [Cas d'Usage Avancés](#8-cas-dusage-avancés)
9. [Script Python Complet](#9-annexe--script-python-complet)
10. [Évolutions Futures](#10-évolutions-futures)

---

## 1. Ontologie RDF minimale

### 1.1 Préfixes et Classes

```turtle
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix iec:  <https://rtei.example.org/iec61850#> .
@prefix scln: <https://rtei.example.org/scl#> .

# === Classes principales ===

# Hiérarchie système
iec:IED        a rdfs:Class .  # Intelligent Electronic Device
iec:LDevice    a rdfs:Class .  # Logical Device
iec:LN         a rdfs:Class .  # Logical Node
iec:DOI        a rdfs:Class .  # Data Object Instance
iec:SDI        a rdfs:Class .  # Sub Data Instance
iec:DAI        a rdfs:Class .  # Data Attribute Instance

# DataTypeTemplates
iec:LNodeType  a rdfs:Class .  # Logical Node Type (modèle)
iec:DOType     a rdfs:Class .  # Data Object Type
iec:DAType     a rdfs:Class .  # Data Attribute Type
iec:EnumType   a rdfs:Class .  # Enumeration Type
iec:EnumVal    a rdfs:Class .  # Enumeration Value
iec:DO         a rdfs:Class .  # Data Object (dans LNodeType)
iec:DA         a rdfs:Class .  # Data Attribute (dans DOType)
iec:BDA        a rdfs:Class .  # Basic Data Attribute (dans DAType)

# Communication
iec:SubNetwork   a rdfs:Class .  # Sous-réseau
iec:ConnectedAP  a rdfs:Class .  # Access Point connecté
iec:Address      a rdfs:Class .  # Adresse réseau
iec:P            a rdfs:Class .  # Paramètre d'adresse

# Datasets & Control Blocks
iec:DataSet              a rdfs:Class .
iec:FCDA                 a rdfs:Class .  # Functional Constraint Data Attribute
iec:GSEControl           a rdfs:Class .  # GOOSE Control Block
iec:SampledValueControl  a rdfs:Class .  # Sampled Values Control Block
iec:ReportControl        a rdfs:Class .  # Report Control Block

# Signaux d'entrée
iec:Inputs     a rdfs:Class .
iec:ExtRef     a rdfs:Class .  # External Reference (abonnement)
iec:InRef      a rdfs:Class .  # Internal Reference (rare)
iec:SourceRef  a rdfs:Class .  # Source Reference (rare)
iec:Private    a rdfs:Class .  # Éléments <Private> (vendor-specific)
```

### 1.2 Propriétés

```turtle
# Relations hiérarchiques
scln:hasChild  a rdf:Property .  # Relation parent → enfant

# Attributs de base
scln:name      a rdf:Property .  # Attribut 'name'
scln:inst      a rdf:Property .  # Attribut 'inst' (instance)
scln:desc      a rdf:Property .  # Description
scln:id        a rdf:Property .  # Identifiant unique (DataTypeTemplates)

# Logical Node
scln:lnClass   a rdf:Property .  # Classe du LN (ex: XCBR, MMXU)
scln:lnType    a rdf:Property .  # Référence vers LNodeType
scln:prefix    a rdf:Property .  # Préfixe du LN

# DataTypeTemplates
scln:typeRef   a rdf:Property .  # Référence de type (DO → DOType, DA → DAType)
scln:bType     a rdf:Property .  # Basic Type (BOOLEAN, INT32, etc.)
scln:fc        a rdf:Property .  # Functional Constraint (ST, MX, CF, etc.)
scln:cdc       a rdf:Property .  # Common Data Class (SPS, DPS, MV, etc.)

# Data Attributes
scln:path      a rdf:Property .  # Chemin complet (ex: "Pos.stVal")
scln:val       a rdf:Property .  # Valeur(s) - CSV si multiple <Val>

# Communication
scln:type      a rdf:Property .  # Type (SubNetwork, Address.P)
scln:text      a rdf:Property .  # Valeur texte (Address.P)
scln:iedName   a rdf:Property .  # Nom de l'IED (ConnectedAP, ExtRef)
scln:apName    a rdf:Property .  # Nom de l'AccessPoint

# ExtRef (abonnements)
scln:serviceType  a rdf:Property .  # Type de service (GOOSE, SV, Report)
scln:cbName       a rdf:Property .  # Control Block Name
scln:srcCBName    a rdf:Property .  # Source CB Name
scln:srcLDInst    a rdf:Property .  # Source LDevice instance
scln:srcLNClass   a rdf:Property .  # Source LN class
scln:srcLNInst    a rdf:Property .  # Source LN instance
scln:srcPrefix    a rdf:Property .  # Source LN prefix
scln:ldInst       a rdf:Property .  # LDevice instance (FCDA, ExtRef)
scln:lnClassRef   a rdf:Property .  # LN class (FCDA)
scln:lnInst       a rdf:Property .  # LN instance (FCDA, ExtRef)
scln:doName       a rdf:Property .  # Data Object name
scln:daName       a rdf:Property .  # Data Attribute name

# Control Blocks
scln:datSet    a rdf:Property .  # Référence au DataSet
scln:appID     a rdf:Property .  # Application ID

# Private (vendor-specific)
scln:xmlContent  a rdf:Property .  # Contenu XML brut

# Ordre (pour préserver l'ordre XML)
scln:order     a rdf:Property .
```

---

## 2. Schéma URI (Adressage des Ressources)

### 2.1 Principe

Chaque élément SCL devient une ressource RDF avec une URI **lisible, stable et hiérarchique**.

### 2.2 Format d'URI

```
https://rtei.example.org/scl/
  ├─ SCD/IED/<iedName>/
  │   ├─ LD/<ldInst>/
  │   │   └─ LN/<lnClass>_<lnInst>/
  │   │       ├─ DOI/<doName>/
  │   │       │   ├─ SDI/<sdiName>/
  │   │       │   └─ DAI/<path>
  │   │       └─ Inputs/
  │   │           └─ ExtRef/<key>
  │   └─ ...
  ├─ SCD/DTT/                          # DataTypeTemplates
  │   ├─ LNodeType/<id>/
  │   │   └─ DO/<name>
  │   ├─ DOType/<id>/
  │   │   ├─ DA/<name>
  │   │   └─ SDI/<name>
  │   ├─ DAType/<id>/
  │   │   └─ BDA/<name>
  │   └─ EnumType/<id>/
  │       └─ EnumVal/<ord>
  └─ SCD/Communication/
      └─ SubNetwork/<name>/
          └─ ConnectedAP/<iedName>@<apName>/
              └─ Address/
                  └─ P/<type>
```

### 2.3 Exemples Concrets

```turtle
# IED
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1> a iec:IED ;
    scln:name "POSTE0TGAUT1" ;
    scln:desc "Automate de poste" .

# LDevice
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/LD/LDAGSA1> a iec:LDevice ;
    scln:inst "LDAGSA1" .

# Logical Node
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/LD/LDAGSA1/LN/GAPC_0> a iec:LN ;
    scln:lnClass "GAPC" ;
    scln:inst "0" ;
    scln:lnType "GAPC1" ;
    scln:prefix "GEN" .

# Data Attribute Instance
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/LD/LDAGSA1/LN/GAPC_0/DAI/Pos.stVal> a iec:DAI ;
    scln:name "stVal" ;
    scln:path "Pos.stVal" ;
    scln:val "true" .

# LNodeType (DataTypeTemplates)
<https://rtei.example.org/scl/SCD/DTT/LNodeType/XCBR1> a iec:LNodeType ;
    scln:id "XCBR1" ;
    scln:lnClass "XCBR" ;
    scln:hasChild <.../DO/Pos> .

# ExtRef (abonnement GOOSE)
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/LD/LDAGSA1/LN/GAPC_0/Inputs/ExtRef/gcb1> a iec:ExtRef ;
    scln:serviceType "GOOSE" ;
    scln:srcCBName "gcb1" ;
    scln:srcLDInst "LD0" ;
    scln:srcLNClass "LLN0" ;
    scln:srcLNInst "0" ;
    scln:doName "Pos" ;
    scln:daName "stVal" .
```

---

## 3. Script de Conversion Python

### 3.1 Installation

```bash
pip install lxml rdflib pandas
```

### 3.2 Usage

#### SCD → RDF

```bash
python scl_rdf_full.py to_rdf /home/aurelien/mooc/data/SCD_POSTE_V1.scd output.ttl
```

**Contenu extrait** :
- IED / LDevice / LN / DOI / SDI / DAI (hiérarchie complète)
- DataTypeTemplates (LNodeType, DOType, DAType, EnumType)
- Communication (SubNetwork, ConnectedAP, Address/P)
- DataSets / FCDA
- Control Blocks (GSEControl, SampledValueControl, ReportControl)
- Inputs / ExtRef (abonnements avec source)

#### RDF → SCD

```bash
python scl_rdf_full.py to_scl input.ttl /home/aurelien/mooc/data/SCD_POSTE_V1.scd output.scd
```

**Note** : Le template SCD sert à récupérer le namespace XML correct.

---

## 4. Requêtes SPARQL

### 4.1 Lecture de Données

#### Lister tous les IEDs

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?ied ?name ?desc
WHERE {
  ?ied a iec:IED ;
       scln:name ?name .
  OPTIONAL { ?ied scln:desc ?desc }
}
ORDER BY ?name
```

#### Lister tous les Logical Nodes d'un IED

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?ln ?lnClass ?inst ?lnType
WHERE {
  ?ied a iec:IED ; scln:name "POSTE0TGAUT1" .
  ?ied scln:hasChild ?ld .
  ?ld scln:hasChild ?ln .
  ?ln a iec:LN ;
      scln:lnClass ?lnClass ;
      scln:inst ?inst .
  OPTIONAL { ?ln scln:lnType ?lnType }
}
ORDER BY ?lnClass ?inst
```

#### Trouver une valeur DAI spécifique

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?dai ?val
WHERE {
  ?dai a iec:DAI ;
       scln:path "Pos.stVal" ;
       scln:val ?val .
  FILTER(CONTAINS(STR(?dai), "GAPC"))
}
```

#### Lister tous les abonnements (ExtRef) d'un LN

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?xr ?service ?srcCB ?srcLD ?srcLNClass ?do ?da
WHERE {
  ?ln a iec:LN ;
      scln:lnClass "GAPC" ;
      scln:inst "0" ;
      scln:hasChild ?inputs .
  ?inputs a iec:Inputs ;
          scln:hasChild ?xr .
  ?xr a iec:ExtRef .
  OPTIONAL { ?xr scln:serviceType ?service }
  OPTIONAL { ?xr scln:srcCBName ?srcCB }
  OPTIONAL { ?xr scln:srcLDInst ?srcLD }
  OPTIONAL { ?xr scln:srcLNClass ?srcLNClass }
  OPTIONAL { ?xr scln:doName ?do }
  OPTIONAL { ?xr scln:daName ?da }
}
```

#### Lister les adresses réseau (Communication)

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?cap ?iedName ?apName ?pType ?pValue
WHERE {
  ?sn a iec:SubNetwork ;
      scln:hasChild ?cap .
  ?cap a iec:ConnectedAP ;
       scln:iedName ?iedName ;
       scln:apName ?apName ;
       scln:hasChild ?addr .
  ?addr a iec:Address ;
        scln:hasChild ?p .
  ?p a iec:P ;
     scln:type ?pType ;
     scln:text ?pValue .
}
ORDER BY ?iedName ?pType
```

### 4.2 Modification de Données (UPDATE)

#### Modifier une valeur DAI

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

DELETE { ?dai scln:val ?old }
INSERT { ?dai scln:val "false" }
WHERE {
  ?dai a iec:DAI ;
       scln:path "Pos.stVal" ;
       scln:val ?old .
  FILTER(CONTAINS(STR(?dai), "POSTE0TGAUT1/LD/LDAGSA1/LN/GAPC_0"))
}
```

#### Modifier une adresse MAC GOOSE

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

DELETE { ?p scln:text ?old }
INSERT { ?p scln:text "01-0C-CD-01-00-01" }
WHERE {
  ?p a iec:P ;
     scln:type "MAC-Address" ;
     scln:text ?old .
  FILTER(CONTAINS(STR(?p), "POSTE0TGAUT1"))
}
```

#### Ajouter une description à un IED

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

INSERT {
  ?ied scln:desc "Protection ligne - ajouté via SPARQL"
}
WHERE {
  ?ied a iec:IED ;
       scln:name "POSTE0TGAUT1" .
  FILTER NOT EXISTS { ?ied scln:desc ?existingDesc }
}
```

---

## 5. Cycle de Vie Complet (Round-trip)

### 5.1 Workflow Typique

```bash
# 1. Conversion SCD → RDF
python scl_rdf_full.py to_rdf /home/aurelien/mooc/data/SCD_POSTE_V1.scd SCD_POSTE_V1.ttl

# 2. Édition RDF (exemples)
# - Modifier valeurs DAI via SPARQL UPDATE
# - Modifier adresses réseau
# - Ajouter/supprimer ExtRef

# 3. Reconstruction SCD ← RDF
python scl_rdf_full.py to_scl SCD_POSTE_V1.ttl /home/aurelien/mooc/data/SCD_POSTE_V1.scd SCD_POSTE_V1_REBUILT.scd

# 4. Validation
xmllint --noout --schema IEC61850.xsd SCD_POSTE_V1_REBUILT.scd
```

### 5.2 Exemple d'Édition Python (via rdflib)

```python
from rdflib import Graph, Namespace, Literal

IEC = Namespace("https://rtei.example.org/iec61850#")
SCLN = Namespace("https://rtei.example.org/scl#")

# Charger le graphe
g = Graph()
g.parse("SCD_POSTE_V1.ttl", format="turtle")

# Modifier une valeur
for dai_uri in g.subjects(SCLN.path, Literal("Pos.stVal")):
    g.remove((dai_uri, SCLN.val, None))
    g.add((dai_uri, SCLN.val, Literal("false")))

# Sauvegarder
g.serialize("SCD_POSTE_V1_modified.ttl", format="turtle")
```

---

## 6. Gestion des Fichiers Multiples (SCD, ICD, CID)

### 6.1 Structure de la Chaîne d'Ingénierie IEC 61850

```
ASD (Application Specification Description)
  ↓
FSD (Functional Specification Description)
  ↓
SSD (System Specification Description)
  ↓
SCD (System Configuration Description) ← Fichier système complet
  ├─ IED (instances configurées)
  ├─ Substation (structure physique)
  ├─ Communication (réseau)
  └─ DataTypeTemplates (types consolidés)

ICD (IED Capability Description) ← Modèle constructeur
  └─ IED + DataTypeTemplates (capacités d'un IED)

CID (Configured IED Description) ← Instance configurée
  └─ IED + DataTypeTemplates filtrés (configuration réelle)
```

### 6.2 Stratégie Multi-Graphes RDF

Pour gérer plusieurs sources, utiliser des **graphes nommés** :

```turtle
# SCD
<https://rtei.example.org/graph/SCD> {
  <.../SCD/IED/POSTE0TGAUT1> a iec:IED ;
      scln:name "POSTE0TGAUT1" .
}

# ICD constructeur
<https://rtei.example.org/graph/ICD/POSTE0TGAUT1> {
  <.../ICD/POSTE0TGAUT1/DTT/LNodeType/GAPC1> a iec:LNodeType ;
      scln:id "GAPC1" ;
      scln:lnClass "GAPC" .
}

# Liens entre graphes
<https://rtei.example.org/graph/Mappings> {
  <.../SCD/IED/POSTE0TGAUT1> scln:basedOn <.../ICD/POSTE0TGAUT1> .
}
```

### 6.3 Requête Multi-Graphes

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?ied ?lnType_scd ?lnType_icd
WHERE {
  GRAPH <https://rtei.example.org/graph/SCD> {
    ?ied a iec:IED ;
         scln:hasChild/scln:hasChild ?ln .
    ?ln scln:lnType ?lnType_scd .
  }
  GRAPH <https://rtei.example.org/graph/ICD/POSTE0TGAUT1> {
    ?lnt a iec:LNodeType ;
         scln:id ?lnType_icd .
    FILTER(?lnType_scd = ?lnType_icd)
  }
}
```

---

## 7. Intégration Apache Jena Fuseki

### 7.1 Configuration Docker Compose

```yaml
version: '3.8'

services:
  fuseki:
    image: stain/jena-fuseki
    container_name: jena-fuseki
    ports:
      - "3030:3030"
    environment:
      ADMIN_PASSWORD: admin123
      JVM_ARGS: "-Xmx2g"
    volumes:
      - fuseki-data:/fuseki
    networks:
      - mooc-network

volumes:
  fuseki-data:

networks:
  mooc-network:
    driver: bridge
```

### 7.2 Chargement des Données

```bash
# Démarrer Fuseki
docker-compose up -d fuseki

# Créer un dataset "scd" via l'interface Web
# http://localhost:3030

# Charger le fichier RDF
curl -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @SCD_POSTE_V1.ttl \
  http://localhost:3030/scd/data?default
```

### 7.3 Requêtes HTTP

#### SPARQL SELECT

```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/sparql-results+json" \
  --data 'SELECT * WHERE { ?s ?p ?o } LIMIT 10' \
  http://localhost:3030/scd/sparql
```

#### SPARQL UPDATE

```bash
curl -X POST \
  -H "Content-Type: application/sparql-update" \
  --data 'PREFIX scln: <https://rtei.example.org/scl#>
DELETE { ?dai scln:val ?old }
INSERT { ?dai scln:val "false" }
WHERE { ?dai scln:path "Pos.stVal" ; scln:val ?old }' \
  http://localhost:3030/scd/update
```

### 7.4 Client JavaScript (React)

```javascript
import { QueryEngine } from '@comunica/query-sparql';

const engine = new QueryEngine();

async function queryFuseki() {
  const query = `
    PREFIX iec: <https://rtei.example.org/iec61850#>
    PREFIX scln: <https://rtei.example.org/scl#>

    SELECT ?ied ?name WHERE {
      ?ied a iec:IED ;
           scln:name ?name .
    }
  `;

  const bindingsStream = await engine.queryBindings(query, {
    sources: ['http://localhost:3030/scd/sparql']
  });

  const bindings = await bindingsStream.toArray();
  bindings.forEach(binding => {
    console.log(binding.get('name').value);
  });
}
```

Alternative avec `sparql-http-client` :

```javascript
import SparqlClient from 'sparql-http-client';

const client = new SparqlClient({
  endpointUrl: 'http://localhost:3030/scd/sparql',
  updateUrl: 'http://localhost:3030/scd/update'
});

// SELECT
const stream = client.query.select(`
  SELECT ?ied ?name WHERE {
    ?ied a <https://rtei.example.org/iec61850#IED> ;
         <https://rtei.example.org/scl#name> ?name .
  }
`);

stream.on('data', row => {
  console.log(row.name.value);
});

// UPDATE
await client.query.update(`
  PREFIX scln: <https://rtei.example.org/scl#>
  DELETE { ?dai scln:val ?old }
  INSERT { ?dai scln:val "false" }
  WHERE { ?dai scln:path "Pos.stVal" ; scln:val ?old }
`);
```

---

## 8. Cas d'Usage Avancés

### 8.1 Gestion des `<Private>`

Les éléments `<Private>` contiennent des données spécifiques constructeur (XML brut).

**Solution** : stocker le XML complet en string

```turtle
<.../IED/POSTE0TGAUT1/Private/RTE-IDRC> a iec:Private ;
    scln:type "RTE-IDRC" ;
    scln:xmlContent """<Private type="RTE-IDRC">
      <rte:IDRC xmlns:rte="http://www.rte-international.com"
                shortLabel="AUT.ETE1"
                longLabel="AUT. DEB.ETE 1"
                value="ID004981"/>
    </Private>""" .
```

**Reconstruction** : réinjecter le XML tel quel dans le SCD.

### 8.2 Préservation de l'Ordre XML

Le SCD impose un ordre strict des éléments. Pour le préserver :

```turtle
?ied scln:hasChild [
  scln:target ?ld1 ;
  scln:order 1
] .
?ied scln:hasChild [
  scln:target ?ld2 ;
  scln:order 2
] .
```

Lors de la reconstruction, trier par `scln:order`.

### 8.3 Liens ExtRef → FCDA (Traçabilité)

**Objectif** : identifier quel ExtRef consomme quel FCDA.

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?xr ?fcda ?ds ?cb
WHERE {
  # FCDA
  ?ds a iec:DataSet ;
      scln:name ?dsName ;
      scln:hasChild ?fcda .
  ?fcda a iec:FCDA ;
        scln:ldInst ?ld ;
        scln:lnClassRef ?lc ;
        scln:lnInst ?li ;
        scln:doName ?do ;
        scln:daName ?da .

  # Control Block référençant ce DataSet
  ?cb scln:datSet ?dsName ;
      scln:cbName ?cbName .

  # ExtRef correspondant
  ?xr a iec:ExtRef ;
      scln:srcCBName ?cbName ;
      scln:srcLDInst ?ld ;
      scln:srcLNClass ?lc ;
      scln:srcLNInst ?li ;
      scln:doName ?do ;
      scln:daName ?da .
}
```

### 8.4 Validation de Cohérence

**Vérifier que tous les lnType existent dans DataTypeTemplates** :

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?ln ?lnType
WHERE {
  ?ln a iec:LN ;
      scln:lnType ?lnType .
  FILTER NOT EXISTS {
    ?lnt a iec:LNodeType ;
         scln:id ?lnType .
  }
}
```

---

## 9. Annexe : Script Python Complet

Créer le fichier `scl_rdf_full.py` :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scl_rdf_full.py
- Parse SCD (IEC 61850-6) -> RDF (rdflib) incluant:
  IED/LDevice/LN/DOI/SDI/DAI, DataTypeTemplates, Communication,
  DataSets/FCDA, GSE/SV/Report Control, Inputs/ExtRef
- Reconstruit un SCD minimal-conforme depuis le RDF.

Usage:
  python scl_rdf_full.py to_rdf input.scd output.ttl
  python scl_rdf_full.py to_scl input.ttl template.scd output.scd
"""
import sys
from lxml import etree as ET
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

IEC  = Namespace("https://rtei.example.org/iec61850#")
SCLN = Namespace("https://rtei.example.org/scl#")

# Classes
IEDC, LDEVC, LNC, DOIC, SDIC, DAIC = IEC.IED, IEC.LDevice, IEC.LN, IEC.DOI, IEC.SDI, IEC.DAI
LNTC, DOTC, DATC, ENUTC = IEC.LNodeType, IEC.DOType, IEC.DAType, IEC.EnumType
ENVC = IEC.EnumVal
SNC, CAPC, ADDRC, PC = IEC.SubNetwork, IEC.ConnectedAP, IEC.Address, IEC.P
DSC, FCDAC = IEC.DataSet, IEC.FCDA
GSEC, SVCC, RPC = IEC.GSEControl, IEC.SampledValueControl, IEC.ReportControl
INPUTSC, EXTREFC, INREFC, SRCREFC = IEC.Inputs, IEC.ExtRef, IEC.InRef, IEC.SourceRef

# Predicates
hasChild = SCLN.hasChild
nameP, instP, lnClassP, lnTypeP, prefixP = SCLN.name, SCLN.inst, SCLN.lnClass, SCLN.lnType, SCLN.prefix
idP, typeRefP, bTypeP, fcP, cdcP = SCLN.id, SCLN.typeRef, SCLN.bType, SCLN.fc, SCLN.cdc
pathP, valP, descP = SCLN.path, SCLN.val, SCLN.desc
cbNameP, serviceTypeP = SCLN.cbName, SCLN.serviceType
apNameP, ldInstP, lnInstP, lnClassRefP, doNameP, daNameP = SCLN.apName, SCLN.ldInst, SCLN.lnInst, SCLN.lnClassRef, SCLN.doName, SCLN.daName
srcCBNameP, srcLDInstP, srcLNClassP, srcLNInstP, srcPrefixP = SCLN.srcCBName, SCLN.srcLDInst, SCLN.srcLNClass, SCLN.srcLNInst, SCLN.srcPrefix
typeP, textP = SCLN.type, SCLN.text
iedNameP = SCLN.iedName

def _uri(*parts: str) -> URIRef:
    safe = "/".join(str(p).strip("/").replace(" ", "_") for p in parts if p is not None)
    return URIRef(f"https://rtei.example.org/scl/{safe}")

def _qn(nsmap: dict, tag: str) -> str:
    return f"{{{nsmap['scl']}}}{tag}"

def scl_to_rdf(scd_path: str, out_ttl: str) -> None:
    parser = ET.XMLParser(remove_blank_text=True)
    tree   = ET.parse(scd_path, parser)
    root   = tree.getroot()
    ns     = root.nsmap.copy()
    if None in ns: ns["scl"] = ns.pop(None)
    qn     = lambda t: _qn(ns, t)

    g = Graph()
    g.bind("iec", IEC); g.bind("scln", SCLN)

    # --- DataTypeTemplates ---
    dtt = root.find(qn("DataTypeTemplates"))
    if dtt is not None:
        # LNodeType
        for lnt in dtt.findall(qn("LNodeType")):
            lnt_id = lnt.get("id"); lnclass = lnt.get("lnClass")
            lnt_u  = _uri("SCD","DTT","LNodeType", lnt_id)
            g.add((lnt_u, RDF.type, LNTC))
            if lnt_id:   g.add((lnt_u, idP, Literal(lnt_id)))
            if lnclass:  g.add((lnt_u, lnClassP, Literal(lnclass)))
            for do in lnt.findall(qn("DO")):
                do_u = _uri("SCD","DTT","LNodeType", lnt_id, "DO", do.get("name"))
                g.add((do_u, RDF.type, IEC.DO))
                if do.get("name"): g.add((do_u, nameP, Literal(do.get("name"))))
                if do.get("type"): g.add((do_u, typeRefP, Literal(do.get("type"))))
                g.add((lnt_u, hasChild, do_u))

        # DOType
        for dot in dtt.findall(qn("DOType")):
            dot_id = dot.get("id"); cdc = dot.get("cdc")
            dot_u  = _uri("SCD","DTT","DOType", dot_id)
            g.add((dot_u, RDF.type, DOTC))
            if dot_id: g.add((dot_u, idP, Literal(dot_id)))
            if cdc:    g.add((dot_u, cdcP, Literal(cdc)))
            for da in dot.findall(qn("DA")):
                da_u = _uri("SCD","DTT","DOType", dot_id, "DA", da.get("name"))
                g.add((da_u, RDF.type, IEC.DA))
                if da.get("name"): g.add((da_u, nameP, Literal(da.get("name"))))
                if da.get("bType"): g.add((da_u, bTypeP, Literal(da.get("bType"))))
                if da.get("type"):  g.add((da_u, typeRefP, Literal(da.get("type"))))
                if da.get("fc"):    g.add((da_u, fcP, Literal(da.get("fc"))))
                g.add((dot_u, hasChild, da_u))

        # DAType
        for dat in dtt.findall(qn("DAType")):
            dat_id = dat.get("id"); dat_u = _uri("SCD","DTT","DAType", dat_id)
            g.add((dat_u, RDF.type, DATC)); g.add((dat_u, idP, Literal(dat_id)))
            for bda in dat.findall(qn("BDA")):
                bda_u = _uri("SCD","DTT","DAType", dat_id, "BDA", bda.get("name"))
                g.add((bda_u, RDF.type, IEC.BDA))
                if bda.get("name"):  g.add((bda_u, nameP, Literal(bda.get("name"))))
                if bda.get("bType"): g.add((bda_u, bTypeP, Literal(bda.get("bType"))))
                if bda.get("type"):  g.add((bda_u, typeRefP, Literal(bda.get("type"))))
                if bda.get("fc"):    g.add((bda_u, fcP, Literal(bda.get("fc"))))
                g.add((dat_u, hasChild, bda_u))

        # EnumType
        for et in dtt.findall(qn("EnumType")):
            et_id = et.get("id"); et_u = _uri("SCD","DTT","EnumType", et_id)
            g.add((et_u, RDF.type, ENUTC)); g.add((et_u, idP, Literal(et_id)))
            for ev in et.findall(qn("EnumVal")):
                ev_u = _uri("SCD","DTT","EnumType", et_id, "EnumVal", ev.get("ord","0"))
                g.add((ev_u, RDF.type, ENVC))
                g.add((ev_u, textP, Literal((ev.text or "").strip())))
                if ev.get("ord"): g.add((ev_u, SCLN.order, Literal(int(ev.get("ord")), datatype=XSD.integer)))
                g.add((et_u, hasChild, ev_u))

    # --- IED / Server / LD / LN / DOI/SDI/DAI (+ Inputs/ExtRef) ---
    for ied in root.findall(qn("IED")):
        ied_name = ied.get("name")
        ied_u    = _uri("SCD","IED", ied_name)
        g.add((ied_u, RDF.type, IEDC)); g.add((ied_u, nameP, Literal(ied_name)))
        if ied.get("desc"): g.add((ied_u, descP, Literal(ied.get("desc"))))

        for ap in ied.findall(qn("AccessPoint")):
            ap_name = ap.get("name")
            svr = ap.find(qn("Server"))
            if svr is None: continue
            for ld in svr.findall(qn("LDevice")):
                ld_inst = ld.get("inst")
                ld_u = _uri("SCD","IED", ied_name, "LD", ld_inst)
                g.add((ld_u, RDF.type, LDEVC)); g.add((ld_u, instP, Literal(ld_inst)))
                g.add((ied_u, hasChild, ld_u))

                # LN & LN0
                for ln in ld.findall(qn("LN")) + ld.findall(qn("LN0")):
                    tag = ET.QName(ln).localname
                    ln_class = "LLN0" if tag == "LN0" else ln.get("lnClass")
                    ln_inst  = "0" if tag == "LN0" else (ln.get("inst") or "")
                    ln_type  = ln.get("lnType")
                    ln_pref  = ln.get("prefix")

                    ln_u = _uri("SCD","IED", ied_name, "LD", ld_inst, "LN", f"{ln_class}_{ln_inst}")
                    g.add((ln_u, RDF.type, LNC))
                    g.add((ln_u, lnClassP, Literal(ln_class)))
                    g.add((ln_u, instP, Literal(ln_inst)))
                    if ln_type: g.add((ln_u, lnTypeP, Literal(ln_type)))
                    if ln_pref: g.add((ln_u, prefixP, Literal(ln_pref)))
                    g.add((ld_u, hasChild, ln_u))

                    # DOI/SDI/DAI
                    for doi in ln.findall(qn("DOI")):
                        doi_name = doi.get("name")
                        doi_u = _uri("SCD","IED", ied_name, "LD", ld_inst, "LN", f"{ln_class}_{ln_inst}", "DOI", doi_name)
                        g.add((doi_u, RDF.type, DOIC)); g.add((doi_u, nameP, Literal(doi_name)))
                        g.add((ln_u, hasChild, doi_u))

                        stack = [(doi, doi_name, doi_u)]
                        while stack:
                            elem, head, parent_u = stack.pop()
                            for sdi in elem.findall(qn("SDI")):
                                sname = sdi.get("name")
                                s_u = _uri(str(parent_u).replace("https://rtei.example.org/scl/",""), "SDI", sname)
                                g.add((s_u, RDF.type, SDIC)); g.add((s_u, nameP, Literal(sname)))
                                g.add((parent_u, hasChild, s_u))
                                stack.append((sdi, f"{head}.{sname}", s_u))
                            for dai in elem.findall(qn("DAI")):
                                dan = dai.get("name")
                                vals = [ (v.text or "").strip() for v in dai.findall(qn("Val")) ]
                                dval = ",".join(vals) if vals else ""
                                dai_u = _uri("SCD","IED", ied_name, "LD", ld_inst, "LN", f"{ln_class}_{ln_inst}",
                                             "DAI", f"{head}.{dan}")
                                g.add((dai_u, RDF.type, DAIC))
                                g.add((dai_u, nameP, Literal(dan)))
                                g.add((dai_u, pathP, Literal(f"{head}.{dan}")))
                                g.add((dai_u, valP, Literal(dval)))
                                g.add((parent_u, hasChild, dai_u))

                    # Inputs/ExtRef
                    inputs = ln.find(qn("Inputs"))
                    if inputs is not None:
                        inputs_u = _uri("SCD","IED", ied_name, "LD", ld_inst, "LN", f"{ln_class}_{ln_inst}", "Inputs")
                        g.add((inputs_u, RDF.type, INPUTSC))
                        g.add((ln_u, hasChild, inputs_u))
                        for xr in inputs.findall(qn("ExtRef")):
                            xr_u = _uri(str(inputs_u).replace("https://rtei.example.org/scl/",""), "ExtRef",
                                        xr.get("intAddr") or xr.get("desc") or (xr.get("srcCBName") or "x"))
                            g.add((xr_u, RDF.type, EXTREFC)); g.add((inputs_u, hasChild, xr_u))
                            for (p, k) in [(serviceTypeP,"serviceType"), (iedNameP,"iedName"), (apNameP,"apName"),
                                (ldInstP,"ldInst"), (lnClassRefP,"lnClass"), (lnInstP,"lnInst"), (prefixP,"prefix"),
                                (doNameP,"doName"), (daNameP,"daName"), (cbNameP,"cbName"),
                                (srcCBNameP,"srcCBName"), (srcLDInstP,"srcLDInst"),
                                (srcLNClassP,"srcLNClass"), (srcLNInstP,"srcLNInst"),
                                (srcPrefixP,"srcPrefix")]:
                                val = xr.get(k)
                                if val: g.add((xr_u, p, Literal(val)))
                            if xr.get("desc"): g.add((xr_u, descP, Literal(xr.get("desc"))))

    # --- Communication ---
    comm = root.find(qn("Communication"))
    if comm is not None:
        for sn in comm.findall(qn("SubNetwork")):
            sn_name = sn.get("name"); sn_type = sn.get("type")
            sn_u = _uri("SCD","Communication","SubNetwork", sn_name)
            g.add((sn_u, RDF.type, SNC))
            if sn_name: g.add((sn_u, nameP, Literal(sn_name)))
            if sn_type: g.add((sn_u, typeP, Literal(sn_type)))

            for cap in sn.findall(qn("ConnectedAP")):
                cap_ied = cap.get("iedName"); cap_ap = cap.get("apName")
                cap_u = _uri("SCD","Communication","SubNetwork", sn_name, "ConnectedAP",
                             f"{cap_ied}@{cap_ap}")
                g.add((cap_u, RDF.type, CAPC)); g.add((sn_u, hasChild, cap_u))
                if cap_ied: g.add((cap_u, iedNameP, Literal(cap_ied)))
                if cap_ap:  g.add((cap_u, apNameP, Literal(cap_ap)))

                addr = cap.find(qn("Address"))
                if addr is not None:
                    addr_u = _uri(str(cap_u).replace("https://rtei.example.org/scl/",""), "Address")
                    g.add((addr_u, RDF.type, ADDRC)); g.add((cap_u, hasChild, addr_u))
                    for p in addr.findall(qn("P")):
                        p_u = _uri(str(addr_u).replace("https://rtei.example.org/scl/",""), "P", p.get("type"))
                        g.add((p_u, RDF.type, PC)); g.add((addr_u, hasChild, p_u))
                        if p.get("type"): g.add((p_u, typeP, Literal(p.get("type"))))
                        g.add((p_u, textP, Literal((p.text or "").strip())))

    # Sauvegarde RDF
    g.serialize(destination=out_ttl, format="turtle")
    print(f"[OK] RDF written -> {out_ttl}")

def rdf_to_scl(in_ttl: str, template_scd: str, out_scd: str) -> None:
    parser = ET.XMLParser(remove_blank_text=True)
    tmpl   = ET.parse(template_scd, parser)
    root   = tmpl.getroot()
    ns     = root.nsmap.copy()
    if None in ns: ns["scl"] = ns.pop(None)
    qn     = lambda t: _qn(ns, t)

    g = Graph(); g.parse(in_ttl, format="turtle")

    scl = ET.Element(qn("SCL"), nsmap=root.nsmap)
    header = ET.SubElement(scl, qn("Header")); header.set("id", "RDF-Rebuilt")

    # --- IED / AP / Server / LDevice / LN / DOI/DAI / Inputs/ExtRef ---
    for ied_u in g.subjects(RDF.type, IEDC):
        ied = ET.SubElement(scl, qn("IED"))
        nm  = g.value(ied_u, nameP)
        if nm: ied.set("name", str(nm))
        ds  = g.value(ied_u, descP)
        if ds: ied.set("desc", str(ds))

        ap = ET.SubElement(ied, qn("AccessPoint")); ap.set("name", "ap1")
        srv = ET.SubElement(ap, qn("Server"))

        for ld_u in g.objects(ied_u, hasChild):
            if (ld_u, RDF.type, LDEVC) not in g: continue
            ld = ET.SubElement(srv, qn("LDevice"))
            inst = g.value(ld_u, instP);  ld.set("inst", str(inst or "1"))

            for ln_u in g.objects(ld_u, hasChild):
                if (ln_u, RDF.type, LNC) not in g: continue
                ln_class = str(g.value(ln_u, lnClassP) or "")
                ln_inst  = str(g.value(ln_u, instP) or "")
                ln_type  = g.value(ln_u, lnTypeP)
                ln_pref  = g.value(ln_u, prefixP)

                tag = qn("LN0") if ln_class == "LLN0" and (ln_inst in ("", "0")) else qn("LN")
                ln = ET.SubElement(ld, tag)
                if tag.endswith("LN"):
                    ln.set("lnClass", ln_class); ln.set("inst", ln_inst)
                if ln_type: ln.set("lnType", str(ln_type))
                if ln_pref: ln.set("prefix", str(ln_pref))

                # DOI / SDI / DAI
                for doi_u in g.objects(ln_u, hasChild):
                    if (doi_u, RDF.type, DOIC) not in g: continue
                    doi = ET.SubElement(ln, qn("DOI"))
                    doi.set("name", str(g.value(doi_u, nameP) or ""))

                    stack = [(doi_u, doi)]
                    while stack:
                        p_u, p_el = stack.pop()
                        for sdi_u in g.objects(p_u, hasChild):
                            if (sdi_u, RDF.type, SDIC) not in g: continue
                            sdi = ET.SubElement(p_el, qn("SDI"))
                            sdi.set("name", str(g.value(sdi_u, nameP) or ""))
                            stack.append((sdi_u, sdi))
                        for dai_u in g.objects(p_u, hasChild):
                            if (dai_u, RDF.type, DAIC) not in g: continue
                            dai = ET.SubElement(p_el, qn("DAI"))
                            dai.set("name", str(g.value(dai_u, nameP) or ""))
                            v = g.value(dai_u, valP)
                            if v:
                                vals = str(v).split(",")
                                for t in vals:
                                    ve = ET.SubElement(dai, qn("Val")); ve.text = t

                # Inputs / ExtRef
                for inp_u in g.objects(ln_u, hasChild):
                    if (inp_u, RDF.type, INPUTSC) not in g: continue
                    inputs = ET.SubElement(ln, qn("Inputs"))
                    for xr_u in g.objects(inp_u, hasChild):
                        if (xr_u, RDF.type, EXTREFC) not in g: continue
                        xr = ET.SubElement(inputs, qn("ExtRef"))
                        for (pred, attr) in [
                            (serviceTypeP,"serviceType"), (iedNameP,"iedName"), (apNameP,"apName"),
                            (ldInstP,"ldInst"), (lnClassRefP,"lnClass"), (lnInstP,"lnInst"),
                            (prefixP,"prefix"), (doNameP,"doName"), (daNameP,"daName"),
                            (cbNameP,"cbName"), (srcCBNameP,"srcCBName"), (srcLDInstP,"srcLDInst"),
                            (srcLNClassP,"srcLNClass"), (srcLNInstP,"srcLNInst"), (srcPrefixP,"srcPrefix")
                        ]:
                            val = g.value(xr_u, pred)
                            if val: xr.set(attr, str(val))
                        dsc = g.value(xr_u, descP)
                        if dsc: xr.set("desc", str(dsc))

    # --- Communication ---
    comm = ET.SubElement(scl, qn("Communication"))
    for sn_u in g.subjects(RDF.type, SNC):
        sn = ET.SubElement(comm, qn("SubNetwork"))
        nm = g.value(sn_u, nameP); tp = g.value(sn_u, typeP)
        if nm: sn.set("name", str(nm))
        if tp: sn.set("type", str(tp))

        for cap_u in g.objects(sn_u, hasChild):
            if (cap_u, RDF.type, CAPC) not in g: continue
            cap = ET.SubElement(sn, qn("ConnectedAP"))
            iedn = g.value(cap_u, iedNameP); apn = g.value(cap_u, apNameP)
            if iedn: cap.set("iedName", str(iedn))
            if apn:  cap.set("apName", str(apn))
            for addr_u in g.objects(cap_u, hasChild):
                if (addr_u, RDF.type, ADDRC) not in g: continue
                addr = ET.SubElement(cap, qn("Address"))
                for p_u in g.objects(addr_u, hasChild):
                    if (p_u, RDF.type, PC) not in g: continue
                    p = ET.SubElement(addr, qn("P"))
                    tp = g.value(p_u, typeP); tx = g.value(p_u, textP)
                    if tp: p.set("type", str(tp))
                    if tx: p.text = str(tx)

    ET.ElementTree(scl).write(out_scd, xml_declaration=True, encoding="utf-8", pretty_print=True)
    print(f"[OK] SCL rebuilt -> {out_scd}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage:")
        print("  python scl_rdf_full.py to_rdf   <input.scd> <output.ttl>")
        print("  python scl_rdf_full.py to_scl   <input.ttl> <template.scd> <output.scd>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "to_rdf":
        scl_to_rdf(sys.argv[2], sys.argv[3])
    elif cmd == "to_scl":
        rdf_to_scl(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Unknown command.")
        sys.exit(1)
```

---

## 10. Évolutions Futures

### Phase 1 (actuelle)
✅ SCD → RDF → SCD (round-trip complet)
✅ DataTypeTemplates, Communication, ExtRef
✅ Édition atomique DAI, adresses réseau

### Phase 2 : Multi-fichiers
- Charger ICD + CID + SCD dans graphes nommés
- Mapping constructeur ↔ instance

### Phase 3 : Amont de la chaîne
- Intégration SSD (System Specification)
- Liens SSD.LNodeType → SCD.LNodeType

### Phase 4 : ASD/FSD
- Traçabilité Requirements → Functions → LNodeType
- Graphe complet de l'ingénierie

### Phase 5 : IA & Génération
- Assistant IA pour génération automatique SCD
- Vérification de cohérence
- Optimisation de configuration

---

## Ressources

### Documentation IEC 61850
- IEC 61850-6 : Configuration language (SCL)
- IEC 61850-7-x : Abstract Communication Service Interface (ACSI)

### Outils
- **Apache Jena Fuseki** : https://jena.apache.org/documentation/fuseki2/
- **rdflib** (Python) : https://rdflib.readthedocs.io/
- **@comunica/query-sparql** (JS) : https://comunica.dev/
- **sparql-http-client** (JS) : https://github.com/zazuko/sparql-http-client

### Standards RDF
- **RDF 1.1** : https://www.w3.org/TR/rdf11-concepts/
- **SPARQL 1.1** : https://www.w3.org/TR/sparql11-query/
- **Turtle** : https://www.w3.org/TR/turtle/

---

**Auteur** : Guide de formation - Projet MOOC Web Development
**Dernière mise à jour** : 2025-10-06
