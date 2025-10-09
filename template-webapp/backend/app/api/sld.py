"""
API endpoints pour la génération de schémas unifilaires (Single Line Diagrams)

Endpoints:
- POST /api/sld/generate-simple : Génère un SLD simple (POC sans PowSyBl)
- POST /api/sld/generate : Génère un SLD complet (avec PowSyBl, à venir)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from app.db.base import get_db
from app.models import User, SCLFile
from app.auth.dependencies import get_current_user
from app.rdf.client import rdf_client
from app.converters.sld_queries import (
    get_substation_topology_query,
    get_primary_equipment_query,
    get_sld_complete_query
)
from app.sld.simple_svg_generator import generate_simple_svg
from rdflib import Graph

router = APIRouter(prefix="/sld", tags=["sld"])
logger = logging.getLogger(__name__)


class SLDGenerateRequest(BaseModel):
    """Request body for SLD generation"""
    file_id: int


def extract_binding_value(binding):
    """Extrait la valeur d'un binding SPARQL"""
    if binding is None:
        return None
    return str(binding)


@router.post("/generate-simple")
async def generate_simple_sld(
    request: SLDGenerateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère un schéma unifilaire simple (POC)

    Cette version utilise un générateur SVG basique en Python
    pour valider que les requêtes SPARQL extraient bien les bonnes données.

    Args:
        file_id: ID du fichier SCL

    Returns:
        {
            "svg": "<svg>...</svg>",
            "statistics": {
                "substations": 1,
                "voltage_levels": 3,
                "bays": 12,
                "equipments": 45
            }
        }
    """
    # Extract file_id from request body
    file_id = request.file_id

    logger.info(f"Generating simple SLD for file_id={file_id}, user={current_user.username}")

    # 1. Vérifier que le fichier existe
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()
    if not scl_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SCL file with id {file_id} not found"
        )

    # 2. Exécuter la requête SPARQL combinée (optimisée) sur Fuseki
    logger.info("Executing SPARQL query to extract SLD data")
    query = get_sld_complete_query()

    try:
        results = rdf_client.query(scl_file.fuseki_dataset, query)
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute SPARQL query: {str(e)}"
        )

    logger.info(f"SPARQL query returned {len(results)} rows")

    # 3. Organiser les résultats (bindings JSON de Fuseki)
    topology_data = {
        "substations": set(),
        "voltage_levels": [],
        "bays": [],
        "equipments": []
    }

    voltage_levels_seen = {}
    bays_seen = {}

    for binding in results:
        # Extraire les valeurs des bindings JSON
        substation_name = binding.get("substationName", {}).get("value")
        vl_name = binding.get("voltageLevelName", {}).get("value")
        bay_name = binding.get("bayName", {}).get("value")

        if not all([substation_name, vl_name, bay_name]):
            continue

        topology_data["substations"].add(substation_name)

        # VoltageLevel (dédupliqué)
        vl_key = f"{substation_name}_{vl_name}"
        if vl_key not in voltage_levels_seen:
            voltage_levels_seen[vl_key] = True
            voltage = binding.get("voltage", {}).get("value") or binding.get("nomFreq", {}).get("value")
            topology_data["voltage_levels"].append({
                "substationName": substation_name,
                "voltageLevelName": vl_name,
                "voltage": voltage
            })

        # Bay (dédupliqué)
        bay_key = f"{substation_name}_{vl_name}_{bay_name}"
        if bay_key not in bays_seen:
            bays_seen[bay_key] = True
            voltage = binding.get("voltage", {}).get("value") or binding.get("nomFreq", {}).get("value")
            topology_data["bays"].append({
                "substationName": substation_name,
                "voltageLevelName": vl_name,
                "bayName": bay_name,
                "voltage": voltage
            })

        # Equipment (peut être None si Bay vide)
        equipment_name = binding.get("equipmentName", {}).get("value")
        if equipment_name:
            # Extract order (convert to int, default to 999 if not present)
            order_value = binding.get("equipmentOrder", {}).get("value")
            try:
                equipment_order = int(order_value) if order_value else 999
            except (ValueError, TypeError):
                equipment_order = 999

            topology_data["equipments"].append({
                "substationName": substation_name,
                "voltageLevelName": vl_name,
                "bayName": bay_name,
                "equipmentName": equipment_name,
                "equipmentType": binding.get("equipmentType", {}).get("value"),
                "equipmentSubtype": binding.get("equipmentSubtype", {}).get("value"),
                "equipmentOrder": equipment_order
            })

    # 5. Statistiques
    statistics = {
        "substations": len(topology_data["substations"]),
        "voltage_levels": len(topology_data["voltage_levels"]),
        "bays": len(topology_data["bays"]),
        "equipments": len(topology_data["equipments"]),
        "triples_extracted": len(results),
        "original_file_size": scl_file.file_size if hasattr(scl_file, 'file_size') else None
    }

    logger.info(f"SLD data extracted: {statistics}")

    # 6. Générer le SVG simple
    try:
        svg = generate_simple_svg(topology_data)
    except Exception as e:
        logger.error(f"Error generating SVG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SVG: {str(e)}"
        )

    logger.info(f"SVG generated successfully, size: {len(svg)} bytes")

    return {
        "svg": svg,
        "statistics": statistics,
        "file_name": scl_file.filename,
        "generator": "simple-svg-poc"
    }


@router.post("/generate-data")
async def generate_sld_data(
    request: SLDGenerateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère les données structurées pour un SLD interactif (component-based)

    Retourne la topologie organisée pour un rendu React component-based,
    permettant l'interactivité (clic, hover, édition future).

    Args:
        file_id: ID du fichier SCL

    Returns:
        {
            "substations": [{name, voltage_levels: [...]}],
            "statistics": {...},
            "file_name": "..."
        }
    """
    file_id = request.file_id

    logger.info(f"Generating SLD data for file_id={file_id}, user={current_user.username}")

    # 1. Vérifier que le fichier existe
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()
    if not scl_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SCL file with id {file_id} not found"
        )

    # 2. Exécuter la requête SPARQL
    logger.info("Executing SPARQL query to extract SLD data")
    query = get_sld_complete_query()

    try:
        results = rdf_client.query(scl_file.fuseki_dataset, query)
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute SPARQL query: {str(e)}"
        )

    logger.info(f"SPARQL query returned {len(results)} rows")

    # 3. Organiser en structure hiérarchique pour component-based rendering
    substations_dict = {}

    for binding in results:
        substation_name = binding.get("substationName", {}).get("value")
        vl_name = binding.get("voltageLevelName", {}).get("value")
        bay_name = binding.get("bayName", {}).get("value")

        if not all([substation_name, vl_name, bay_name]):
            continue

        # Initialiser substation
        if substation_name not in substations_dict:
            substations_dict[substation_name] = {
                "name": substation_name,
                "voltage_levels": {}
            }

        # Initialiser voltage level
        if vl_name not in substations_dict[substation_name]["voltage_levels"]:
            voltage = binding.get("voltage", {}).get("value") or binding.get("nomFreq", {}).get("value")
            substations_dict[substation_name]["voltage_levels"][vl_name] = {
                "name": vl_name,
                "voltage": voltage,
                "bays": {}
            }

        # Initialiser bay
        if bay_name not in substations_dict[substation_name]["voltage_levels"][vl_name]["bays"]:
            is_coupling = ("CBO" in bay_name.upper() or "COUPL" in bay_name.upper())
            substations_dict[substation_name]["voltage_levels"][vl_name]["bays"][bay_name] = {
                "name": bay_name,
                "is_coupling": is_coupling,
                "equipments": []
            }

        # Ajouter equipment
        equipment_name = binding.get("equipmentName", {}).get("value")
        if equipment_name:
            order_value = binding.get("equipmentOrder", {}).get("value")
            try:
                equipment_order = int(order_value) if order_value else 999
            except (ValueError, TypeError):
                equipment_order = 999

            substations_dict[substation_name]["voltage_levels"][vl_name]["bays"][bay_name]["equipments"].append({
                "name": equipment_name,
                "type": binding.get("equipmentType", {}).get("value"),
                "subtype": binding.get("equipmentSubtype", {}).get("value"),
                "order": equipment_order
            })

    # 4. Convertir en liste et trier les équipements
    substations_list = []
    for substation_name, substation_data in substations_dict.items():
        voltage_levels_list = []
        for vl_name, vl_data in substation_data["voltage_levels"].items():
            bays_list = []
            for bay_name, bay_data in vl_data["bays"].items():
                # Trier les équipements par ordre
                bay_data["equipments"].sort(key=lambda eq: (eq["order"], eq["name"]))
                # Ne garder que les bays non vides
                if len(bay_data["equipments"]) > 0:
                    bays_list.append(bay_data)

            # Ne garder que les voltage levels avec des bays non vides
            if len(bays_list) > 0:
                vl_data["bays"] = bays_list
                voltage_levels_list.append(vl_data)

        substation_data["voltage_levels"] = voltage_levels_list
        substations_list.append(substation_data)

    # 5. Statistiques
    total_bays = sum(len(vl["bays"]) for sub in substations_list for vl in sub["voltage_levels"])
    total_equipments = sum(len(bay["equipments"]) for sub in substations_list for vl in sub["voltage_levels"] for bay in vl["bays"])

    statistics = {
        "substations": len(substations_list),
        "voltage_levels": sum(len(sub["voltage_levels"]) for sub in substations_list),
        "bays": total_bays,
        "equipments": total_equipments,
        "triples_extracted": len(results)
    }

    logger.info(f"SLD data organized: {statistics}")

    return {
        "substations": substations_list,
        "statistics": statistics,
        "file_name": scl_file.filename,
        "generator": "component-based"
    }


@router.post("/generate")
async def generate_sld_with_powsybl(
    file_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère un schéma unifilaire avec PowSyBl (À VENIR)

    Cette version utilisera :
    1. Conversion IEC 61850 → CIM RDF (via convertisseur)
    2. Export CIM RDF → CGMES XML
    3. PowSyBl pour générer le SVG professionnel

    Args:
        file_id: ID du fichier SCL

    Returns:
        {
            "svg": "<svg>...</svg>",
            "generator": "powsybl"
        }
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PowSyBl integration not yet implemented. Use /generate-simple for now."
    )
