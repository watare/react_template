import requests
from typing import Dict, List, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RDFClient:
    """Client for interacting with Apache Jena Fuseki SPARQL endpoint"""

    def __init__(self):
        self.fuseki_url = settings.FUSEKI_URL
        self.default_dataset = settings.FUSEKI_DATASET
        self.base_url = f"{self.fuseki_url}/{self.default_dataset}"
        self.sparql_endpoint = f"{self.base_url}/sparql"
        self.update_endpoint = f"{self.base_url}/update"
        self.data_endpoint = f"{self.base_url}/data"
        # Fuseki authentication
        self.auth = (settings.FUSEKI_ADMIN_USER, settings.FUSEKI_ADMIN_PASSWORD)

    def _get_endpoints(self, dataset: Optional[str] = None):
        """Get endpoints for a specific dataset"""
        ds = dataset or self.default_dataset
        base = f"{self.fuseki_url}/{ds}"
        return {
            "sparql": f"{base}/sparql",
            "update": f"{base}/update",
            "data": f"{base}/data"
        }

    def query(self, dataset: Optional[str] = None, sparql_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL SELECT query

        Args:
            dataset: Dataset name (optional, uses default if not specified)
            sparql_query: SPARQL query string (if dataset is None, this is the first arg)

        Returns:
            List of result bindings
        """
        # Handle both signatures: query(sparql) and query(dataset, sparql)
        if sparql_query is None:
            sparql_query = dataset
            dataset = None

        endpoints = self._get_endpoints(dataset)

        try:
            logger.debug(f"Executing SPARQL query on {dataset or 'default'}:\n{sparql_query}")

            response = requests.post(
                endpoints["sparql"],
                data={"query": sparql_query},
                headers={"Accept": "application/sparql-results+json"},
                auth=self.auth,
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
                auth=self.auth,
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
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()

            results = response.json()
            return results.get("boolean", False)

        except requests.exceptions.RequestException as e:
            logger.error(f"SPARQL ASK query failed: {str(e)}")
            raise

    def load_turtle(self, turtle_data: str, dataset: Optional[str] = None) -> None:
        """
        Load Turtle RDF data into the dataset

        Args:
            turtle_data: RDF data in Turtle format
            dataset: Dataset name (optional)
        """
        endpoints = self._get_endpoints(dataset)

        try:
            response = requests.post(
                endpoints["data"],
                data=turtle_data,
                headers={"Content-Type": "text/turtle"},
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()

            logger.info("Turtle data loaded successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to load Turtle data: {str(e)}")
            raise

    def create_dataset(self, dataset_name: str, dataset_type: str = "tdb2") -> None:
        """
        Create a new dataset in Fuseki

        Args:
            dataset_name: Name of the dataset
            dataset_type: Type of dataset (tdb2, mem, etc.)
        """
        try:
            response = requests.post(
                f"{self.fuseki_url}/$/datasets",
                data={"dbName": dataset_name, "dbType": dataset_type},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Dataset '{dataset_name}' created successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create dataset: {str(e)}")
            raise

    def delete_dataset(self, dataset_name: str) -> None:
        """
        Delete a dataset from Fuseki

        Args:
            dataset_name: Name of the dataset to delete
        """
        try:
            response = requests.delete(
                f"{self.fuseki_url}/$/datasets/{dataset_name}",
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Dataset '{dataset_name}' deleted successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete dataset: {str(e)}")
            raise

    def upload_file(self, dataset: str, file_path: str, format: str = "turtle") -> None:
        """
        Upload an RDF file to Fuseki dataset

        Args:
            dataset: Dataset name
            file_path: Path to RDF file
            format: RDF format (turtle, rdf/xml, n-triples, etc.)
        """
        content_types = {
            "turtle": "text/turtle",
            "ttl": "text/turtle",
            "rdf": "application/rdf+xml",
            "xml": "application/rdf+xml",
            "nt": "application/n-triples",
            "ntriples": "application/n-triples"
        }

        content_type = content_types.get(format.lower(), "text/turtle")

        endpoints = self._get_endpoints(dataset)

        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    endpoints["data"],
                    data=f,
                    headers={"Content-Type": content_type},
                    auth=self.auth,
                    timeout=300  # 5 minutes for large files
                )
                response.raise_for_status()

            logger.info(f"File '{file_path}' uploaded to dataset '{dataset}'")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise


# Global RDF client instance
rdf_client = RDFClient()
