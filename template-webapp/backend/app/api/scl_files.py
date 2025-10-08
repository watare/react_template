"""
API routes for SCL file upload and management
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime
import tempfile
from pathlib import Path
import hashlib

from app.db.base import get_db
from app.models import User, SCLFile
from app.auth.dependencies import get_current_user
from app.scl_converter import SCLToRDFConverter, RDFToSCLConverter
from app.rdf.client import rdf_client
from rdflib import Graph

router = APIRouter(prefix="/api/scl-files", tags=["scl-files"])

# Configuration
UPLOAD_DIR = Path("/app/uploads/scl")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def verify_admin(user: User = Depends(get_current_user)):
    """Verify user has admin role"""
    if not user.is_superuser:
        has_admin_role = any(role.name == "admin" for role in user.roles)
        if not has_admin_role:
            raise HTTPException(status_code=403, detail="Admin access required")
    return user


def process_scl_file(
    file_id: int,
    scl_path: str,
    db: Session
):
    """
    Background task to convert SCL to RDF and validate round-trip

    Steps:
    1. Convert SCL → RDF
    2. Store RDF in Fuseki
    3. Convert RDF → SCL (validation)
    4. Compare original vs regenerated
    5. Update database status
    """
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()

    try:
        # Update status
        scl_file.status = "converting"
        db.commit()

        # Step 1: SCL → RDF
        converter = SCLToRDFConverter()
        rdf_graph = converter.convert(scl_path)

        # Save RDF file
        rdf_path = scl_path.replace(".scd", ".ttl").replace(".icd", ".ttl").replace(".cid", ".ttl")
        converter.save_rdf(rdf_path, format='turtle')

        scl_file.rdf_path = rdf_path
        scl_file.triple_count = len(rdf_graph)

        # Step 2: Store in Fuseki
        dataset_name = f"scl_file_{file_id}"

        # Create dataset in Fuseki
        try:
            rdf_client.create_dataset(dataset_name)
        except Exception as e:
            # Dataset might already exist
            pass

        # Upload RDF to Fuseki
        rdf_client.upload_file(dataset_name, rdf_path, format='turtle')
        scl_file.fuseki_dataset = dataset_name

        # Step 3: RDF → SCL (validation)
        validated_scl_path = scl_path.replace(".scd", "_validated.scd").replace(".icd", "_validated.icd").replace(".cid", "_validated.cid")

        rdf_to_scl = RDFToSCLConverter(rdf_graph)
        rdf_to_scl.save_scl(validated_scl_path)
        scl_file.validated_scl_path = validated_scl_path

        # Step 4: Compare files
        with open(scl_path, 'rb') as f1, open(validated_scl_path, 'rb') as f2:
            original_hash = hashlib.sha256(f1.read()).hexdigest()
            validated_hash = hashlib.sha256(f2.read()).hexdigest()

        if original_hash == validated_hash:
            scl_file.is_validated = True
            scl_file.validation_passed = True
            scl_file.validation_message = "Perfect round-trip: files are identical"
        else:
            # Try XML comparison (ignoring whitespace differences)
            from lxml import etree

            original_tree = etree.parse(scl_path)
            validated_tree = etree.parse(validated_scl_path)

            # Normalize and compare
            original_str = etree.tostring(original_tree, encoding='unicode', pretty_print=False)
            validated_str = etree.tostring(validated_tree, encoding='unicode', pretty_print=False)

            if original_str == validated_str:
                scl_file.is_validated = True
                scl_file.validation_passed = True
                scl_file.validation_message = "Round-trip successful (XML semantically identical)"
            else:
                scl_file.is_validated = True
                scl_file.validation_passed = False
                scl_file.validation_message = "Round-trip validation failed: XML differs"

        # Update status
        scl_file.status = "validated" if scl_file.validation_passed else "converted"
        scl_file.converted_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        scl_file.status = "failed"
        scl_file.error_message = str(e)
        db.commit()
        raise


@router.post("/upload")
async def upload_scl_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Upload SCL file (admin only)

    - Max size: 100MB
    - Supported formats: .scd, .icd, .cid
    - Automatically converts to RDF and validates round-trip
    """
    # Check file extension
    if not file.filename.endswith(('.scd', '.icd', '.cid', '.SCD', '.ICD', '.CID')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only .scd, .icd, .cid files are supported"
        )

    # Read file and check size
    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    # Save file
    with open(file_path, 'wb') as f:
        f.write(contents)

    # Create database record
    scl_file = SCLFile(
        filename=safe_filename,
        original_filename=file.filename,
        file_size=file_size,
        scl_path=str(file_path),
        status="uploaded",
        uploaded_by=user.id
    )
    db.add(scl_file)
    db.commit()
    db.refresh(scl_file)

    # Start background processing
    background_tasks.add_task(
        process_scl_file,
        scl_file.id,
        str(file_path),
        db
    )

    return {
        "id": scl_file.id,
        "filename": scl_file.filename,
        "file_size": scl_file.file_size,
        "status": scl_file.status,
        "message": "File uploaded successfully. Processing in background..."
    }


@router.get("/")
def list_scl_files(
    user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """List all uploaded SCL files (admin only)"""
    files = db.query(SCLFile).order_by(SCLFile.uploaded_at.desc()).all()

    return [{
        "id": f.id,
        "filename": f.filename,
        "original_filename": f.original_filename,
        "file_size": f.file_size,
        "status": f.status,
        "is_validated": f.is_validated,
        "validation_passed": f.validation_passed,
        "validation_message": f.validation_message,
        "triple_count": f.triple_count,
        "fuseki_dataset": f.fuseki_dataset,
        "uploaded_by": f.uploader.username if f.uploader else None,
        "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
        "converted_at": f.converted_at.isoformat() if f.converted_at else None,
        "error_message": f.error_message
    } for f in files]


@router.get("/{file_id}")
def get_scl_file(
    file_id: int,
    user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get details of a specific SCL file"""
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()

    if not scl_file:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "id": scl_file.id,
        "filename": scl_file.filename,
        "original_filename": scl_file.original_filename,
        "file_size": scl_file.file_size,
        "status": scl_file.status,
        "is_validated": scl_file.is_validated,
        "validation_passed": scl_file.validation_passed,
        "validation_message": scl_file.validation_message,
        "triple_count": scl_file.triple_count,
        "fuseki_dataset": scl_file.fuseki_dataset,
        "uploaded_by": scl_file.uploader.username if scl_file.uploader else None,
        "uploaded_at": scl_file.uploaded_at.isoformat() if scl_file.uploaded_at else None,
        "converted_at": scl_file.converted_at.isoformat() if scl_file.converted_at else None,
        "error_message": scl_file.error_message,
        "scl_path": scl_file.scl_path,
        "rdf_path": scl_file.rdf_path,
        "validated_scl_path": scl_file.validated_scl_path
    }


@router.get("/{file_id}/rdf-schema")
def get_rdf_schema(
    file_id: int,
    user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Get RDF schema/graph structure for visualization

    Returns:
    - Classes (types) and their counts
    - Sample triples for each class
    - Namespaces used
    """
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()

    if not scl_file:
        raise HTTPException(status_code=404, detail="File not found")

    if scl_file.status not in ["converted", "validated"]:
        raise HTTPException(
            status_code=400,
            detail=f"File not yet converted. Current status: {scl_file.status}"
        )

    # Query Fuseki for schema information
    dataset = scl_file.fuseki_dataset

    # Get all classes and their counts
    query_classes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?type (COUNT(?s) AS ?count)
    WHERE {
        ?s rdf:type ?type .
    }
    GROUP BY ?type
    ORDER BY DESC(?count)
    """

    classes_result = rdf_client.query(dataset, query_classes)

    classes = []
    for binding in classes_result:
        type_uri = binding["type"]["value"]
        count = int(binding["count"]["value"])

        # Get sample instances
        query_samples = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?s ?p ?o
        WHERE {{
            ?s rdf:type <{type_uri}> .
            ?s ?p ?o .
        }}
        LIMIT 10
        """

        samples_result = rdf_client.query(dataset, query_samples)

        samples = []
        for sample in samples_result:
            samples.append({
                "subject": sample["s"]["value"],
                "predicate": sample["p"]["value"],
                "object": sample["o"]["value"]
            })

        classes.append({
            "type": type_uri,
            "count": count,
            "samples": samples
        })

    # Get namespaces
    query_namespaces = """
    SELECT DISTINCT ?ns
    WHERE {
        {
            SELECT DISTINCT (STRBEFORE(STR(?s), "#") AS ?ns)
            WHERE { ?s ?p ?o }
        }
        UNION
        {
            SELECT DISTINCT (STRBEFORE(STR(?p), "#") AS ?ns)
            WHERE { ?s ?p ?o }
        }
    }
    """

    namespaces_result = rdf_client.query(dataset, query_namespaces)
    namespaces = [b["ns"]["value"] for b in namespaces_result if b.get("ns")]

    return {
        "file_id": file_id,
        "filename": scl_file.filename,
        "triple_count": scl_file.triple_count,
        "classes": classes,
        "namespaces": namespaces,
        "fuseki_dataset": dataset
    }


@router.delete("/{file_id}")
def delete_scl_file(
    file_id: int,
    user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete SCL file and associated RDF data"""
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()

    if not scl_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete files
    for path in [scl_file.scl_path, scl_file.rdf_path, scl_file.validated_scl_path]:
        if path and os.path.exists(path):
            os.remove(path)

    # Delete Fuseki dataset
    if scl_file.fuseki_dataset:
        try:
            rdf_client.delete_dataset(scl_file.fuseki_dataset)
        except Exception as e:
            # Log but don't fail
            pass

    # Delete database record
    db.delete(scl_file)
    db.commit()

    return {"message": "File deleted successfully"}
