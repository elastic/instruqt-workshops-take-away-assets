import logging
from elasticsearch import Elasticsearch
import os

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


def es_chat_completion(prompt, inference_id):
    logging.info(f"Starting Elasticsearch chat completion with Inference ID: {inference_id}")

    response = es_client.inference.inference(
        inference_id = inference_id,
        task_type = "completion",
        input = prompt,
        timeout="90s"
    )

    logging.info(f"Response from Elasticsearch chat completion: {response}")

    return response['completion'][0]['result']




