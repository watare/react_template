"""SPARQL query templates for RDF operations"""

# Common namespaces
PREFIXES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX data: <http://template.app/data#>
PREFIX vocab: <http://template.app/vocab#>
"""


def list_all_nodes() -> str:
    """Query to list all nodes in the graph"""
    return f"""
    {PREFIXES}
    SELECT ?node ?type ?label
    WHERE {{
        ?node a ?type .
        OPTIONAL {{ ?node rdfs:label ?label }}
    }}
    ORDER BY ?type ?node
    """


def get_node_details(node_id: str) -> str:
    """Query to get all properties of a specific node"""
    return f"""
    {PREFIXES}
    SELECT ?property ?value
    WHERE {{
        data:{node_id} ?property ?value .
    }}
    """


def search_nodes(search_term: str) -> str:
    """Query to search nodes by label"""
    return f"""
    {PREFIXES}
    SELECT ?node ?type ?label
    WHERE {{
        ?node a ?type .
        ?node rdfs:label ?label .
        FILTER(CONTAINS(LCASE(?label), LCASE("{search_term}")))
    }}
    """


def insert_node(node_id: str, node_type: str, label: str, properties: dict = None) -> str:
    """Generate INSERT query for a new node"""
    props = ""
    if properties:
        for key, value in properties.items():
            props += f'    data:{node_id} vocab:{key} "{value}" .\n'

    return f"""
    {PREFIXES}
    INSERT DATA {{
        data:{node_id} a vocab:{node_type} ;
                      rdfs:label "{label}" .
        {props}
    }}
    """


def update_node_property(node_id: str, property_name: str, new_value: str) -> str:
    """Generate UPDATE query to modify a node property"""
    return f"""
    {PREFIXES}
    DELETE {{ data:{node_id} vocab:{property_name} ?old }}
    INSERT {{ data:{node_id} vocab:{property_name} "{new_value}" }}
    WHERE {{
        OPTIONAL {{ data:{node_id} vocab:{property_name} ?old }}
    }}
    """


def delete_node(node_id: str) -> str:
    """Generate DELETE query to remove a node and all its properties"""
    return f"""
    {PREFIXES}
    DELETE WHERE {{
        data:{node_id} ?p ?o .
    }}
    """


def count_nodes_by_type() -> str:
    """Query to count nodes grouped by type"""
    return f"""
    {PREFIXES}
    SELECT ?type (COUNT(?node) AS ?count)
    WHERE {{
        ?node a ?type .
    }}
    GROUP BY ?type
    ORDER BY DESC(?count)
    """
