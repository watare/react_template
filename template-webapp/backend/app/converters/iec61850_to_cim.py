"""
Convertisseur IEC 61850 → CIM/CGMES

Convertit un graphe RDF IEC 61850 en graphe RDF CIM via transformations SPARQL.
"""

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Namespaces
IEC = Namespace("http://iec61850.com/SCL#")
CIM = Namespace("http://iec.ch/TC57/CIM100#")
MD = Namespace("http://iec.ch/TC57/61970-552/ModelDescription/1#")
CGMES = Namespace("http://entsoe.eu/CIM/SchemaExtension/3/1#")

# Mapping des types d'équipements IEC 61850 → CIM
EQUIPMENT_TYPE_MAPPING = {
    "CBR": CIM.Breaker,
    "DIS": CIM.Disconnector,
    "CTR": CIM.CurrentTransformer,
    "VTR": CIM.PotentialTransformer,
    "PTR": CIM.PowerTransformer,
    "CAP": CIM.LinearShuntCompensator,
    "REA": CIM.LinearShuntCompensator,
    "GEN": CIM.GeneratingUnit,
    "MOT": CIM.SynchronousMachine,
    "BAT": CIM.BatteryUnit,
}

# Sous-types de sectionneurs RTE
RTE_DISCONNECTOR_SUBTYPES = {
    "ST": CIM.GroundDisconnector,  # Sectionneur de terre
    "SA": CIM.Disconnector,         # Sectionneur d'aiguillage
    "SL": CIM.Disconnector,         # Sectionneur de ligne
    "SS": CIM.Disconnector,         # Sectionneur de sectionnement
}


class IEC61850ToCIMConverter:
    """
    Convertit IEC 61850 RDF → CIM RDF

    Utilise des transformations SPARQL pour mapper:
    - Substation → Substation
    - VoltageLevel → VoltageLevel
    - Bay → Bay
    - ConductingEquipment → Equipment (CBR, DIS, CTR, etc.)
    - Terminal → Terminal
    - ConnectivityNode → ConnectivityNode
    """

    def __init__(self, base_uri: str = "http://cim.org/"):
        """
        Args:
            base_uri: URI de base pour les ressources CIM générées
        """
        self.base_uri = base_uri
        self.cim_graph = Graph()
        self.cim_graph.bind("cim", CIM)
        self.cim_graph.bind("md", MD)
        self.cim_graph.bind("rdf", RDF)
        self.cim_graph.bind("rdfs", RDFS)

    def convert(self, iec_graph: Graph) -> Graph:
        """
        Convertit un graphe IEC 61850 en graphe CIM

        Args:
            iec_graph: Graphe RDF IEC 61850

        Returns:
            Graphe RDF CIM/CGMES
        """
        logger.info("Starting IEC 61850 → CIM conversion")

        # 1. Convertir les Substations
        self._convert_substations(iec_graph)

        # 2. Convertir les VoltageLevels
        self._convert_voltage_levels(iec_graph)

        # 3. Convertir les Bays
        self._convert_bays(iec_graph)

        # 4. Convertir les équipements
        self._convert_equipment(iec_graph)

        # 5. Convertir la connectivité (Terminals, ConnectivityNodes)
        self._convert_connectivity(iec_graph)

        # 6. Ajouter les métadonnées CGMES
        self._add_cgmes_metadata()

        logger.info(f"Conversion complete: {len(self.cim_graph)} triples generated")
        return self.cim_graph

    def _convert_substations(self, iec_graph: Graph):
        """Convertit les Substations IEC → CIM"""
        query = """
        PREFIX iec: <http://iec61850.com/SCL#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?substation ?name
        WHERE {
            ?substation rdf:type iec:Substation .
            ?substation iec:name ?name .
        }
        """

        for row in iec_graph.query(query):
            substation_uri = self._create_cim_uri("Substation", str(row.name))

            # Créer la Substation CIM
            self.cim_graph.add((substation_uri, RDF.type, CIM.Substation))
            self.cim_graph.add((substation_uri, CIM.IdentifiedObject_name, Literal(str(row.name))))

            # Stocker le mapping pour les références
            self.cim_graph.add((substation_uri, RDFS.seeAlso, row.substation))

            logger.debug(f"Converted Substation: {row.name}")

    def _convert_voltage_levels(self, iec_graph: Graph):
        """Convertit les VoltageLevels IEC → CIM"""
        query = """
        PREFIX iec: <http://iec61850.com/SCL#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?voltageLevel ?name ?substationName ?nomFreq
        WHERE {
            ?substation rdf:type iec:Substation ;
                       iec:name ?substationName ;
                       iec:hasVoltageLevel ?voltageLevel .

            ?voltageLevel rdf:type iec:VoltageLevel ;
                         iec:name ?name .

            OPTIONAL { ?voltageLevel iec:nomFreq ?nomFreq }
        }
        """

        for row in iec_graph.query(query):
            vl_uri = self._create_cim_uri("VoltageLevel", f"{row.substationName}_{row.name}")
            substation_uri = self._create_cim_uri("Substation", str(row.substationName))

            # Créer le VoltageLevel CIM
            self.cim_graph.add((vl_uri, RDF.type, CIM.VoltageLevel))
            self.cim_graph.add((vl_uri, CIM.IdentifiedObject_name, Literal(str(row.name))))
            self.cim_graph.add((vl_uri, CIM.VoltageLevel_Substation, substation_uri))

            if row.nomFreq:
                self.cim_graph.add((vl_uri, CIM.VoltageLevel_nominalVoltage, Literal(float(row.nomFreq))))

            # Mapping de référence
            self.cim_graph.add((vl_uri, RDFS.seeAlso, row.voltageLevel))

            logger.debug(f"Converted VoltageLevel: {row.substationName}/{row.name}")

    def _convert_bays(self, iec_graph: Graph):
        """Convertit les Bays IEC → CIM"""
        query = """
        PREFIX iec: <http://iec61850.com/SCL#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?bay ?name ?vlName ?substationName
        WHERE {
            ?substation rdf:type iec:Substation ;
                       iec:name ?substationName ;
                       iec:hasVoltageLevel ?voltageLevel .

            ?voltageLevel rdf:type iec:VoltageLevel ;
                         iec:name ?vlName ;
                         iec:hasBay ?bay .

            ?bay rdf:type iec:Bay ;
                iec:name ?name .
        }
        """

        for row in iec_graph.query(query):
            bay_uri = self._create_cim_uri("Bay", f"{row.substationName}_{row.vlName}_{row.name}")
            vl_uri = self._create_cim_uri("VoltageLevel", f"{row.substationName}_{row.vlName}")

            # Créer le Bay CIM
            self.cim_graph.add((bay_uri, RDF.type, CIM.Bay))
            self.cim_graph.add((bay_uri, CIM.IdentifiedObject_name, Literal(str(row.name))))
            self.cim_graph.add((bay_uri, CIM.Bay_VoltageLevel, vl_uri))

            # Mapping de référence
            self.cim_graph.add((bay_uri, RDFS.seeAlso, row.bay))

            logger.debug(f"Converted Bay: {row.substationName}/{row.vlName}/{row.name}")

    def _convert_equipment(self, iec_graph: Graph):
        """Convertit les ConductingEquipment IEC → CIM"""
        query = """
        PREFIX iec: <http://iec61850.com/SCL#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX private: <http://iec61850.com/private#>

        SELECT ?equipment ?name ?type ?bayName ?vlName ?substationName ?subtype
        WHERE {
            ?substation rdf:type iec:Substation ;
                       iec:name ?substationName ;
                       iec:hasVoltageLevel ?voltageLevel .

            ?voltageLevel iec:name ?vlName ;
                         iec:hasBay ?bay .

            ?bay iec:name ?bayName ;
                 iec:hasConductingEquipment ?equipment .

            ?equipment rdf:type iec:ConductingEquipment ;
                      iec:name ?name ;
                      iec:type ?type .

            # Tenter de récupérer le sous-type RTE (pour sectionneurs)
            OPTIONAL {
                ?equipment private:hasPrivate ?private .
                ?private private:type "RTE-ConductingEquipmentType" ;
                        private:xmlContent ?subtypeContent .
                # Extraire le sous-type du XML encodé (simplifié)
                BIND(REPLACE(?subtypeContent, ".*>([A-Z]+)</.*", "$1") AS ?subtype)
            }
        }
        """

        for row in iec_graph.query(query):
            eq_type = str(row.type)
            eq_name = str(row.name)
            bay_uri = self._create_cim_uri("Bay", f"{row.substationName}_{row.vlName}_{row.bayName}")

            # Déterminer la classe CIM
            if eq_type == "DIS" and row.subtype:
                # Sectionneur avec sous-type RTE
                cim_class = RTE_DISCONNECTOR_SUBTYPES.get(str(row.subtype), CIM.Disconnector)
            else:
                cim_class = EQUIPMENT_TYPE_MAPPING.get(eq_type, CIM.ConductingEquipment)

            eq_uri = self._create_cim_uri(
                cim_class.split("#")[-1],
                f"{row.substationName}_{row.vlName}_{row.bayName}_{eq_name}"
            )

            # Créer l'équipement CIM
            self.cim_graph.add((eq_uri, RDF.type, cim_class))
            self.cim_graph.add((eq_uri, CIM.IdentifiedObject_name, Literal(eq_name)))
            self.cim_graph.add((eq_uri, CIM.Equipment_EquipmentContainer, bay_uri))

            # Mapping de référence
            self.cim_graph.add((eq_uri, RDFS.seeAlso, row.equipment))

            logger.debug(f"Converted Equipment: {eq_name} ({eq_type} → {cim_class})")

    def _convert_connectivity(self, iec_graph: Graph):
        """Convertit les Terminals et ConnectivityNodes IEC → CIM"""
        query = """
        PREFIX iec: <http://iec61850.com/SCL#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?equipment ?eqName ?terminal ?terminalName ?connectivityNode ?cnName
        WHERE {
            ?equipment rdf:type iec:ConductingEquipment ;
                      iec:name ?eqName ;
                      iec:hasTerminal ?terminal .

            ?terminal iec:name ?terminalName ;
                     iec:connectivityNode ?connectivityNode .

            ?connectivityNode iec:name ?cnName .
        }
        """

        for row in iec_graph.query(query):
            # TODO: Retrouver l'URI CIM de l'équipement via le mapping
            # Pour l'instant, création simplifiée

            terminal_uri = self._create_cim_uri("Terminal", f"{row.eqName}_{row.terminalName}")
            cn_uri = self._create_cim_uri("ConnectivityNode", str(row.cnName))

            # Créer le Terminal CIM
            self.cim_graph.add((terminal_uri, RDF.type, CIM.Terminal))
            self.cim_graph.add((terminal_uri, CIM.Terminal_ConnectivityNode, cn_uri))

            # Créer le ConnectivityNode CIM (s'il n'existe pas déjà)
            if (cn_uri, RDF.type, CIM.ConnectivityNode) not in self.cim_graph:
                self.cim_graph.add((cn_uri, RDF.type, CIM.ConnectivityNode))
                self.cim_graph.add((cn_uri, CIM.IdentifiedObject_name, Literal(str(row.cnName))))

            logger.debug(f"Converted connectivity: {row.eqName} → {row.cnName}")

    def _add_cgmes_metadata(self):
        """Ajoute les métadonnées CGMES requises"""
        model_uri = URIRef(f"{self.base_uri}FullModel")

        self.cim_graph.add((model_uri, RDF.type, MD.FullModel))
        self.cim_graph.add((model_uri, MD.Model_created, Literal("2025-01-01T00:00:00Z")))
        self.cim_graph.add((model_uri, MD.Model_description, Literal("Converted from IEC 61850 SCL")))
        self.cim_graph.add((model_uri, MD.Model_version, Literal("1.0")))
        self.cim_graph.add((model_uri, MD.Model_profile, Literal("http://entsoe.eu/CIM/EquipmentCore/3/1")))

    def _create_cim_uri(self, resource_type: str, identifier: str) -> URIRef:
        """
        Crée une URI CIM

        Args:
            resource_type: Type de ressource (Substation, VoltageLevel, etc.)
            identifier: Identifiant unique

        Returns:
            URI RDF
        """
        # Nettoyer l'identifiant (enlever espaces, caractères spéciaux)
        clean_id = identifier.replace(" ", "_").replace("/", "_").replace(".", "_")
        return URIRef(f"{self.base_uri}{resource_type}/{clean_id}")

    def export_cgmes_xml(self, output_file: str):
        """
        Exporte le graphe CIM en format CGMES XML

        Args:
            output_file: Chemin du fichier de sortie
        """
        # Sérialiser en RDF/XML (format CGMES standard)
        self.cim_graph.serialize(destination=output_file, format='xml', encoding='utf-8')
        logger.info(f"CGMES XML exported to {output_file}")
