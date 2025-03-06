import logging
import os
import requests
from io import StringIO
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def load_env():
    try:
        response = requests.get('http://kubernetes-vm:9000/env')
        response.raise_for_status()
        # Load the environment variables from the response
        load_dotenv(stream=StringIO(response.text))
        logging.debug("Environment variables loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load environment variables: {e}")

# Load environment variables from the remote source
load_env()

# --- FastAPI and routes setup ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import search_router
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optionally enable APM middleware (if configured)
# app.add_middleware(ElasticAPM, client=apm)

# Include the search router
app.include_router(search_router.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# --- Command-line flag processing ---
if __name__ == "__main__":
    import argparse
    import uvicorn

    # Create an argument parser and add the optional "-i" flag.
    parser = argparse.ArgumentParser(
        description="Run the FastAPI app with an optional INFERENCE_ID."
    )
    parser.add_argument(
        "-i",
        type=str,
        default="openai_chat_completions",
        help="Set the INFERENCE_ID environment variable (default: openai_chat_completions)"
    )
    args = parser.parse_args()

    # Override or set the INFERENCE_ID environment variable
    os.environ["INFERENCE_ID"] = args.i
    logging.debug(f"Using INFERENCE_ID: {os.environ['INFERENCE_ID']}")

    # Run the app with uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)


## to run
# /vectordb-genai-101/chat-app-code
# OpenAI version
# python -m backend.main
# Bedrock Version
# python -m backend.main -i bedrock_claude_3_sonnet