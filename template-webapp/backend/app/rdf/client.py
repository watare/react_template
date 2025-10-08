import requests
from typing import Dict, List, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RDFClient:
    """Client for interacting with Apache Jena Fuseki SPARQL endpoint"""

    def __init__(self):
        self.base_url = f"{settings.FUSEKI_URL}/{settings.FUSEKI_DATASET}"
        self.sparql_endpoint = f"{self.base_url}/sparql"
        self.update_endpoint = f"{self.base_url}/update"
        self.data_endpoint = f"{self.base_url}/data"

    def query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL SELECT query

        Args:
            sparql_query: SPARQL query string

        Returns:
            List of result bindings
        """
        try:
            logger.debug(f"Executing SPARQL query:\n{sparql_query}")

            response = requests.post(
                self.sparql_endpoint,
                data={"query": sparql_query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=30
            )
            response.raise_for_status()

            results = response.json()
            bindings = results.get("results", {}).get("bindings", [])

            logger.info(f"Query returned {len(bindings)} results")
            return bindings

        except requests.exceptions.RequestException as e:
            logger.error(f"SPARQL query failed: {str(e)}")
            raise

    def update(self, sparql_update: str) -> None:
        """
        Execute a SPARQL UPDATE query (INSERT/DELETE)

        Args:
            sparql_update: SPARQL UPDATE query string
        """
        try:
            logger.debug(f"Executing SPARQL update:\n{sparql_update}")

            response = requests.post(
                self.update_endpoint,
                data={"update": sparql_update},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response.raise_for_status()

            logger.info("Update executed successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"SPARQL update failed: {str(e)}")
            raise

    def ask(self, sparql_query: str) -> bool:
        """
        Execute a SPARQL ASK query

        Args:
            sparql_query: SPARQL ASK query string

        Returns:
            True if pattern exists, False otherwise
        """
        try:
            response = requests.post(
                self.sparql_endpoint,
                data={"query": sparql_query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=30
            )
            response.raise_for_status()

            results = response.json()
            return results.get("boolean", False)

        except requests.exceptions.RequestException as e:
            logger.error(f"SPARQL ASK query failed: {str(e)}")
            raise

    def load_turtle(self, turtle_data: str) -> None:
        """
        Load Turtle RDF data into the dataset

        Args:
            turtle_data: RDF data in Turtle format
        """
        try:
            response = requests.post(
                self.data_endpoint,
                data=turtle_data,
                headers={"Content-Type": "text/turtle"},
                timeout=30
            )
            response.raise_for_status()

            logger.info("Turtle data loaded successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to load Turtle data: {str(e)}")
            raise


# Global RDF client instance
rdf_client = RDFClient()
