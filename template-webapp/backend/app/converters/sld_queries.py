"""
Requêtes SPARQL optimisées pour extraction SLD

Ce module contient des requêtes SPARQL chirurgicales qui extraient
UNIQUEMENT les données nécessaires à la génération d'un schéma unifilaire.

Ignore :
- IED descriptions (LDevice, LN, DO, DA) → 70% du fichier
- Communication (SubNetwork, ConnectedAP) → 10% du fichier
- DataTypeTemplates (LNodeType, DOType, DAType) → 15% du fichier

Extrait :
- Substation topology (Substation → VoltageLevel → Bay) → 2% du fichier
- Primary equipment (CBR, DIS, CTR, VTR, PTR) → 3% du fichier
- Connectivity (Terminal, ConnectivityNode) → 2% du fichier

Total : ~7% du fichier original
"""

# Liste des types d'équipements visibles sur un SLD
SLD_PRIMARY_EQUIPMENT_TYPES = [
    "BUSBAR",  # Busbar / Jeu De Barres (peut être explicite dans certains fichiers)
    "CBR",  # Circuit Breaker (Disjoncteur)
    "DIS",  # Disconnector (Sectionneur)
    "CTR",  # Current Transformer (TC)
    "VTR",  # Voltage Transformer (TT)
    "PTR",  # Power Transformer (Transfo puissance)
    "CAP",  # Capacitor (Condensateur)
    "REA",  # Reactor (Réactance)
    "GEN",  # Generator (Générateur)
    "BAT",  # Battery (Batterie)
    "MOT",  # Motor (Moteur)
]


def get_substation_topology_query() -> str:
    """
    Requête SPARQL pour extraire la topologie complète du poste

    Extrait :
    - Substation (nom, description)
    - VoltageLevel (nom, tension nominale)
    - Bay (nom, type)

    Ignore tout le reste (IEDs, Communication, etc.)
    """
    return """
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT
        ?substation ?substationName ?substationDesc
        ?voltageLevel ?voltageLevelName ?nomFreq ?voltage
        ?bay ?bayName ?bayDesc
    WHERE {
        # Substation (racine)
        ?substation rdf:type iec:Substation ;
                   iec:name ?substationName .

        OPTIONAL { ?substation iec:desc ?substationDesc }

        # VoltageLevel
        ?substation iec:hasVoltageLevel ?voltageLevel .
        ?voltageLevel rdf:type iec:VoltageLevel ;
                     iec:name ?voltageLevelName .

        OPTIONAL { ?voltageLevel iec:nomFreq ?nomFreq }
        OPTIONAL {
            ?voltageLevel iec:voltage ?voltageNode .
            ?voltageNode iec:value ?voltage
        }

        # Bay (travées)
        ?voltageLevel iec:hasBay ?bay .
        ?bay rdf:type iec:Bay ;
            iec:name ?bayName .

        OPTIONAL { ?bay iec:desc ?bayDesc }
    }
    ORDER BY ?substationName ?voltageLevelName ?bayName
    """


def get_primary_equipment_query() -> str:
    """
    Requête SPARQL pour extraire UNIQUEMENT les équipements primaires

    Filtre sur les types d'équipements visibles sur le SLD.
    Ignore tous les équipements de mesure, protection, contrôle.

    Extrait aussi les sous-types RTE (SA, SL, ST, SS) pour les sectionneurs.
    """
    types_filter = '", "'.join(SLD_PRIMARY_EQUIPMENT_TYPES)

    return f"""
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX private: <http://iec61850.com/private#>

    SELECT DISTINCT
        ?equipment ?name ?type ?desc
        ?substationName ?voltageLevelName ?bayName
        ?subtype
    WHERE {{
        # Naviguer depuis Substation jusqu'à Equipment
        ?substation rdf:type iec:Substation ;
                   iec:name ?substationName ;
                   iec:hasVoltageLevel ?voltageLevel .

        ?voltageLevel iec:name ?voltageLevelName ;
                     iec:hasBay ?bay .

        ?bay iec:name ?bayName ;
             iec:hasConductingEquipment ?equipment .

        # Equipment avec FILTER sur le type
        ?equipment rdf:type iec:ConductingEquipment ;
                  iec:name ?name ;
                  iec:type ?type .

        # FILTER : uniquement les équipements primaires pour SLD
        FILTER(?type IN ("{types_filter}"))

        OPTIONAL {{ ?equipment iec:desc ?desc }}

        # Sous-type RTE (optionnel, pour sectionneurs)
        OPTIONAL {{
            ?equipment private:hasPrivate ?private .
            ?private private:type "RTE-ConductingEquipmentType" ;
                    private:xmlContent ?subtypeContent .

            # Extraire le sous-type (SA, SL, ST, SS)
            BIND(REPLACE(?subtypeContent, ".*>([A-Z]{{2}})</.*", "$1") AS ?subtype)
        }}
    }}
    ORDER BY ?substationName ?voltageLevelName ?bayName ?name
    """


def get_connectivity_query() -> str:
    """
    Requête SPARQL pour extraire la connectivité

    Extrait UNIQUEMENT :
    - Terminals des équipements primaires
    - ConnectivityNodes connectant ces équipements

    Ignore les Terminals des équipements secondaires (mesures, protections, etc.)
    """
    types_filter = '", "'.join(SLD_PRIMARY_EQUIPMENT_TYPES)

    return f"""
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT
        ?equipment ?equipmentName ?terminalName ?terminalCNodeName
    WHERE {{
        # Equipment primaire uniquement
        ?equipment rdf:type iec:ConductingEquipment ;
                  iec:name ?equipmentName ;
                  iec:type ?equipmentType .

        # FILTER : uniquement équipements primaires
        FILTER(?equipmentType IN ("{types_filter}"))

        # Terminal de l'équipement
        ?equipment iec:hasTerminal ?terminal .
        ?terminal iec:name ?terminalName ;
                 iec:connectivityNode ?terminalCNodeName .
    }}
    ORDER BY ?equipmentName ?terminalName
    """


def get_busbar_sections_query() -> str:
    """
    Requête SPARQL pour extraire les sections de barres (jeux de barres)

    Important pour le layout du SLD (position des omnibus).
    """
    return """
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT
        ?voltageLevel ?voltageLevelName
        ?connectivityNode ?cnName ?cnPathName
        ?substationName
    WHERE {
        # Substation
        ?substation rdf:type iec:Substation ;
                   iec:name ?substationName ;
                   iec:hasVoltageLevel ?voltageLevel .

        # VoltageLevel
        ?voltageLevel iec:name ?voltageLevelName ;
                     iec:hasConnectivityNode ?connectivityNode .

        # ConnectivityNode (représente un jeu de barres)
        ?connectivityNode iec:name ?cnName ;
                         iec:pathName ?cnPathName .

        # FILTER : uniquement les nœuds "principaux" (souvent suffixés BB1, BB2, etc.)
        # Peut être adapté selon la convention de nommage
        FILTER(CONTAINS(?cnName, "BB") || CONTAINS(?cnName, "BUS"))
    }
    ORDER BY ?substationName ?voltageLevelName ?cnName
    """


def get_coupling_bays_query() -> str:
    """
    Requête SPARQL pour identifier les couplages de barres (CBO)

    Couplage = Bay contenant un disjoncteur reliant deux jeux de barres.
    Important pour les conventions RTE (position du couplage à gauche/droite).
    """
    return """
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT
        ?bay ?bayName ?bayDesc
        ?voltageLevel ?voltageLevelName
        ?substationName
        ?breaker ?breakerName
    WHERE {
        # Navigation
        ?substation rdf:type iec:Substation ;
                   iec:name ?substationName ;
                   iec:hasVoltageLevel ?voltageLevel .

        ?voltageLevel iec:name ?voltageLevelName ;
                     iec:hasBay ?bay .

        ?bay iec:name ?bayName ;
            iec:hasConductingEquipment ?breaker .

        OPTIONAL { ?bay iec:desc ?bayDesc }

        # Disjoncteur dans le Bay
        ?breaker rdf:type iec:ConductingEquipment ;
                iec:name ?breakerName ;
                iec:type "CBR" .

        # FILTER : détecter les couplages par nom
        # Convention : "CBO", "COUPL", "COUPLING" dans le nom du Bay
        FILTER(
            CONTAINS(LCASE(?bayName), "cbo") ||
            CONTAINS(LCASE(?bayName), "coupl") ||
            CONTAINS(LCASE(?bayName), "coupling")
        )
    }
    ORDER BY ?substationName ?voltageLevelName ?bayName
    """


def get_transformer_bays_query() -> str:
    """
    Requête SPARQL pour identifier les transformateurs de puissance

    Important car ils relient souvent plusieurs niveaux de tension.
    """
    return """
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT
        ?transformer ?transformerName ?transformerDesc
        ?bay ?bayName
        ?voltageLevel ?voltageLevelName
        ?substationName
    WHERE {
        # Navigation
        ?substation rdf:type iec:Substation ;
                   iec:name ?substationName ;
                   iec:hasVoltageLevel ?voltageLevel .

        ?voltageLevel iec:name ?voltageLevelName ;
                     iec:hasBay ?bay .

        ?bay iec:name ?bayName ;
            iec:hasConductingEquipment ?transformer .

        # Transformateur de puissance
        ?transformer rdf:type iec:ConductingEquipment ;
                    iec:name ?transformerName ;
                    iec:type "PTR" .

        OPTIONAL { ?transformer iec:desc ?transformerDesc }
    }
    ORDER BY ?substationName ?voltageLevelName ?bayName
    """


# Requête combinée ultra-optimisée (tout en une seule requête)
def get_sld_complete_query() -> str:
    """
    Requête SPARQL SIMPLE pour extraire TOUS les équipements primaires

    Version ultra-simplifiée: on récupère juste les équipements avec leur hiérarchie.
    Les OPTIONAL sont groupés pour éviter les produits cartésiens.
    """
    types_filter = '", "'.join(SLD_PRIMARY_EQUIPMENT_TYPES)

    return f"""
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX private: <http://iec61850.com/private#>

    SELECT DISTINCT
        ?equipment ?equipmentName ?equipmentType
        ?substationName ?voltageLevelName ?bayName
        ?equipmentSubtype ?equipmentOrder

    WHERE {{
        # Equipment primaire (point de départ)
        ?equipment rdf:type iec:ConductingEquipment ;
                  iec:name ?equipmentName ;
                  iec:type ?equipmentType .

        # FILTER : uniquement équipements primaires
        FILTER(?equipmentType IN ("{types_filter}"))

        # Hiérarchie (Bay → VoltageLevel → Substation)
        ?bay iec:hasConductingEquipment ?equipment ;
            iec:name ?bayName .

        ?voltageLevel iec:hasBay ?bay ;
                     iec:name ?voltageLevelName .

        ?substation iec:hasVoltageLevel ?voltageLevel ;
                   iec:name ?substationName .

        # Attributs optionnels (groupés)
        OPTIONAL {{ ?equipment iec:order ?equipmentOrder }}
        OPTIONAL {{
            ?equipment private:hasPrivate ?private .
            ?private private:type "RTE-ConductingEquipmentType" ;
                    private:xmlContent ?subtypeContent .
            BIND(REPLACE(?subtypeContent, ".*>([A-Z]{{2}})</.*", "$1") AS ?equipmentSubtype)
        }}
    }}
    ORDER BY ?substationName ?voltageLevelName ?bayName ?equipmentOrder ?equipmentName
    """


# Statistiques pour comparer avec fichier original
def get_statistics_query() -> str:
    """
    Requête SPARQL pour obtenir des statistiques sur ce qui est extrait vs ignoré

    Utile pour afficher :
    "Extracted: 1250 triples (7% of original 18500 triples)"
    """
    return """
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT
        (COUNT(DISTINCT ?substation) AS ?substationCount)
        (COUNT(DISTINCT ?voltageLevel) AS ?voltageLevelCount)
        (COUNT(DISTINCT ?bay) AS ?bayCount)
        (COUNT(DISTINCT ?equipment) AS ?equipmentCount)
        (COUNT(DISTINCT ?terminal) AS ?terminalCount)
        (COUNT(DISTINCT ?connectivityNode) AS ?connectivityNodeCount)
    WHERE {
        OPTIONAL { ?substation rdf:type iec:Substation }
        OPTIONAL { ?voltageLevel rdf:type iec:VoltageLevel }
        OPTIONAL { ?bay rdf:type iec:Bay }
        OPTIONAL { ?equipment rdf:type iec:ConductingEquipment }
        OPTIONAL { ?terminal rdf:type iec:Terminal }
        OPTIONAL { ?connectivityNode rdf:type iec:ConnectivityNode }
    }
    """
