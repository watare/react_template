# Ontologie RDF IEC 61850 avec Versioning Atomique Complet

## Vue d'ensemble

Cette ontologie étend le modèle RDF de base pour gérer le **versioning atomique** de chaque élément IEC 61850 (IED, LD, LN, DO, DA, DAI, etc.) avec trois dimensions de traçabilité :

1. **Version de l'élément** : V0, V0.1, V1.0, etc. (évolution de la configuration)
2. **Édition du standard** : IEC 61850-7-4 Ed1, Ed2, Ed2.1, etc.
3. **Version du profil** : RTE_2017, RTE_2020, MANUFACTURER_PROFILE_V3, etc.

### Objectifs

✅ **Versioning atomique** : chaque IED, LD, LN, DO, DA, DAI a sa propre version
✅ **Traçabilité standard** : lien explicite vers l'édition IEC 61850
✅ **Conformité profil** : support des profils constructeur/utilisateur
✅ **Configuration figée** : récupération de la configuration complète à une version donnée
✅ **Évolution contrôlée** : historique des modifications de chaque élément

---

## 1. Ontologie Complète

### 1.1 Préfixes

```turtle
@prefix rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .
@prefix owl:      <http://www.w3.org/2002/07/owl#> .
@prefix dcterms:  <http://purl.org/dc/terms/> .

@prefix iec:      <https://rtei.example.org/iec61850#> .
@prefix scln:     <https://rtei.example.org/scl#> .
@prefix std:      <https://rtei.example.org/standard#> .
@prefix profile:  <https://rtei.example.org/profile#> .
```

---

### 1.2 Classes Principales

#### 1.2.1 Hiérarchie IEC 61850 (Existant + Extensions)

```turtle
# === Classes de base (inchangées) ===
iec:IED        a rdfs:Class ; rdfs:label "Intelligent Electronic Device" .
iec:LDevice    a rdfs:Class ; rdfs:label "Logical Device" .
iec:LN         a rdfs:Class ; rdfs:label "Logical Node" .
iec:DOI        a rdfs:Class ; rdfs:label "Data Object Instance" .
iec:SDI        a rdfs:Class ; rdfs:label "Sub Data Instance" .
iec:DAI        a rdfs:Class ; rdfs:label "Data Attribute Instance" .

# === DataTypeTemplates ===
iec:LNodeType  a rdfs:Class ; rdfs:label "Logical Node Type" .
iec:DOType     a rdfs:Class ; rdfs:label "Data Object Type" .
iec:DAType     a rdfs:Class ; rdfs:label "Data Attribute Type" .
iec:EnumType   a rdfs:Class ; rdfs:label "Enumeration Type" .
iec:EnumVal    a rdfs:Class ; rdfs:label "Enumeration Value" .
iec:DO         a rdfs:Class ; rdfs:label "Data Object (template)" .
iec:DA         a rdfs:Class ; rdfs:label "Data Attribute (template)" .
iec:BDA        a rdfs:Class ; rdfs:label "Basic Data Attribute" .

# === Communication ===
iec:SubNetwork   a rdfs:Class ; rdfs:label "SubNetwork" .
iec:ConnectedAP  a rdfs:Class ; rdfs:label "Connected Access Point" .
iec:Address      a rdfs:Class ; rdfs:label "Network Address" .
iec:P            a rdfs:Class ; rdfs:label "Address Parameter" .

# === Datasets & Control Blocks ===
iec:DataSet              a rdfs:Class ; rdfs:label "DataSet" .
iec:FCDA                 a rdfs:Class ; rdfs:label "Functional Constraint Data Attribute" .
iec:GSEControl           a rdfs:Class ; rdfs:label "GOOSE Control Block" .
iec:SampledValueControl  a rdfs:Class ; rdfs:label "Sampled Values Control Block" .
iec:ReportControl        a rdfs:Class ; rdfs:label "Report Control Block" .

# === Inputs ===
iec:Inputs     a rdfs:Class ; rdfs:label "Inputs Container" .
iec:ExtRef     a rdfs:Class ; rdfs:label "External Reference" .
iec:Private    a rdfs:Class ; rdfs:label "Private Vendor Data" .
```

#### 1.2.2 Classes de Versioning et Conformité

```turtle
# === Versioning ===
iec:Version           a rdfs:Class ; rdfs:label "Version d'un élément" ;
    rdfs:comment "Représente une version spécifique d'un élément (V0, V0.1, V1.0, etc.)" .

iec:VersionedElement  a rdfs:Class ; rdfs:label "Élément versionné" ;
    rdfs:comment "Classe abstraite pour tous les éléments versionnés" .

# === Standard IEC 61850 ===
std:StandardEdition   a rdfs:Class ; rdfs:label "Édition du standard IEC 61850" ;
    rdfs:comment "IEC 61850-7-4 Edition 1, 2, 2.1, etc." .

std:CDC               a rdfs:Class ; rdfs:label "Common Data Class" ;
    rdfs:comment "CDC définies dans une édition du standard (SPS, DPS, MV, etc.)" .

std:LNClass           a rdfs:Class ; rdfs:label "Logical Node Class" ;
    rdfs:comment "Classes LN définies dans le standard (XCBR, MMXU, GAPC, etc.)" .

# === Profils ===
profile:Profile        a rdfs:Class ; rdfs:label "Profil de conformité" ;
    rdfs:comment "Profil utilisateur (RTE, constructeur, etc.)" .

profile:ProfileVersion a rdfs:Class ; rdfs:label "Version d'un profil" ;
    rdfs:comment "Version spécifique d'un profil (RTE_2017, RTE_2020, etc.)" .

profile:Conformance    a rdfs:Class ; rdfs:label "Déclaration de conformité" ;
    rdfs:comment "Lien entre un élément et une version de profil" .

profile:Requirement    a rdfs:Class ; rdfs:label "Exigence du profil" ;
    rdfs:comment "Définit si un élément est M/O/C dans un profil" .

# === Configuration Figée ===
iec:Configuration     a rdfs:Class ; rdfs:label "Configuration SCD figée" ;
    rdfs:comment "Snapshot d'une configuration complète à un instant donné" .
```

---

### 1.3 Propriétés de Versioning

```turtle
# === Version de l'élément ===
scln:elementVersion      a rdf:Property ; rdfs:label "Version de l'élément" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range xsd:string ;
    rdfs:comment "Version sémantique : V0, V0.1, V1.0, V2.0, etc." .

scln:versionDate         a rdf:Property ; rdfs:label "Date de version" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range xsd:dateTime .

scln:versionAuthor       a rdf:Property ; rdfs:label "Auteur de la version" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range xsd:string .

scln:versionComment      a rdf:Property ; rdfs:label "Commentaire de version" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range xsd:string .

scln:previousVersion     a rdf:Property ; rdfs:label "Version précédente" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range iec:VersionedElement ;
    rdfs:comment "Lien vers la version antérieure de cet élément" .

scln:isLatestVersion     a rdf:Property ; rdfs:label "Dernière version" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range xsd:boolean ;
    rdfs:comment "true si c'est la version actuelle" .

scln:isDeprecated        a rdf:Property ; rdfs:label "Version obsolète" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range xsd:boolean .

# === Édition du standard ===
scln:standardEdition     a rdf:Property ; rdfs:label "Édition du standard IEC 61850" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range std:StandardEdition .

scln:editionName         a rdf:Property ; rdfs:label "Nom de l'édition" ;
    rdfs:domain std:StandardEdition ;
    rdfs:range xsd:string ;
    rdfs:comment "Ex: 'IEC 61850-7-4 Edition 2.1'" .

scln:editionYear         a rdf:Property ; rdfs:label "Année de l'édition" ;
    rdfs:domain std:StandardEdition ;
    rdfs:range xsd:integer .

# === Version du profil ===
scln:conformsTo          a rdf:Property ; rdfs:label "Conforme au profil" ;
    rdfs:domain iec:VersionedElement ;
    rdfs:range profile:ProfileVersion .

scln:profileName         a rdf:Property ; rdfs:label "Nom du profil" ;
    rdfs:domain profile:Profile ;
    rdfs:range xsd:string ;
    rdfs:comment "Ex: 'RTE', 'SIEMENS_SIPROTEC5', 'IEC61850-90-5'" .

scln:profileVersion      a rdf:Property ; rdfs:label "Version du profil" ;
    rdfs:domain profile:ProfileVersion ;
    rdfs:range xsd:string ;
    rdfs:comment "Ex: '2017', '2020-draft', 'V3.2'" .

scln:profileEditionDate  a rdf:Property ; rdfs:label "Date d'édition du profil" ;
    rdfs:domain profile:ProfileVersion ;
    rdfs:range xsd:date .

scln:profileOf           a rdf:Property ; rdfs:label "Profil parent" ;
    rdfs:domain profile:ProfileVersion ;
    rdfs:range profile:Profile .

scln:extendsProfile      a rdf:Property ; rdfs:label "Étend le profil" ;
    rdfs:domain profile:ProfileVersion ;
    rdfs:range profile:ProfileVersion ;
    rdfs:comment "Profil héritant d'un autre profil" .

# === Exigences du profil ===
scln:hasRequirement      a rdf:Property ; rdfs:label "A comme exigence" ;
    rdfs:domain profile:ProfileVersion ;
    rdfs:range profile:Requirement .

scln:requirementTarget   a rdf:Property ; rdfs:label "Cible de l'exigence" ;
    rdfs:domain profile:Requirement ;
    rdfs:range rdfs:Resource ;
    rdfs:comment "LN, DO, DA concerné par l'exigence" .

scln:requirementType     a rdf:Property ; rdfs:label "Type d'exigence" ;
    rdfs:domain profile:Requirement ;
    rdfs:range xsd:string ;
    rdfs:comment "M (Mandatory), O (Optional), C (Conditional), F (Forbidden)" .

scln:requirementCondition a rdf:Property ; rdfs:label "Condition" ;
    rdfs:domain profile:Requirement ;
    rdfs:range xsd:string ;
    rdfs:comment "Condition pour type 'C'" .

# === Configuration figée ===
scln:configurationVersion a rdf:Property ; rdfs:label "Version de configuration" ;
    rdfs:domain iec:Configuration ;
    rdfs:range xsd:string .

scln:frozenAt            a rdf:Property ; rdfs:label "Date de gel" ;
    rdfs:domain iec:Configuration ;
    rdfs:range xsd:dateTime .

scln:includesElement     a rdf:Property ; rdfs:label "Inclut l'élément" ;
    rdfs:domain iec:Configuration ;
    rdfs:range iec:VersionedElement .
```

---

### 1.4 Propriétés Existantes (Inchangées)

```turtle
# Relations hiérarchiques
scln:hasChild    a rdf:Property ; rdfs:label "A comme enfant" .

# Attributs de base
scln:name        a rdf:Property ; rdfs:label "Nom" .
scln:inst        a rdf:Property ; rdfs:label "Instance" .
scln:desc        a rdf:Property ; rdfs:label "Description" .
scln:id          a rdf:Property ; rdfs:label "Identifiant" .

# Logical Node
scln:lnClass     a rdf:Property ; rdfs:label "Classe LN" .
scln:lnType      a rdf:Property ; rdfs:label "Type LN" .
scln:prefix      a rdf:Property ; rdfs:label "Préfixe LN" .

# DataTypeTemplates
scln:typeRef     a rdf:Property ; rdfs:label "Référence de type" .
scln:bType       a rdf:Property ; rdfs:label "Type de base" .
scln:fc          a rdf:Property ; rdfs:label "Functional Constraint" .
scln:cdc         a rdf:Property ; rdfs:label "Common Data Class" .

# Data Attributes
scln:path        a rdf:Property ; rdfs:label "Chemin complet" .
scln:val         a rdf:Property ; rdfs:label "Valeur" .

# Communication
scln:type        a rdf:Property ; rdfs:label "Type" .
scln:text        a rdf:Property ; rdfs:label "Texte" .
scln:iedName     a rdf:Property ; rdfs:label "Nom IED" .
scln:apName      a rdf:Property ; rdfs:label "Nom Access Point" .

# ExtRef
scln:serviceType  a rdf:Property ; rdfs:label "Type de service" .
scln:cbName       a rdf:Property ; rdfs:label "Nom Control Block" .
scln:srcCBName    a rdf:Property ; rdfs:label "Source CB Name" .
scln:srcLDInst    a rdf:Property ; rdfs:label "Source LD Instance" .
scln:srcLNClass   a rdf:Property ; rdfs:label "Source LN Class" .
scln:srcLNInst    a rdf:Property ; rdfs:label "Source LN Instance" .
scln:srcPrefix    a rdf:Property ; rdfs:label "Source Prefix" .
scln:ldInst       a rdf:Property ; rdfs:label "LD Instance" .
scln:lnClassRef   a rdf:Property ; rdfs:label "LN Class Ref" .
scln:lnInst       a rdf:Property ; rdfs:label "LN Instance" .
scln:doName       a rdf:Property ; rdfs:label "DO Name" .
scln:daName       a rdf:Property ; rdfs:label "DA Name" .

# Control Blocks
scln:datSet      a rdf:Property ; rdfs:label "DataSet" .
scln:appID       a rdf:Property ; rdfs:label "Application ID" .

# Private
scln:xmlContent  a rdf:Property ; rdfs:label "Contenu XML" .

# Ordre
scln:order       a rdf:Property ; rdfs:label "Ordre" .
```

---

## 2. Exemples d'Instances

### 2.1 Standard Editions

```turtle
# Éditions du standard IEC 61850
<https://rtei.example.org/standard/IEC61850-7-4-Ed1> a std:StandardEdition ;
    scln:editionName "IEC 61850-7-4 Edition 1" ;
    scln:editionYear 2003 .

<https://rtei.example.org/standard/IEC61850-7-4-Ed2> a std:StandardEdition ;
    scln:editionName "IEC 61850-7-4 Edition 2" ;
    scln:editionYear 2010 .

<https://rtei.example.org/standard/IEC61850-7-4-Ed2.1> a std:StandardEdition ;
    scln:editionName "IEC 61850-7-4 Edition 2.1" ;
    scln:editionYear 2018 .
```

### 2.2 Profils et Versions

```turtle
# Profil RTE
<https://rtei.example.org/profile/RTE> a profile:Profile ;
    scln:profileName "RTE" ;
    scln:desc "Profil RTE pour postes électriques HTA/HTB" .

# Version 2017 du profil RTE
<https://rtei.example.org/profile/RTE/2017> a profile:ProfileVersion ;
    scln:profileOf <https://rtei.example.org/profile/RTE> ;
    scln:profileVersion "2017" ;
    scln:profileEditionDate "2017-03-15"^^xsd:date ;
    scln:desc "Profil RTE 2017 - version initiale" .

# Version 2020 du profil RTE
<https://rtei.example.org/profile/RTE/2020> a profile:ProfileVersion ;
    scln:profileOf <https://rtei.example.org/profile/RTE> ;
    scln:profileVersion "2020" ;
    scln:profileEditionDate "2020-09-01"^^xsd:date ;
    scln:desc "Profil RTE 2020 - ajout support Edition 2.1" ;
    scln:extendsProfile <https://rtei.example.org/profile/RTE/2017> .

# Profil constructeur Siemens
<https://rtei.example.org/profile/SIEMENS/SIPROTEC5/V3.2> a profile:ProfileVersion ;
    scln:profileOf <https://rtei.example.org/profile/SIEMENS/SIPROTEC5> ;
    scln:profileVersion "V3.2" ;
    scln:profileEditionDate "2021-06-10"^^xsd:date .
```

### 2.3 IED avec Versioning Complet

```turtle
# IED Version V0 (version initiale)
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0> a iec:IED, iec:VersionedElement ;
    scln:name "POSTE0TGAUT1" ;
    scln:desc "Automate de poste - version initiale" ;

    # Versioning atomique
    scln:elementVersion "V0" ;
    scln:versionDate "2023-01-15T10:30:00Z"^^xsd:dateTime ;
    scln:versionAuthor "Jean Dupont" ;
    scln:versionComment "Configuration initiale après commissioning" ;
    scln:isLatestVersion false ;

    # Standard et profil
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2> ;
    scln:conformsTo <https://rtei.example.org/profile/RTE/2017> .

# IED Version V0.1 (correction mineure)
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0.1> a iec:IED, iec:VersionedElement ;
    scln:name "POSTE0TGAUT1" ;
    scln:desc "Automate de poste - correction adresse IP" ;

    # Versioning atomique
    scln:elementVersion "V0.1" ;
    scln:versionDate "2023-02-20T14:15:00Z"^^xsd:dateTime ;
    scln:versionAuthor "Marie Martin" ;
    scln:versionComment "Correction adresse IP suite incident réseau" ;
    scln:previousVersion <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0> ;
    scln:isLatestVersion false ;

    # Standard et profil (inchangés)
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2> ;
    scln:conformsTo <https://rtei.example.org/profile/RTE/2017> .

# IED Version V1.0 (migration profil 2020)
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0> a iec:IED, iec:VersionedElement ;
    scln:name "POSTE0TGAUT1" ;
    scln:desc "Automate de poste - migration profil RTE 2020" ;

    # Versioning atomique
    scln:elementVersion "V1.0" ;
    scln:versionDate "2024-05-10T09:00:00Z"^^xsd:dateTime ;
    scln:versionAuthor "Pierre Durand" ;
    scln:versionComment "Migration vers profil RTE 2020 + Edition 2.1" ;
    scln:previousVersion <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0.1> ;
    scln:isLatestVersion true ;

    # Standard et profil (mis à jour)
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2.1> ;
    scln:conformsTo <https://rtei.example.org/profile/RTE/2020> .
```

### 2.4 LDevice avec Versioning

```turtle
# LDevice V0
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0> a iec:LDevice, iec:VersionedElement ;
    scln:inst "LDAGSA1" ;
    scln:elementVersion "V0" ;
    scln:versionDate "2024-05-10T09:00:00Z"^^xsd:dateTime ;
    scln:isLatestVersion true ;
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2.1> ;
    scln:conformsTo <https://rtei.example.org/profile/RTE/2020> .

# Lien hiérarchique
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0> scln:hasChild
    <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0> .
```

### 2.5 Logical Node avec Versioning

```turtle
# LN XCBR Version V0
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0>
    a iec:LN, iec:VersionedElement ;
    scln:lnClass "XCBR" ;
    scln:inst "1" ;
    scln:lnType "XCBR1" ;
    scln:prefix "Q0" ;

    # Versioning
    scln:elementVersion "V0" ;
    scln:versionDate "2024-05-10T09:00:00Z"^^xsd:dateTime ;
    scln:isLatestVersion false ;

    # Standard et profil
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2.1> ;
    scln:conformsTo <https://rtei.example.org/profile/RTE/2020> .

# LN XCBR Version V0.1 (ajout d'un ExtRef)
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0.1>
    a iec:LN, iec:VersionedElement ;
    scln:lnClass "XCBR" ;
    scln:inst "1" ;
    scln:lnType "XCBR1" ;
    scln:prefix "Q0" ;

    # Versioning
    scln:elementVersion "V0.1" ;
    scln:versionDate "2024-06-01T11:30:00Z"^^xsd:dateTime ;
    scln:versionComment "Ajout abonnement GOOSE pour verrouillage" ;
    scln:previousVersion <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0> ;
    scln:isLatestVersion true ;

    # Standard et profil (inchangés)
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2.1> ;
    scln:conformsTo <https://rtei.example.org/profile/RTE/2020> .
```

### 2.6 LNodeType avec Standard Edition

```turtle
# LNodeType XCBR (Edition 2)
<https://rtei.example.org/scl/SCD/DTT/LNodeType/XCBR1/V0> a iec:LNodeType, iec:VersionedElement ;
    scln:id "XCBR1" ;
    scln:lnClass "XCBR" ;

    # Versioning
    scln:elementVersion "V0" ;
    scln:isLatestVersion true ;

    # Standard
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2> ;

    # Enfants (DO)
    scln:hasChild <https://rtei.example.org/scl/SCD/DTT/LNodeType/XCBR1/V0/DO/Pos> ,
                  <https://rtei.example.org/scl/SCD/DTT/LNodeType/XCBR1/V0/DO/BlkOpn> .

# DO Pos
<https://rtei.example.org/scl/SCD/DTT/LNodeType/XCBR1/V0/DO/Pos> a iec:DO, iec:VersionedElement ;
    scln:name "Pos" ;
    scln:typeRef "DPC1" ;
    scln:cdc "DPC" ;
    scln:elementVersion "V0" ;
    scln:isLatestVersion true ;
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2> .
```

### 2.7 Exigences de Profil

```turtle
# Exigence : DO "Pos" est Mandatory dans profil RTE 2020
<https://rtei.example.org/profile/RTE/2020/req/XCBR-Pos> a profile:Requirement ;
    scln:requirementTarget <https://rtei.example.org/scl/SCD/DTT/LNodeType/XCBR1/V0/DO/Pos> ;
    scln:requirementType "M" ;
    rdfs:comment "DO Pos est obligatoire dans XCBR selon RTE 2020" .

<https://rtei.example.org/profile/RTE/2020> scln:hasRequirement
    <https://rtei.example.org/profile/RTE/2020/req/XCBR-Pos> .

# Exigence : DA "origin" est Optional dans profil RTE 2020
<https://rtei.example.org/profile/RTE/2020/req/XCBR-origin> a profile:Requirement ;
    scln:requirementTarget <https://rtei.example.org/scl/SCD/DTT/DOType/DPC1/V0/DA/origin> ;
    scln:requirementType "O" ;
    rdfs:comment "DA origin est optionnel dans DPC selon RTE 2020" .

# Exigence : DA "pulseConfig" est Forbidden dans profil RTE 2017
<https://rtei.example.org/profile/RTE/2017/req/XCBR-pulseConfig> a profile:Requirement ;
    scln:requirementTarget <https://rtei.example.org/scl/SCD/DTT/DOType/DPC1/V0/DA/pulseConfig> ;
    scln:requirementType "F" ;
    rdfs:comment "DA pulseConfig interdit dans profil RTE 2017" .
```

### 2.8 Configuration Figée (Snapshot)

```turtle
# Configuration complète V1.0 du SCD
<https://rtei.example.org/config/SCD_POSTE0_V1.0> a iec:Configuration ;
    scln:configurationVersion "V1.0" ;
    scln:frozenAt "2024-06-15T16:00:00Z"^^xsd:dateTime ;
    scln:desc "Configuration SCD POSTE0 - Version 1.0 validée pour production" ;

    # Inclut tous les éléments figés
    scln:includesElement <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0> ;
    scln:includesElement <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0> ;
    scln:includesElement <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0.1> ;
    # ... tous les autres éléments

    # Standard et profil de la configuration globale
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2.1> ;
    scln:conformsTo <https://rtei.example.org/profile/RTE/2020> .
```

---

## 3. Schéma URI avec Versioning

### 3.1 Principe

Chaque élément versionné a une URI contenant sa version :

```
https://rtei.example.org/scl/
  ├─ SCD/IED/<iedName>/<version>/
  │   ├─ LD/<ldInst>/<version>/
  │   │   └─ LN/<lnClass>_<lnInst>/<version>/
  │   │       ├─ DOI/<doName>/<version>
  │   │       └─ DAI/<path>/<version>
  ├─ SCD/DTT/LNodeType/<id>/<version>/
  │   └─ DO/<name>/<version>
  ├─ SCD/DTT/DOType/<id>/<version>/
  │   └─ DA/<name>/<version>
  └─ config/<configName>/<version>
```

### 3.2 Exemples

```turtle
# IED à différentes versions
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0>
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0.1>
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0>

# LN à différentes versions
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0>
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0.1>
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0.2>

# DAI à différentes versions
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0.1/DAI/Pos.stVal/V0>
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0.1/DAI/Pos.stVal/V1>
```

---

## 4. Requêtes SPARQL

### 4.1 Récupération de la Dernière Version d'un IED

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?ied ?version ?date ?author ?stdEdition ?profile
WHERE {
  ?ied a iec:IED ;
       scln:name "POSTE0TGAUT1" ;
       scln:elementVersion ?version ;
       scln:isLatestVersion true ;
       scln:versionDate ?date ;
       scln:versionAuthor ?author ;
       scln:standardEdition ?stdEdition ;
       scln:conformsTo ?profile .
}
```

### 4.2 Historique Complet d'un Élément

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?uri ?version ?date ?author ?comment
WHERE {
  ?uri a iec:IED ;
       scln:name "POSTE0TGAUT1" ;
       scln:elementVersion ?version ;
       scln:versionDate ?date ;
       scln:versionAuthor ?author .
  OPTIONAL { ?uri scln:versionComment ?comment }
}
ORDER BY ?date
```

### 4.3 Traçabilité des Versions (Chaîne Précédent)

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?current ?currentVersion ?previous ?previousVersion
WHERE {
  ?current a iec:LN ;
           scln:lnClass "XCBR" ;
           scln:inst "1" ;
           scln:elementVersion ?currentVersion ;
           scln:previousVersion ?previous .
  ?previous scln:elementVersion ?previousVersion .
}
ORDER BY DESC(?currentVersion)
```

### 4.4 Récupération d'une Configuration Figée

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?element ?type ?version ?name
WHERE {
  <https://rtei.example.org/config/SCD_POSTE0_V1.0>
    scln:includesElement ?element .

  ?element a ?type ;
           scln:elementVersion ?version .

  OPTIONAL { ?element scln:name ?name }
}
ORDER BY ?type ?name
```

### 4.5 Lister tous les Éléments conformes à un Profil Spécifique

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>
PREFIX profile: <https://rtei.example.org/profile#>

SELECT ?element ?type ?version
WHERE {
  ?element a iec:VersionedElement ;
           a ?type ;
           scln:elementVersion ?version ;
           scln:conformsTo <https://rtei.example.org/profile/RTE/2020> .

  FILTER(?type != iec:VersionedElement)
}
ORDER BY ?type ?element
```

### 4.6 Lister tous les Éléments basés sur une Édition du Standard

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>
PREFIX std: <https://rtei.example.org/standard#>

SELECT ?element ?type ?version ?stdName
WHERE {
  ?element a iec:VersionedElement ;
           a ?type ;
           scln:elementVersion ?version ;
           scln:standardEdition ?std .

  ?std scln:editionName ?stdName .

  FILTER(?std = <https://rtei.example.org/standard/IEC61850-7-4-Ed2.1>)
  FILTER(?type != iec:VersionedElement)
}
ORDER BY ?type
```

### 4.7 Vérifier la Conformité au Profil

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>
PREFIX profile: <https://rtei.example.org/profile#>

# Trouver les DO manquants (M dans profil mais absents)
SELECT ?lnType ?requiredDO ?reqType
WHERE {
  # LNodeType utilisé
  ?ln a iec:LN ;
      scln:lnType ?lnTypeId .

  ?lnType a iec:LNodeType ;
          scln:id ?lnTypeId ;
          scln:conformsTo ?profile .

  # Exigence du profil
  ?profile scln:hasRequirement ?req .
  ?req scln:requirementTarget ?requiredDO ;
       scln:requirementType "M" .

  # Le DO doit exister
  FILTER NOT EXISTS {
    ?lnType scln:hasChild ?requiredDO .
  }
}
```

### 4.8 Comparaison entre Deux Versions

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?property ?oldValue ?newValue
WHERE {
  # Version ancienne
  <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0>
    ?property ?oldValue .

  # Version nouvelle
  <https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0>
    ?property ?newValue .

  FILTER(?oldValue != ?newValue)
  FILTER(?property NOT IN (scln:elementVersion, scln:versionDate, scln:versionAuthor, scln:versionComment, scln:previousVersion, scln:isLatestVersion))
}
```

### 4.9 Audit : Qui a Modifié Quoi et Quand

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?element ?type ?version ?date ?author ?comment
WHERE {
  ?element a iec:VersionedElement ;
           a ?type ;
           scln:elementVersion ?version ;
           scln:versionDate ?date ;
           scln:versionAuthor ?author .

  OPTIONAL { ?element scln:versionComment ?comment }

  FILTER(?type != iec:VersionedElement)
  FILTER(?date >= "2024-01-01T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "2024-12-31T23:59:59Z"^^xsd:dateTime)
}
ORDER BY DESC(?date)
```

### 4.10 Exporter Tous les Éléments d'un SCD à une Version Donnée

```sparql
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

CONSTRUCT {
  ?element ?p ?o .
}
WHERE {
  # Configuration figée
  <https://rtei.example.org/config/SCD_POSTE0_V1.0>
    scln:includesElement ?element .

  # Toutes les propriétés de l'élément
  ?element ?p ?o .
}
```

---

## 5. Cas d'Usage

### 5.1 Création d'une Nouvelle Version d'un LN

**Scénario** : Ajout d'un abonnement GOOSE (ExtRef) au LN XCBR_1

```turtle
# 1. Créer la nouvelle version V0.2
<https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.0/LD/LDAGSA1/V0/LN/XCBR_1/V0.2>
    a iec:LN, iec:VersionedElement ;
    scln:lnClass "XCBR" ;
    scln:inst "1" ;
    scln:lnType "XCBR1" ;
    scln:prefix "Q0" ;

    # Versioning
    scln:elementVersion "V0.2" ;
    scln:versionDate "2024-07-10T08:45:00Z"^^xsd:dateTime ;
    scln:versionAuthor "Sophie Bernard" ;
    scln:versionComment "Ajout ExtRef pour télécommande depuis SCADA" ;
    scln:previousVersion <.../XCBR_1/V0.1> ;
    scln:isLatestVersion true ;

    # Standard et profil (inchangés)
    scln:standardEdition <https://rtei.example.org/standard/IEC61850-7-4-Ed2.1> ;
    scln:conformsTo <https://rtei.example.org/profile/RTE/2020> ;

    # Nouvel ExtRef
    scln:hasChild <.../XCBR_1/V0.2/Inputs/ExtRef/SCADA_CMD> .

# 2. Marquer l'ancienne version comme non-latest
# (UPDATE SPARQL)
DELETE { <.../XCBR_1/V0.1> scln:isLatestVersion true }
INSERT { <.../XCBR_1/V0.1> scln:isLatestVersion false }
WHERE { <.../XCBR_1/V0.1> scln:isLatestVersion true }
```

### 5.2 Migration de Profil (RTE 2017 → RTE 2020)

```sparql
# UPDATE pour migrer un IED
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

DELETE {
  ?ied scln:conformsTo <https://rtei.example.org/profile/RTE/2017>
}
INSERT {
  ?ied scln:conformsTo <https://rtei.example.org/profile/RTE/2020> ;
       scln:elementVersion "V1.0" ;
       scln:versionDate "2024-08-01T10:00:00Z"^^xsd:dateTime ;
       scln:versionAuthor "Admin Migration" ;
       scln:versionComment "Migration vers profil RTE 2020"
}
WHERE {
  ?ied a iec:IED ;
       scln:name "POSTE0TGAUT1" ;
       scln:conformsTo <https://rtei.example.org/profile/RTE/2017> .
}
```

### 5.3 Gel d'une Configuration (Snapshot)

**Scénario** : Figer la configuration SCD avant mise en production

```python
from rdflib import Graph, Namespace, Literal, URIRef
from datetime import datetime

IEC = Namespace("https://rtei.example.org/iec61850#")
SCLN = Namespace("https://rtei.example.org/scl#")

g = Graph()
g.parse("SCD_POSTE0.ttl", format="turtle")

# Créer la configuration figée
config_uri = URIRef("https://rtei.example.org/config/SCD_POSTE0_V1.0")
g.add((config_uri, RDF.type, IEC.Configuration))
g.add((config_uri, SCLN.configurationVersion, Literal("V1.0")))
g.add((config_uri, SCLN.frozenAt, Literal(datetime.now())))
g.add((config_uri, SCLN.desc, Literal("Configuration validée pour production")))

# Récupérer tous les éléments avec isLatestVersion=true
query = """
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

SELECT ?element WHERE {
  ?element a iec:VersionedElement ;
           scln:isLatestVersion true .
}
"""

for row in g.query(query):
    g.add((config_uri, SCLN.includesElement, row.element))

g.serialize("SCD_POSTE0_frozen_V1.0.ttl", format="turtle")
```

### 5.4 Restauration d'une Version Antérieure

```sparql
# Récupérer la version V0.1 d'un LN et la remettre comme latest
PREFIX iec: <https://rtei.example.org/iec61850#>
PREFIX scln: <https://rtei.example.org/scl#>

DELETE {
  ?current scln:isLatestVersion true
}
INSERT {
  <.../LN/XCBR_1/V0.1> scln:isLatestVersion true
}
WHERE {
  ?current a iec:LN ;
           scln:lnClass "XCBR" ;
           scln:inst "1" ;
           scln:isLatestVersion true .
}
```

---

## 6. Extensions Python pour Versioning

### 6.1 Classe Helper pour Gestion des Versions

```python
from rdflib import Graph, Namespace, Literal, URIRef, RDF, XSD
from datetime import datetime
from typing import Optional

IEC = Namespace("https://rtei.example.org/iec61850#")
SCLN = Namespace("https://rtei.example.org/scl#")

class VersionManager:
    def __init__(self, graph: Graph):
        self.g = graph

    def create_version(
        self,
        element_uri: URIRef,
        element_type: URIRef,
        version: str,
        author: str,
        comment: str = "",
        previous_version: Optional[URIRef] = None,
        standard_edition: Optional[URIRef] = None,
        profile_version: Optional[URIRef] = None
    ) -> URIRef:
        """Crée une nouvelle version d'un élément"""

        # Marquer l'ancienne version comme non-latest si elle existe
        if previous_version:
            self.g.remove((previous_version, SCLN.isLatestVersion, None))
            self.g.add((previous_version, SCLN.isLatestVersion, Literal(False)))

        # Créer la nouvelle version
        self.g.add((element_uri, RDF.type, element_type))
        self.g.add((element_uri, RDF.type, IEC.VersionedElement))
        self.g.add((element_uri, SCLN.elementVersion, Literal(version)))
        self.g.add((element_uri, SCLN.versionDate, Literal(datetime.now(), datatype=XSD.dateTime)))
        self.g.add((element_uri, SCLN.versionAuthor, Literal(author)))
        self.g.add((element_uri, SCLN.isLatestVersion, Literal(True)))

        if comment:
            self.g.add((element_uri, SCLN.versionComment, Literal(comment)))

        if previous_version:
            self.g.add((element_uri, SCLN.previousVersion, previous_version))

        if standard_edition:
            self.g.add((element_uri, SCLN.standardEdition, standard_edition))

        if profile_version:
            self.g.add((element_uri, SCLN.conformsTo, profile_version))

        return element_uri

    def get_latest_version(self, element_name: str, element_type: URIRef) -> Optional[URIRef]:
        """Récupère la dernière version d'un élément par nom"""
        query = f"""
        PREFIX iec: <https://rtei.example.org/iec61850#>
        PREFIX scln: <https://rtei.example.org/scl#>

        SELECT ?uri WHERE {{
          ?uri a {element_type.n3()} ;
               scln:name "{element_name}" ;
               scln:isLatestVersion true .
        }}
        """
        results = list(self.g.query(query))
        return results[0][0] if results else None

    def get_version_history(self, latest_uri: URIRef) -> list:
        """Récupère tout l'historique des versions d'un élément"""
        history = []
        current = latest_uri

        while current:
            version = self.g.value(current, SCLN.elementVersion)
            date = self.g.value(current, SCLN.versionDate)
            author = self.g.value(current, SCLN.versionAuthor)
            comment = self.g.value(current, SCLN.versionComment)

            history.append({
                "uri": str(current),
                "version": str(version),
                "date": str(date),
                "author": str(author),
                "comment": str(comment) if comment else ""
            })

            current = self.g.value(current, SCLN.previousVersion)

        return history

    def freeze_configuration(
        self,
        config_name: str,
        config_version: str,
        description: str = ""
    ) -> URIRef:
        """Crée un snapshot de configuration figée"""

        config_uri = URIRef(f"https://rtei.example.org/config/{config_name}/{config_version}")

        self.g.add((config_uri, RDF.type, IEC.Configuration))
        self.g.add((config_uri, SCLN.configurationVersion, Literal(config_version)))
        self.g.add((config_uri, SCLN.frozenAt, Literal(datetime.now(), datatype=XSD.dateTime)))

        if description:
            self.g.add((config_uri, SCLN.desc, Literal(description)))

        # Récupérer tous les éléments avec isLatestVersion=true
        query = """
        PREFIX iec: <https://rtei.example.org/iec61850#>
        PREFIX scln: <https://rtei.example.org/scl#>

        SELECT ?element WHERE {
          ?element a iec:VersionedElement ;
                   scln:isLatestVersion true .
        }
        """

        for row in self.g.query(query):
            self.g.add((config_uri, SCLN.includesElement, row.element))

        return config_uri

# Exemple d'utilisation
g = Graph()
g.bind("iec", IEC)
g.bind("scln", SCLN)

vm = VersionManager(g)

# Créer un IED V0
ied_v0 = URIRef("https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0")
vm.create_version(
    element_uri=ied_v0,
    element_type=IEC.IED,
    version="V0",
    author="Jean Dupont",
    comment="Configuration initiale",
    standard_edition=URIRef("https://rtei.example.org/standard/IEC61850-7-4-Ed2"),
    profile_version=URIRef("https://rtei.example.org/profile/RTE/2017")
)

g.add((ied_v0, SCLN.name, Literal("POSTE0TGAUT1")))

# Créer une nouvelle version V0.1
ied_v01 = URIRef("https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V0.1")
vm.create_version(
    element_uri=ied_v01,
    element_type=IEC.IED,
    version="V0.1",
    author="Marie Martin",
    comment="Correction adresse IP",
    previous_version=ied_v0,
    standard_edition=URIRef("https://rtei.example.org/standard/IEC61850-7-4-Ed2"),
    profile_version=URIRef("https://rtei.example.org/profile/RTE/2017")
)

g.add((ied_v01, SCLN.name, Literal("POSTE0TGAUT1")))

# Récupérer l'historique
history = vm.get_version_history(ied_v01)
for h in history:
    print(f"{h['version']} - {h['date']} - {h['author']}: {h['comment']}")

# Figer la configuration
config = vm.freeze_configuration(
    config_name="SCD_POSTE0",
    config_version="V1.0",
    description="Configuration validée pour production"
)

g.serialize("versioned_scd.ttl", format="turtle")
```

---

## 7. Intégration avec Apache Jena Fuseki

### 7.1 API REST pour Versioning

```javascript
// Client JavaScript pour gérer les versions via Fuseki
import SparqlClient from 'sparql-http-client';

const client = new SparqlClient({
  endpointUrl: 'http://localhost:3030/scd/sparql',
  updateUrl: 'http://localhost:3030/scd/update'
});

// Fonction : récupérer la dernière version d'un IED
async function getLatestIEDVersion(iedName) {
  const query = `
    PREFIX iec: <https://rtei.example.org/iec61850#>
    PREFIX scln: <https://rtei.example.org/scl#>

    SELECT ?uri ?version ?date ?author ?stdEdition ?profile
    WHERE {
      ?uri a iec:IED ;
           scln:name "${iedName}" ;
           scln:elementVersion ?version ;
           scln:isLatestVersion true ;
           scln:versionDate ?date ;
           scln:versionAuthor ?author ;
           scln:standardEdition ?stdEdition ;
           scln:conformsTo ?profile .
    }
  `;

  const stream = client.query.select(query);
  const results = [];

  stream.on('data', row => {
    results.push({
      uri: row.uri.value,
      version: row.version.value,
      date: row.date.value,
      author: row.author.value,
      standardEdition: row.stdEdition.value,
      profile: row.profile.value
    });
  });

  return new Promise((resolve) => {
    stream.on('end', () => resolve(results[0]));
  });
}

// Fonction : créer une nouvelle version
async function createNewVersion(
  oldUri,
  newUri,
  newVersion,
  author,
  comment,
  standardEdition,
  profileVersion
) {
  const update = `
    PREFIX iec: <https://rtei.example.org/iec61850#>
    PREFIX scln: <https://rtei.example.org/scl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE { <${oldUri}> scln:isLatestVersion true }
    INSERT { <${oldUri}> scln:isLatestVersion false }
    WHERE { <${oldUri}> scln:isLatestVersion true } ;

    INSERT DATA {
      <${newUri}> a iec:IED, iec:VersionedElement ;
                  scln:elementVersion "${newVersion}" ;
                  scln:versionDate "${new Date().toISOString()}"^^xsd:dateTime ;
                  scln:versionAuthor "${author}" ;
                  scln:versionComment "${comment}" ;
                  scln:previousVersion <${oldUri}> ;
                  scln:isLatestVersion true ;
                  scln:standardEdition <${standardEdition}> ;
                  scln:conformsTo <${profileVersion}> .
    }
  `;

  await client.query.update(update);
}

// Utilisation
const latestIED = await getLatestIEDVersion("POSTE0TGAUT1");
console.log(`Latest version: ${latestIED.version} by ${latestIED.author}`);

await createNewVersion(
  latestIED.uri,
  "https://rtei.example.org/scl/SCD/IED/POSTE0TGAUT1/V1.1",
  "V1.1",
  "Sophie Bernard",
  "Ajout LN protection distance",
  "https://rtei.example.org/standard/IEC61850-7-4-Ed2.1",
  "https://rtei.example.org/profile/RTE/2020"
);
```

---

## 8. Résumé

### 8.1 Ce que cette ontologie permet

✅ **Versioning atomique** : chaque IED, LD, LN, DO, DA, DAI, DOI, etc. a sa propre version
✅ **Traçabilité complète** : auteur, date, commentaire pour chaque version
✅ **Historique** : chaîne de `previousVersion` pour remonter dans le temps
✅ **Standard IEC 61850** : lien explicite vers Edition 1/2/2.1
✅ **Profils** : conformité à des profils (RTE, constructeur, etc.) avec versioning
✅ **Exigences** : définition M/O/C/F pour chaque élément dans un profil
✅ **Configuration figée** : snapshot complet de toutes les versions à un instant T
✅ **Requêtes** : récupération facile de la dernière version, historique, comparaison
✅ **Migration** : traçabilité des migrations de profil ou d'édition de standard

### 8.2 Schéma des 3 Dimensions

```
┌─────────────────────────────────────────────┐
│         Élément IEC 61850 (IED)            │
├─────────────────────────────────────────────┤
│                                             │
│  [1] Version Élément : V0 → V0.1 → V1.0    │
│       ├─ Date, Auteur, Commentaire         │
│       └─ previousVersion (chaîne)          │
│                                             │
│  [2] Standard IEC 61850 : Ed1 / Ed2 / Ed2.1│
│       └─ Année, Nom officiel               │
│                                             │
│  [3] Profil : RTE_2017 / RTE_2020          │
│       ├─ Version, Date édition             │
│       ├─ Exigences (M/O/C/F)               │
│       └─ Héritage (extendsProfile)         │
│                                             │
└─────────────────────────────────────────────┘
```

### 8.3 Workflow Typique

1. **Création** : créer un IED/LN/DA en version V0 avec standard + profil
2. **Modification** : créer une nouvelle version (V0.1, V1.0, etc.) avec lien `previousVersion`
3. **Migration** : changer `standardEdition` et/ou `conformsTo` lors de mise à jour
4. **Gel** : créer une `Configuration` qui référence toutes les versions actuelles
5. **Audit** : requêter l'historique des modifications (qui, quand, quoi)
6. **Restauration** : remettre `isLatestVersion=true` sur une version antérieure

---

**Auteur** : Guide de formation - Projet MOOC Web Development
**Dernière mise à jour** : 2025-10-08
