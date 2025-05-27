from pathlib import Path
import vertexai
from google import genai

# Using pathlib (modern approach) to define the base directory as the directory that contains this file.
BASE_DIR = Path(__file__).resolve().parent

# REPO_DIR is defined as one directory above the package
REPO_DIR = BASE_DIR.parent

markdown_files_path = REPO_DIR / "markdowns"
datasets_path = REPO_DIR / "datasets"

DATASET = "CosmoPaperQA.parquet"

import google.auth

credentials, project = google.auth.default()


EMBEDDING_MODEL = "publishers/google/models/text-embedding-005"  # @param {type:"string", isTemplate: true}
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 100

display_name = "corpus"
assistant_name = "rag_agent"


TOP_K = 20
DISTANCE_THRESHOLD = 0.5

GEN_MODEL = "gemini-2.5-flash-preview-05-20"
OPENAI_GEN_MODEL = "gpt-4.1"


LOCATION="us-central1"
PROJECT = "camels-453517"
vertexai.init(project=PROJECT,location=LOCATION,credentials=credentials)
vertex_client = genai.Client(vertexai=True,project=PROJECT,location=LOCATION)


SCOPES = ['https://www.googleapis.com/auth/drive.file']
folder_id="1uoXS3wmCIU5v4iURI1Y9EgUxhGPaF4y7"




from openai import OpenAI
import os
openai_client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])




# The below pricing is for 1K tokens. Whenever there is an update in the LLM's pricing,
# Please convert it to 1K tokens and update in the below dictionary in the format: (input_token_price, output_token_price).
OAI_PRICE1K = {
    # https://openai.com/api/pricing/
    # o1
    "o1-preview-2024-09-12": (0.0015, 0.0060),
    "o1-preview": (0.0015, 0.0060),
    # 4.5 mini
    "gpt-4.5-preview-2025-02-27": (0.075, 0.15),
    "o1-mini-2024-09-12": (0.0003, 0.0012),
    "o1-mini": (0.0003, 0.0012),
    "o1": (0.0015, 0.0060),
    "o1-2024-12-17": (0.0015, 0.0060),
    # o1 pro
    "o1-pro": (0.15, 0.6),  # $150 / $600!
    "o1-pro-2025-03-19": (0.15, 0.6),
    # o3
    "o3": (0.0011, 0.0044),
    "o3-mini-2025-01-31": (0.0011, 0.0044),
    # gpt-4o
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-2024-05-13": (0.005, 0.015),
    "gpt-4o-2024-08-06": (0.0025, 0.01),
    "gpt-4o-2024-11-20": (0.0025, 0.01),
    # gpt-4o-mini
    "gpt-4o-mini": (0.000150, 0.000600),
    "gpt-4o-mini-2024-07-18": (0.000150, 0.000600),
    # gpt-4-turbo
    "gpt-4-turbo-2024-04-09": (0.01, 0.03),
    # gpt-4
    "gpt-4": (0.03, 0.06),
    "gpt-4-32k": (0.06, 0.12),
    # gpt-4.1
    "gpt-4.1": (0.002, 0.008),
    "gpt-4.1-2025-04-14": (0.002, 0.008),
    # gpt-4.1 mini
    "gpt-4.1-mini": (0.0004, 0.0016),
    "gpt-4.1-mini-2025-04-14": (0.0004, 0.0016),
    # gpt-4.1 nano
    "gpt-4.1-nano": (0.0001, 0.0004),
    "gpt-4.1-nano-2025-04-14": (0.0001, 0.0004),
    # gpt-3.5 turbo
    "gpt-3.5-turbo": (0.0005, 0.0015),  # default is 0125
    "gpt-3.5-turbo-0125": (0.0005, 0.0015),  # 16k
    "gpt-3.5-turbo-instruct": (0.0015, 0.002),
    # base model
    "davinci-002": 0.002,
    "babbage-002": 0.0004,
    # old model
    "gpt-4-0125-preview": (0.01, 0.03),
    "gpt-4-1106-preview": (0.01, 0.03),
    "gpt-4-1106-vision-preview": (0.01, 0.03),  # TODO: support vision pricing of images
    "gpt-3.5-turbo-1106": (0.001, 0.002),
    "gpt-3.5-turbo-0613": (0.0015, 0.002),
    # "gpt-3.5-turbo-16k": (0.003, 0.004),
    "gpt-3.5-turbo-16k-0613": (0.003, 0.004),
    "gpt-3.5-turbo-0301": (0.0015, 0.002),
    "text-ada-001": 0.0004,
    "text-babbage-001": 0.0005,
    "text-curie-001": 0.002,
    "code-cushman-001": 0.024,
    "code-davinci-002": 0.1,
    "text-davinci-002": 0.02,
    "text-davinci-003": 0.02,
    "gpt-4-0314": (0.03, 0.06),  # deprecate in Sep
    "gpt-4-32k-0314": (0.06, 0.12),  # deprecate in Sep
    "gpt-4-0613": (0.03, 0.06),
    "gpt-4-32k-0613": (0.06, 0.12),
    "gpt-4-turbo-preview": (0.01, 0.03),
    # https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/#pricing
    "gpt-35-turbo": (0.0005, 0.0015),  # what's the default? using 0125 here.
    "gpt-35-turbo-0125": (0.0005, 0.0015),
    "gpt-35-turbo-instruct": (0.0015, 0.002),
    "gpt-35-turbo-1106": (0.001, 0.002),
    "gpt-35-turbo-0613": (0.0015, 0.002),
    "gpt-35-turbo-0301": (0.0015, 0.002),
    "gpt-35-turbo-16k": (0.003, 0.004),
    "gpt-35-turbo-16k-0613": (0.003, 0.004),
    # deepseek
    "deepseek-chat": (0.00027, 0.0011),
}



from pydantic import BaseModel, Field
from typing import List
from paperqa.settings import Settings, AnswerSettings, AgentSettings

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
OCR_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'txt_files')

class AnswerFormat(BaseModel):
    answer: str = Field(
        description="The answer to the question using the given files only. Must be concise. At most 2 sentences."
    )
    sources: List[str] = Field(
        description=(
            "A list of source names used to formulate the answer. "
            "If possible, include page number, equation number, table number, section number, etc."
        )
    )


paperqa2_settings = Settings(
        llm="gpt-4o-mini",
        llm_config={
            "model_list": [
                {
                    "model_name": "gpt-4o-mini",
                    "litellm_params": {
                        "model": "gpt-4o-mini",
                        "temperature": 0.5,
                        "max_tokens": 4096,
                    },
                }
            ]
        },
        summary_llm="gpt-4o-mini",
        summary_llm_config={
            "rate_limit": {"gpt-4o-mini": "30000 per 1 minute"},
        },
        answer=AnswerSettings(
            evidence_k=30,
            answer_max_sources=15,
            evidence_skip_summary=False
        ),
        agent=AgentSettings(
            agent_llm="gpt-4o-mini",
            agent_llm_config={
                "rate_limit": {"gpt-4o-mini": "30000 per 1 minute"},
            }
        ),
        embedding="text-embedding-3-small",
        temperature=0.5,
        paper_directory=OCR_OUTPUT_DIR
    )

index_settings = Settings(
                paper_directory=OCR_OUTPUT_DIR,
                agent={"index": {
                    "sync_with_paper_directory": True,
                    "recurse_subdirectories": True
                }}
            )