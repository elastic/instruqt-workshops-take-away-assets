from elasticsearch import Elasticsearch
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Initialize the Elasticsearch client
es_url = os.getenv('ELASTICSEARCH_URL')
es_user = os.getenv('ELASTICSEARCH_USER')
es_pass = os.getenv('ELASTICSEARCH_PASSWORD')

logging.debug(f'es_url: {es_url}')
logging.debug(f'es_user: {es_user}')

es_client = Elasticsearch(
    hosts=[es_url],
    basic_auth=(
        es_user,
        es_pass
    )
)


def perform_es_search(query, index):
    """Performs the Elasticsearch query based on the context type."""
    logging.info(f"Starting Elasticsearch search for query: {query}")

## TODO USERS ENTER QUERY CODE HERE
    es_query = {

    }

    try:
        result = es_client.search(index="restaurant_reviews", body=es_query)

    except Exception as e:
        # If generated query fails fallback to backup query
        logging.error(f"Error in Elasticsearch search: {str(e)}")
        raise

    # logging.info(f"elasticsearch results: {result}")
    hits = result["hits"]["hits"]
    logging.info(f"number of hits: {len(hits)}")
    return hits

