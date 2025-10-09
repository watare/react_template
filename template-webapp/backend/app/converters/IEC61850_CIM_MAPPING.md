# Convertisseur bidirectionnel IEC 61850 ↔ CIM

## Objectif

Créer un convertisseur bidirectionnel entre :
- **IEC 61850 SCL** (Substation Configuration Language) - Standard des postes électriques
- **CIM/CGMES** (Common Information Model) - Standard des réseaux de transport

## Standards de référence

| Standard | Description | Utilisation |
|----------|-------------|-------------|
| **IEC 61850-6** | SCL (Substation Configuration Language) | Configuration des postes |
| **IEC 61970-301** | CIM (Common Information Model) | Modélisation des réseaux |
| **IEC 61970-453** | CIM Diagram Layout | Layout des schémas |
| **IEC 62361-102** | Harmonisation IEC 61850 / CIM | Mapping entre les deux |
| **CGMES** | Common Grid Model Exchange Specification | Profil CIM pour TSO européens |

## Vue d'ensemble de l'architecture

```
┌─────────────────┐                    ┌─────────────────┐
│   IEC 61850     │    Converter       │      CIM        │
│   SCL (XML)     │ ←──────────────→   │   (XML/RDF)     │
│                 │                    │                 │
│ - Substation    │                    │ - Substation    │
│ - VoltageLevel  │                    │ - VoltageLevel  │
│ - Bay           │                    │ - Bay           │
│ - Equipment     │                    │ - Equipment     │
│ - LNode         │                    │ - Terminal      │
│ - ConnNode      │                    │ - ConnNode      │
└─────────────────┘                    └─────────────────┘
         │                                      │
         │                                      │
         └───────────> RDF Triplestore <────────┘
                       (Apache Jena Fuseki)
```

## Mapping des concepts clés

### 1. Structure hiérarchique

| IEC 61850 (SCL) | CIM/CGMES | Notes |
|-----------------|-----------|-------|
| `SCL` | `Model` | Document racine |
| `Substation` | `Substation` | ✅ Mapping direct |
| `VoltageLevel` | `VoltageLevel` | ✅ Mapping direct |
| `Bay` | `Bay` | ✅ Mapping direct |

### 2. Équipements (ConductingEquipment)

| IEC 61850 Type | CIM Class | Description |
|----------------|-----------|-------------|
| `CBR` | `Breaker` | Disjoncteur |
| `DIS` | `Disconnector` ou `LoadBreakSwitch` | Sectionneur (selon type) |
| `CTR` | `CurrentTransformer` | Transformateur de courant |
| `VTR` | `PotentialTransformer` | Transformateur de tension |
| `PTR` | `PowerTransformer` | Transformateur de puissance |
| `CAP` | `LinearShuntCompensator` | Condensateur |
| `REA` | `LinearShuntCompensator` | Réactance |
| `BAT` | `BatteryUnit` | Batterie |
| `GEN` | `GeneratingUnit` | Générateur |
| `MOT` | `SynchronousMachine` | Moteur |

### 3. Sous-types de sectionneurs (RTE)

| IEC 61850 Subtype | CIM | Description |
|-------------------|-----|-------------|
| `DIS` (SA) | `Disconnector` | Sectionneur d'aiguillage |
| `DIS` (SL) | `Disconnector` | Sectionneur de ligne |
| `DIS` (ST) | `GroundDisconnector` | Sectionneur de terre |
| `DIS` (SS) | `Disconnector` | Sectionneur de sectionnement |

### 4. Connectivité

| IEC 61850 | CIM | Mapping |
|-----------|-----|---------|
| `Terminal` (élément) | `Terminal` (classe) | Point de connexion d'un équipement |
| `connectivityNode` (attribut) | `ConnectivityNode` (classe) | Nœud de connexion électrique |
| `ConnectivityNode` (élément) | `ConnectivityNode` (classe) | ✅ Mapping direct |

### 5. Logical Nodes → Measurements/Controls

| IEC 61850 | CIM | Mapping |
|-----------|-----|---------|
| `LNode` | `Measurement` ou `Control` | Selon le type de LN |
| `MMXU` (mesure) | `Analog` | Mesures analogiques |
| `CSWI` (commande) | `Control` | Commandes |
| `XCBR` (disjoncteur) | `Discrete` | États discrets |

## Défis du mapping

### 1. Approches différentes

**IEC 61850** :
- Approche **fonctionnelle** (Logical Nodes)
- Focus sur la **communication** et l'**automatisation**
- Représentation détaillée de l'**information temps réel**

**CIM** :
- Approche **topologique** (équipements physiques)
- Focus sur la **modélisation du réseau**
- Représentation **statique** de l'infrastructure

### 2. Informations manquantes

**IEC 61850 → CIM** :
- ❌ Paramètres électriques (impédances, ratings)
- ❌ Informations géographiques (GPS)
- ❌ Relations entre postes (lignes réseau)
- ✅ Topologie interne du poste
- ✅ Équipements et connexions

**CIM → IEC 61850** :
- ❌ Configuration des IEDs
- ❌ Logical Nodes détaillés
- ❌ DataSets, ReportControls
- ✅ Topologie du poste
- ✅ Équipements principaux

### 3. Informations RTE propriétaires

**COMPAS-Topo** (RTE) :
- `Node` : Numéro de jeu de barres
- `NodeOrder` : Ordre horizontal
- `Direction` : Up/Down
- `BusBarSectionOrder` : Ordre des JdB

**Mapping CIM** :
- Stocker dans `IdentifiedObject.description` ?
- Utiliser des `Properties` customs ?
- Créer un profil CIM étendu ?

## Architecture du convertisseur

```python
# backend/app/converters/
converters/
├── __init__.py
├── base_converter.py           # Classe abstraite
├── iec61850_to_cim.py         # IEC 61850 → CIM
├── cim_to_iec61850.py         # CIM → IEC 61850
├── mapping_rules.py           # Tables de mapping
└── validators.py              # Validation des conversions
```

### Classes principales

```python
class BaseConverter(ABC):
    """Classe abstraite pour les convertisseurs"""

    @abstractmethod
    def convert(self, input_data: Union[str, Graph]) -> Union[str, Graph]:
        """Convertit d'un format à l'autre"""
        pass

    @abstractmethod
    def validate(self, output_data: Union[str, Graph]) -> bool:
        """Valide la sortie"""
        pass


class IEC61850ToCIMConverter(BaseConverter):
    """
    Convertit IEC 61850 SCL → CIM/CGMES

    Input:  Fichier SCL (XML) ou Graph RDF (IEC 61850)
    Output: CIM CGMES (XML) ou Graph RDF (CIM)
    """

    def convert(self, scl_input: Union[str, Graph]) -> Graph:
        """
        Conversion IEC 61850 → CIM

        Étapes :
        1. Parser le SCL (si XML)
        2. Extraire la topologie (Substation, VoltageLevel, Bay)
        3. Mapper les équipements (CBR, DIS, etc.)
        4. Créer les ConnectivityNodes et Terminals
        5. Générer le graph CIM
        """
        cim_graph = Graph()

        # 1. Extraire les substations
        substations = self._extract_substations(scl_input)

        for substation in substations:
            # 2. Mapper vers CIM
            cim_substation = self._map_substation(substation)
            cim_graph.add((cim_substation, RDF.type, CIM.Substation))

            # 3. Mapper les voltageLevels
            for vl in substation.voltageLevels:
                cim_vl = self._map_voltage_level(vl)
                cim_graph.add((cim_vl, CIM.Substation.contains, cim_substation))

                # 4. Mapper les Bays
                for bay in vl.bays:
                    cim_bay = self._map_bay(bay)

                    # 5. Mapper les équipements
                    for equipment in bay.equipment:
                        cim_eq = self._map_equipment(equipment)
                        cim_graph.add((cim_eq, CIM.Equipment.EquipmentContainer, cim_bay))

        return cim_graph


class CIMToIEC61850Converter(BaseConverter):
    """
    Convertit CIM/CGMES → IEC 61850 SCL

    Input:  CIM CGMES (XML) ou Graph RDF (CIM)
    Output: Fichier SCL (XML) ou Graph RDF (IEC 61850)
    """

    def convert(self, cim_input: Union[str, Graph]) -> str:
        """
        Conversion CIM → IEC 61850

        Étapes :
        1. Parser le CIM (si XML)
        2. Extraire la topologie CIM
        3. Mapper vers SCL
        4. Générer les IEDs par défaut
        5. Créer les LNodes pour chaque équipement
        6. Générer le XML SCL
        """
        scl_root = Element("SCL", nsmap={...})

        # ... conversion inverse

        return ET.tostring(scl_root, pretty_print=True)
```

## Tables de mapping

```python
# mapping_rules.py

IEC61850_TO_CIM_EQUIPMENT = {
    "CBR": "cim:Breaker",
    "DIS": "cim:Disconnector",
    "CTR": "cim:CurrentTransformer",
    "VTR": "cim:PotentialTransformer",
    "PTR": "cim:PowerTransformer",
    # ... etc
}

CIM_TO_IEC61850_EQUIPMENT = {
    "cim:Breaker": "CBR",
    "cim:Disconnector": "DIS",
    "cim:CurrentTransformer": "CTR",
    # ... etc
}

# Sous-types RTE
RTE_DISCONNECTOR_SUBTYPES = {
    "SA": "cim:Disconnector",  # Aiguillage
    "SL": "cim:Disconnector",  # Ligne
    "ST": "cim:GroundDisconnector",  # Terre
    "SS": "cim:Disconnector"   # Sectionnement
}
```

## Exemple de conversion

### Input : IEC 61850 SCL

```xml
<Substation name="POSTE">
  <VoltageLevel name="4" voltage="90kV">
    <Bay name="4ZBIGN.1">
      <ConductingEquipment type="CBR" name="DJ">
        <Terminal connectivityNode="POSTE/4/4ZBIGN1/NODE_A"/>
        <Terminal connectivityNode="POSTE/4/4ZBIGN1/NODE_B"/>
      </ConductingEquipment>
      <ConnectivityNode name="NODE_A"/>
      <ConnectivityNode name="NODE_B"/>
    </Bay>
  </VoltageLevel>
</Substation>
```

### Output : CIM/CGMES

```xml
<cim:Substation rdf:ID="POSTE">
  <cim:IdentifiedObject.name>POSTE</cim:IdentifiedObject.name>
</cim:Substation>

<cim:VoltageLevel rdf:ID="POSTE_VL_4">
  <cim:IdentifiedObject.name>4</cim:IdentifiedObject.name>
  <cim:VoltageLevel.Substation rdf:resource="#POSTE"/>
  <cim:VoltageLevel.BaseVoltage rdf:resource="#BaseVoltage_90kV"/>
</cim:VoltageLevel>

<cim:Bay rdf:ID="POSTE_BAY_4ZBIGN1">
  <cim:IdentifiedObject.name>4ZBIGN.1</cim:IdentifiedObject.name>
  <cim:Bay.VoltageLevel rdf:resource="#POSTE_VL_4"/>
</cim:Bay>

<cim:Breaker rdf:ID="POSTE_4ZBIGN1_DJ">
  <cim:IdentifiedObject.name>DJ</cim:IdentifiedObject.name>
  <cim:Equipment.EquipmentContainer rdf:resource="#POSTE_BAY_4ZBIGN1"/>
</cim:Breaker>

<cim:Terminal rdf:ID="POSTE_4ZBIGN1_DJ_T1">
  <cim:Terminal.ConductingEquipment rdf:resource="#POSTE_4ZBIGN1_DJ"/>
  <cim:Terminal.ConnectivityNode rdf:resource="#POSTE_4ZBIGN1_NODE_A"/>
</cim:Terminal>

<cim:ConnectivityNode rdf:ID="POSTE_4ZBIGN1_NODE_A">
  <cim:IdentifiedObject.name>NODE_A</cim:IdentifiedObject.name>
  <cim:ConnectivityNode.ConnectivityNodeContainer rdf:resource="#POSTE_BAY_4ZBIGN1"/>
</cim:ConnectivityNode>
```

## Phases d'implémentation

### Phase 1 : POC Minimal ✅
- ✅ Mapping basique : Substation, VoltageLevel, Bay
- ✅ Équipements principaux : CBR, DIS
- ✅ Connectivité : Terminals, ConnectivityNodes
- ✅ Conversion IEC 61850 → CIM uniquement

### Phase 2 : Extension
- ⏳ Tous les types d'équipements (CTR, VTR, PTR, etc.)
- ⏳ Support des sous-types RTE (SA, SL, ST, SS)
- ⏳ Validation des conversions

### Phase 3 : Bidirectionnel
- ⏳ Conversion CIM → IEC 61850
- ⏳ Génération des IEDs par défaut
- ⏳ Création des LNodes

### Phase 4 : Production
- ⏳ Gestion des erreurs robuste
- ⏳ Tests exhaustifs
- ⏳ Documentation complète
- ⏳ Performance (fichiers volumineux)

## Références

- **IEC 62361-102** : Harmonization IEC 61850 / CIM
- **IEC 61850-6** : SCL Language
- **IEC 61970-301** : CIM Base
- **CGMES** : ENTSO-E Common Grid Model Exchange Specification
- **PowSyBl** : Framework Java pour CIM/CGMES

## Prochaines étapes

1. ⏳ Créer la structure de base du convertisseur
2. ⏳ Implémenter le mapping IEC 61850 → CIM pour un Bay simple
3. ⏳ Tester avec le fichier SCD_POSTE_V1.scd
4. ⏳ Intégrer avec PowSyBl pour générer le SVG
