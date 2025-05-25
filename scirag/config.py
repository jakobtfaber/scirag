from pathlib import Path
import vertexai
from google import genai

# Using pathlib (modern approach) to define the base directory as the directory that contains this file.
BASE_DIR = Path(__file__).resolve().parent

# REPO_DIR is defined as one directory above the package
REPO_DIR = BASE_DIR.parent


import google.auth

credentials, project = google.auth.default()


EMBEDDING_MODEL = "publishers/google/models/text-embedding-005"  # @param {type:"string", isTemplate: true}
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 100
TOP_K = 10
DISTANCE_THRESHOLD = 0.5

GEN_MODEL = "gemini-2.5-flash-preview-05-20"


LOCATION="us-central1"
PROJECT = "camels-453517"
vertexai.init(project=PROJECT,location=LOCATION,credentials=credentials)
client = genai.Client(vertexai=True,project=PROJECT,location=LOCATION)
