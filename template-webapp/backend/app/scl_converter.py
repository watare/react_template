#!/usr/bin/env python3
"""
IEC 61850 SCL to RDF Converter with Private Field Management
Preserves element order and private XML sections for round-trip conversion
"""

import sys
from lxml import etree
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, XSD
from rdflib.namespace import DCTERMS
from collections import OrderedDict
import json
import base64
from urllib.parse import quote, unquote


# Define IEC 61850 namespaces
SCL_NS = "http://www.iec.ch/61850/2003/SCL"
IEC = Namespace("http://iec61850.com/SCL#")
TOPOLOGY = Namespace("http://iec61850.com/topology#")
PRIVATE = Namespace("http://iec61850.com/private#")

# Namespace map for SCL
NSMAP = {
    'scl': SCL_NS,
    'compas': 'https://www.lfenergy.org/compas/extension/v1',
    'rte': 'http://www.rte-international.com'
}


class SCLToRDFConverter:
    """Convert SCL XML to RDF while preserving private sections and element order"""

    def __init__(self):
        self.graph = Graph()
        self.graph.bind("iec", IEC)
        self.graph.bind("topology", TOPOLOGY)
        self.graph.bind("private", PRIVATE)
        self.graph.bind("dcterms", DCTERMS)

        # Track element order globally
        self.element_order = {}
        self.order_counter = 0

    def _get_next_order(self):
        """Get next order number"""
        self.order_counter += 1
        return self.order_counter

    def _serialize_private_element(self, element):
        """Serialize Private element as base64-encoded XML string"""
        return base64.b64encode(
            etree.tostring(element, encoding='utf-8', pretty_print=False)
        ).decode('utf-8')

    def _create_element_uri(self, element, parent_uri=None):
        """Create a unique URI for an element with proper URL encoding"""
        # Always use order counter to ensure uniqueness
        # Names are not unique (e.g., DAI name="d" appears thousands of times)
        order = self._get_next_order()
        tag = etree.QName(element.tag).localname

        # Try to use id or name for readability, but append order for uniqueness
        elem_id = element.get('id') or element.get('name')

        if elem_id and parent_uri:
            # URL-encode the element ID to handle spaces and special characters
            encoded_id = quote(elem_id, safe='')
            return URIRef(f"{parent_uri}/{encoded_id}_{order}")
        elif elem_id:
            # Root level element with ID/name
            encoded_id = quote(elem_id, safe='')
            return URIRef(f"{IEC}{tag}/{encoded_id}")
        elif parent_uri:
            # No ID/name, use tag and order
            return URIRef(f"{parent_uri}/{tag}_{order}")
        else:
            # Root level, no ID/name
            return URIRef(f"{IEC}{tag}_{order}")

    def _process_element(self, element, parent_uri=None, parent_order=None):
        """Recursively process XML element to RDF"""
        tag = etree.QName(element.tag).localname

        # Skip comments and processing instructions
        if not isinstance(element.tag, str):
            return None

        # Handle Private elements specially
        if tag == 'Private':
            private_uri = self._create_element_uri(element, parent_uri)

            # Store order information
            order = self._get_next_order()
            self.graph.add((private_uri, RDF.type, PRIVATE.PrivateSection))
            self.graph.add((private_uri, PRIVATE.order, Literal(order, datatype=XSD.integer)))

            if parent_uri:
                self.graph.add((parent_uri, PRIVATE.hasPrivate, private_uri))

            # Store serialized XML
            serialized = self._serialize_private_element(element)
            self.graph.add((private_uri, PRIVATE.xmlContent, Literal(serialized)))

            # Store type attribute if present
            private_type = element.get('type')
            if private_type:
                self.graph.add((private_uri, PRIVATE.type, Literal(private_type)))

            return private_uri

        # Create URI for this element
        element_uri = self._create_element_uri(element, parent_uri)

        # Store order information
        order = self._get_next_order()
        self.graph.add((element_uri, IEC.order, Literal(order, datatype=XSD.integer)))

        # Add type
        self.graph.add((element_uri, RDF.type, IEC[tag]))

        # Link to parent
        if parent_uri:
            self.graph.add((parent_uri, IEC[f"has{tag}"], element_uri))

        # Process attributes
        for attr_name, attr_value in element.attrib.items():
            # Handle namespaced attributes properly
            if isinstance(attr_name, str) and attr_name.startswith('{'):
                # This is a namespaced attribute like {http://namespace}localName
                # Store it as a literal string to preserve during round-trip
                attr_uri = IEC[f"attr_{quote(attr_name, safe='')}"]
            else:
                attr_uri = IEC[attr_name]
            self.graph.add((element_uri, attr_uri, Literal(attr_value)))

        # Process text content
        if element.text and element.text.strip():
            self.graph.add((element_uri, IEC.textContent, Literal(element.text.strip())))

        # Process child elements
        for child in element:
            self._process_element(child, element_uri, order)

        return element_uri

    def convert(self, scl_file):
        """Convert SCL file to RDF graph"""
        try:
            tree = etree.parse(scl_file)
            root = tree.getroot()

            # Store all namespaces from the original document for round-trip preservation
            # This ensures xmlns declarations are restored on the root element
            root_nsmap = root.nsmap
            if root_nsmap:
                for prefix, uri in root_nsmap.items():
                    if prefix is None:
                        # Default namespace
                        self.graph.add((IEC.SCL, IEC.defaultNamespace, Literal(uri)))
                    else:
                        # Prefixed namespace
                        self.graph.add((IEC.SCL, IEC[f"namespace_{prefix}"], Literal(uri)))

            # Process root element
            self._process_element(root)

            return self.graph

        except Exception as e:
            print(f"Error converting SCL to RDF: {e}", file=sys.stderr)
            raise

    def save_rdf(self, output_file, format='turtle'):
        """Save RDF graph to file"""
        self.graph.serialize(destination=output_file, format=format, encoding='utf-8')


class RDFToSCLConverter:
    """Convert RDF back to SCL XML with proper element order and private section restoration"""

    def __init__(self, rdf_graph):
        self.graph = rdf_graph
        # Restore namespaces from the RDF graph
        self.nsmap = self._restore_namespaces()

    def _restore_namespaces(self):
        """Restore namespace map from RDF graph"""
        nsmap = {}

        # Get default namespace
        default_ns = self.graph.value(IEC.SCL, IEC.defaultNamespace)
        if default_ns:
            nsmap[None] = str(default_ns)
        else:
            nsmap[None] = SCL_NS  # Fallback to default

        # Get prefixed namespaces
        for pred, ns_uri in self.graph.predicate_objects(IEC.SCL):
            pred_str = str(pred)
            if pred_str.startswith(str(IEC) + "namespace_"):
                prefix = pred_str.replace(str(IEC) + "namespace_", "")
                nsmap[prefix] = str(ns_uri)

        return nsmap

    def _deserialize_private_element(self, base64_content):
        """Deserialize base64-encoded XML string back to element"""
        xml_bytes = base64.b64decode(base64_content.encode('utf-8'))
        return etree.fromstring(xml_bytes)

    def _get_element_order(self, uri):
        """Get order number for an element"""
        # Check both order types
        for order_pred in [IEC.order, PRIVATE.order]:
            order_value = self.graph.value(uri, order_pred)
            if order_value:
                return int(order_value)
        return 0

    def _build_element(self, uri, parent_element=None):
        """Recursively build XML element from RDF"""

        # Check if this is a Private element
        types = list(self.graph.objects(uri, RDF.type))

        if PRIVATE.PrivateSection in types:
            # Deserialize the private XML content
            xml_content = self.graph.value(uri, PRIVATE.xmlContent)
            if xml_content:
                return self._deserialize_private_element(str(xml_content))
            return None

        # Get element type (tag name)
        element_type = None
        for type_uri in types:
            if str(type_uri).startswith(str(IEC)):
                element_type = str(type_uri).replace(str(IEC), '')
                break

        if not element_type:
            return None

        # Create element
        tag = f"{{{SCL_NS}}}{element_type}"
        element = etree.Element(tag, nsmap=self.nsmap)

        # Add attributes (skip RDF metadata attributes)
        skip_predicates = {
            str(RDF.type),
            str(IEC.order),
            str(IEC.textContent),
            str(PRIVATE.order),
            str(PRIVATE.hasPrivate)
        }

        # Collect attributes
        for pred, obj in self.graph.predicate_objects(uri):
            pred_str = str(pred)

            # Skip if it's a relationship to another element
            if pred_str.startswith(str(IEC) + "has"):
                continue

            if pred_str not in skip_predicates and not pred_str.startswith(str(PRIVATE)):
                attr_name = pred_str.replace(str(IEC), '')

                # Handle encoded namespaced attributes
                if attr_name.startswith('attr_'):
                    # This was a namespaced attribute, remove prefix and decode
                    attr_name = attr_name[5:]  # Remove 'attr_' prefix
                    attr_name = unquote(attr_name)

                element.set(attr_name, str(obj))

        # Add text content
        text_content = self.graph.value(uri, IEC.textContent)
        if text_content:
            element.text = str(text_content)

        # Get and sort child elements by order
        children = []

        # Get regular children
        for pred, child_uri in self.graph.predicate_objects(uri):
            pred_str = str(pred)
            if pred_str.startswith(str(IEC) + "has") and pred_str != str(IEC) + "hasPrivate":
                order = self._get_element_order(child_uri)
                children.append((order, child_uri))

        # Get private children
        for private_uri in self.graph.objects(uri, PRIVATE.hasPrivate):
            order = self._get_element_order(private_uri)
            children.append((order, private_uri))

        # Sort by order and build child elements
        children.sort(key=lambda x: x[0])

        for _, child_uri in children:
            child_element = self._build_element(child_uri, element)
            if child_element is not None:
                element.append(child_element)

        return element

    def convert(self):
        """Convert RDF graph back to SCL XML tree"""
        # Find the root SCL element
        scl_uris = list(self.graph.subjects(RDF.type, IEC.SCL))

        if not scl_uris:
            raise ValueError("No SCL root element found in RDF graph")

        root_uri = scl_uris[0]
        root_element = self._build_element(root_uri)

        return etree.ElementTree(root_element)

    def save_scl(self, output_file):
        """Save SCL XML to file"""
        tree = self.convert()
        tree.write(
            output_file,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True
        )


def main():
    """Main entry point for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert IEC 61850 SCL files to/from RDF'
    )
    parser.add_argument('input', help='Input file (SCL or RDF)')
    parser.add_argument('output', help='Output file')
    parser.add_argument(
        '--to-rdf',
        action='store_true',
        help='Convert SCL to RDF (default: auto-detect)'
    )
    parser.add_argument(
        '--to-scl',
        action='store_true',
        help='Convert RDF to SCL (default: auto-detect)'
    )
    parser.add_argument(
        '--rdf-format',
        default='turtle',
        choices=['turtle', 'xml', 'n3', 'nt', 'json-ld'],
        help='RDF serialization format (default: turtle)'
    )

    args = parser.parse_args()

    # Auto-detect conversion direction
    if not args.to_rdf and not args.to_scl:
        if args.input.endswith('.scd') or args.input.endswith('.xml'):
            args.to_rdf = True
        else:
            args.to_scl = True

    try:
        if args.to_rdf:
            print(f"Converting SCL to RDF: {args.input} -> {args.output}")
            converter = SCLToRDFConverter()
            converter.convert(args.input)
            converter.save_rdf(args.output, format=args.rdf_format)
            print(f"Successfully converted to RDF ({len(converter.graph)} triples)")

        else:  # to_scl
            print(f"Converting RDF to SCL: {args.input} -> {args.output}")
            g = Graph()
            g.parse(args.input, format=args.rdf_format)
            print(f"Loaded RDF graph ({len(g)} triples)")

            converter = RDFToSCLConverter(g)
            converter.save_scl(args.output)
            print(f"Successfully converted to SCL")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
