from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.db.base import get_db
from app.models.user import User, AuditLog
from app.auth.dependencies import require_permission, get_current_active_user
from app.rdf.client import rdf_client
from app.rdf.queries import (
    list_all_nodes,
    get_node_details,
    search_nodes,
    insert_node,
    update_node_property,
    delete_node,
    count_nodes_by_type
)
import json

router = APIRouter(prefix="/nodes", tags=["nodes"])


# Schemas
class NodeCreate(BaseModel):
    id: str
    type: str
    label: str
    properties: Optional[Dict[str, str]] = None


class NodeUpdate(BaseModel):
    properties: Dict[str, str]


class NodeResponse(BaseModel):
    id: str
    type: Optional[str] = None
    label: Optional[str] = None
    properties: Dict[str, Any] = {}


@router.get("/", response_model=List[Dict[str, Any]])
def list_nodes(
    current_user: User = Depends(require_permission("nodes:read"))
):
    """List all nodes in the RDF graph"""
    try:
        query = list_all_nodes()
        bindings = rdf_client.query(query)

        nodes = []
        for binding in bindings:
            nodes.append({
                "id": binding.get("node", {}).get("value", ""),
                "type": binding.get("type", {}).get("value", ""),
                "label": binding.get("label", {}).get("value", "")
            })

        return nodes

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch nodes: {str(e)}"
        )


@router.get("/stats")
def get_node_stats(
    current_user: User = Depends(require_permission("nodes:read"))
):
    """Get statistics about nodes by type"""
    try:
        query = count_nodes_by_type()
        bindings = rdf_client.query(query)

        stats = []
        for binding in bindings:
            stats.append({
                "type": binding.get("type", {}).get("value", ""),
                "count": int(binding.get("count", {}).get("value", 0))
            })

        return {"stats": stats}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {str(e)}"
        )


@router.get("/search")
def search(
    q: str,
    current_user: User = Depends(require_permission("nodes:read"))
):
    """Search nodes by label"""
    try:
        query = search_nodes(q)
        bindings = rdf_client.query(query)

        results = []
        for binding in bindings:
            results.append({
                "id": binding.get("node", {}).get("value", ""),
                "type": binding.get("type", {}).get("value", ""),
                "label": binding.get("label", {}).get("value", "")
            })

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{node_id}")
def get_node(
    node_id: str,
    current_user: User = Depends(require_permission("nodes:read"))
):
    """Get details of a specific node"""
    try:
        query = get_node_details(node_id)
        bindings = rdf_client.query(query)

        if not bindings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )

        node = {"id": node_id, "properties": {}}
        for binding in bindings:
            prop = binding.get("property", {}).get("value", "").split("#")[-1].split("/")[-1]
            value = binding.get("value", {}).get("value", "")
            node["properties"][prop] = value

        return node

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch node: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_node(
    node_data: NodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("nodes:write"))
):
    """Create a new node in the RDF graph"""
    try:
        query = insert_node(
            node_data.id,
            node_data.type,
            node_data.label,
            node_data.properties
        )
        rdf_client.update(query)

        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action="CREATE",
            resource_type="node",
            resource_id=node_data.id,
            details=json.dumps(node_data.dict())
        )
        db.add(audit)
        db.commit()

        return {"message": "Node created successfully", "id": node_data.id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create node: {str(e)}"
        )


@router.patch("/{node_id}")
def update_node(
    node_id: str,
    updates: NodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("nodes:write"))
):
    """Update properties of a node"""
    try:
        # Update each property
        for prop, value in updates.properties.items():
            query = update_node_property(node_id, prop, value)
            rdf_client.update(query)

        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action="UPDATE",
            resource_type="node",
            resource_id=node_id,
            details=json.dumps(updates.dict())
        )
        db.add(audit)
        db.commit()

        return {"message": "Node updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update node: {str(e)}"
        )


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node_endpoint(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("nodes:delete"))
):
    """Delete a node from the RDF graph"""
    try:
        query = delete_node(node_id)
        rdf_client.update(query)

        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action="DELETE",
            resource_type="node",
            resource_id=node_id
        )
        db.add(audit)
        db.commit()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete node: {str(e)}"
        )
