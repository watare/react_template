"""
Single Line Diagram (SLD) Generation Module

Ce module génère des schémas unifilaires à partir des données RDF IEC 61850.
Il supporte différents namespaces de rendu selon les conventions des GRT.
"""

from .rte_rules import RTE_NAMESPACE, RTERenderingNamespace

__all__ = ['RTE_NAMESPACE', 'RTERenderingNamespace']
