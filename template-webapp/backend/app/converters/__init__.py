"""
Convertisseurs IEC 61850 ↔ CIM

Ce module gère la conversion bidirectionnelle entre :
- IEC 61850 SCL/RDF (standard postes électriques)
- CIM/CGMES (standard réseaux de transport)
"""

from .iec61850_to_cim import IEC61850ToCIMConverter

__all__ = ['IEC61850ToCIMConverter']
