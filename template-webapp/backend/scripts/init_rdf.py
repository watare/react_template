"""
Initialize RDF dataset in Fuseki with sample data
"""
import sys
sys.path.append('/app')

import requests
import time
from app.core.config import settings

FUSEKI_URL = settings.FUSEKI_URL
DATASET = settings.FUSEKI_DATASET


def wait_for_fuseki():
    """Wait for Fuseki to be ready"""
    print("Waiting for Fuseki to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{FUSEKI_URL}/$/ping", timeout=2)
            if response.status_code == 200:
                print("✓ Fuseki is ready")
                return True
        except requests.exceptions.RequestException:
            pass

        print(f"  Attempt {i+1}/{max_retries}...")
        time.sleep(2)

    print("✗ Fuseki did not start in time")
    return False


def create_dataset():
    """Create dataset if it doesn't exist"""
    print(f"Creating dataset: {DATASET}...")

    try:
        # Check if dataset exists
        response = requests.get(f"{FUSEKI_URL}/$/datasets", timeout=5)
        datasets = response.json().get("datasets", [])

        dataset_exists = any(d.get("ds.name") == f"/{DATASET}" for d in datasets)

        if dataset_exists:
            print(f"  ✓ Dataset '{DATASET}' already exists")
            return True

        # Create dataset
        response = requests.post(
            f"{FUSEKI_URL}/$/datasets",
            data={
                "dbName": DATASET,
                "dbType": "tdb2"
            },
            timeout=10
        )

        if response.status_code in [200, 201]:
            print(f"  ✓ Dataset '{DATASET}' created successfully")
            return True
        else:
            print(f"  ✗ Failed to create dataset: {response.text}")
            return False

    except Exception as e:
        print(f"  ✗ Error creating dataset: {str(e)}")
        return False


def load_sample_data():
    """Load sample RDF data"""
    print("Loading sample RDF data...")

    sample_data = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix data: <http://template.app/data#> .
@prefix vocab: <http://template.app/vocab#> .

# Sample Device
data:device1 a vocab:Device ;
    rdfs:label "Main Server" ;
    vocab:status "active" ;
    vocab:location "Datacenter A" .

data:device2 a vocab:Device ;
    rdfs:label "Backup Server" ;
    vocab:status "standby" ;
    vocab:location "Datacenter B" .

# Sample Sensors
data:sensor1 a vocab:Sensor ;
    rdfs:label "Temperature Sensor 1" ;
    vocab:type "temperature" ;
    vocab:unit "celsius" ;
    vocab:deviceId "device1" .

data:sensor2 a vocab:Sensor ;
    rdfs:label "Humidity Sensor 1" ;
    vocab:type "humidity" ;
    vocab:unit "percent" ;
    vocab:deviceId "device1" .
"""

    try:
        response = requests.post(
            f"{FUSEKI_URL}/{DATASET}/data",
            data=sample_data,
            headers={"Content-Type": "text/turtle"},
            timeout=10
        )

        if response.status_code in [200, 201, 204]:
            print("  ✓ Sample data loaded successfully")
            return True
        else:
            print(f"  ✗ Failed to load data: {response.text}")
            return False

    except Exception as e:
        print(f"  ✗ Error loading data: {str(e)}")
        return False


def verify_data():
    """Verify data was loaded"""
    print("Verifying data...")

    query = """
    SELECT (COUNT(*) AS ?count)
    WHERE {
        ?s ?p ?o .
    }
    """

    try:
        response = requests.post(
            f"{FUSEKI_URL}/{DATASET}/sparql",
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=10
        )

        if response.status_code == 200:
            results = response.json()
            count = int(results["results"]["bindings"][0]["count"]["value"])
            print(f"  ✓ Found {count} triples in the dataset")
            return True
        else:
            print(f"  ✗ Failed to verify: {response.text}")
            return False

    except Exception as e:
        print(f"  ✗ Error verifying data: {str(e)}")
        return False


def main():
    """Main initialization function"""
    print("\n" + "="*50)
    print("RDF Dataset Initialization Script")
    print("="*50 + "\n")

    print(f"Fuseki URL: {FUSEKI_URL}")
    print(f"Dataset: {DATASET}\n")

    try:
        # Wait for Fuseki
        if not wait_for_fuseki():
            sys.exit(1)

        # Create dataset
        if not create_dataset():
            sys.exit(1)

        # Load sample data
        if not load_sample_data():
            sys.exit(1)

        # Verify
        if not verify_data():
            sys.exit(1)

        print("\n" + "="*50)
        print("✓ RDF dataset initialized successfully!")
        print("="*50)
        print(f"\nFuseki UI: {FUSEKI_URL}")
        print(f"Dataset: {DATASET}")
        print(f"SPARQL endpoint: {FUSEKI_URL}/{DATASET}/sparql")
        print("")

    except Exception as e:
        print(f"\n✗ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
