from typing import List
from typing import Any, Optional, Union
# from IPython.display import display, Markdown
import asyncio
import time
import os
import re
import json
import pandas as pd

import shutil
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


from google.genai.types import (
    GenerateContentConfig,
    Retrieval,
    Tool,
    VertexRagStore,
    VertexRagStoreRagResource,
)

from vertexai import rag


from .config import (openai_client,
                     credentials, 
                     CHUNK_SIZE, CHUNK_OVERLAP,
                     TOP_K, DISTANCE_THRESHOLD,
                     OPENAI_GEN_MODEL,
                     TEMPERATURE,
                     display_name,
                     folder_id,
                     markdown_files_path,
                     OAI_PRICE1K,
                     AnswerFormat,
                     assistant_name)

from .scirag import SciRag

class SciRagOpenAI(SciRag):
    def __init__(self, 
                 client = openai_client,
                 credentials = credentials,
                 markdown_files_path = markdown_files_path,
                 corpus_name = display_name,
                 gen_model = OPENAI_GEN_MODEL,
                 ):
        super().__init__(client, credentials, markdown_files_path, corpus_name, gen_model)





        print("Listing RAG Corpora:")
        vector_stores = self.client.vector_stores.list()

        for vs in vector_stores:
            if vs.name == self.corpus_name:
                print(f"--- Corpus: {vs.name} ---")
                self.rag_corpus = vs


                self.rag_assistant = self.client.beta.assistants.create(
                    name=assistant_name,
                    instructions=self.rag_prompt,
                    tools=[
                                        {"type": "file_search",
                                            "file_search":{
                                                'max_num_results': TOP_K,
                                                "ranking_options": {
                                                    "ranker": "auto",
                                                    "score_threshold": DISTANCE_THRESHOLD
                                                }
                                            }
                                        }
                                    ],
                                    tool_resources={"file_search": {"vector_store_ids":[self.rag_corpus.id]}},
                                    model=self.gen_model, 
                                    temperature = TEMPERATURE,
                                    top_p = 0.2,
                                    response_format= {
                                        "type": "json_schema",
                                        "json_schema": {
                                            "name": "answer",
                                            "schema": AnswerFormat.model_json_schema()
                                        },
                                    }
                                )




        

        
    def create_vector_db(self, folder_id = folder_id):

        chunking_strategy =  {
                "type": "static",
                "static": {
                    "max_chunk_size_tokens": CHUNK_SIZE, # reduce size to ensure better context integrity
                    "chunk_overlap_tokens": CHUNK_OVERLAP # increase overlap to maintain context across chunks
                }}

        vector_store = self.client.vector_stores.create(name=self.corpus_name, chunking_strategy=chunking_strategy)
        self.rag_corpus = vector_store

        # Get all local .md files
        file_paths = [
            os.path.join(markdown_files_path, f)
            for f in os.listdir(markdown_files_path)
            if f.endswith('.md')
        ]
        if not file_paths:
            print("No markdown files found.")
            return

        print(f"Uploading {len(file_paths)} markdown files to OpenAI vector store...")

        # Open files in binary mode
        files = [open(path, "rb") for path in file_paths]
        try:
            # Upload and poll the file batch
            response = self.client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=self.rag_corpus.id,
                files=files,
            )
            print("Upload complete. Status:", response.status)
        finally:
            for f in files:
                f.close()



    def delete_vector_db(self):
        # List all vector stores
        vector_stores = self.client.vector_stores.list()
        deleted_ids = []
        for vs in vector_stores:
            # Depending on the API, it might be vs["name"] or vs.name
            try:
                if (getattr(vs, "name", None) or vs.get("name")) == self.corpus_name:
                    vs_id = getattr(vs, "id", None) or vs.get("id")
                    if vs_id:
                        self.client.vector_stores.delete(vs_id)
                        deleted_ids.append(vs_id)
            except Exception as e:
                continue
        return deleted_ids


    def delete_assistant_by_name(self, assistant_name=assistant_name):
        # List all assistants
        assistants = self.client.beta.assistants.list()
        deleted_ids = []
        for a in assistants:
            # Some clients use attribute access, some use dict-style
            try:
                name = getattr(a, "name", None) or a.get("name")
                if name == assistant_name:
                    a_id = getattr(a, "id", None) or a.get("id")
                    if a_id:
                        self.client.beta.assistants.delete(a_id)
                        deleted_ids.append(a_id)
            except Exception as e:
                continue
        return deleted_ids
    




    def _wait_for_run(self,run_id: str, thread_id: str) -> Any:
        in_progress = True
        while in_progress:
            run = self.client.beta.threads.runs.retrieve(run_id, thread_id=thread_id)
            in_progress = run.status in ("in_progress", "queued")
            if in_progress:
                time.sleep(0.1)
        return run


    def _format_assistant_message(self, message_content):
        """Formats the assistant's message to include annotations and citations."""
        annotations = message_content.annotations
        citations = []

        # Iterate over the annotations and add footnotes
        for index, annotation in enumerate(annotations):
            # Replace the text with a footnote
            message_content.value = message_content.value.replace(annotation.text, f" [{index}]")

            # Gather citations based on annotation attributes
            if file_citation := getattr(annotation, "file_citation", None):
                try:
                    cited_file = self.client.files.retrieve(file_citation.file_id)
                    # print(cited_file)
                    # citations.append(f"[{index}] {cited_file.filename}: {file_citation.quote}")
                    citations.append(f"[{index}] {cited_file.filename}")
                except Exception as e:
                    print(f"Error retrieving file citation: {e}")
            elif file_path := getattr(annotation, "file_path", None):
                try:
                    cited_file = self.client.files.retrieve(file_path.file_id)
                    citations.append(f"[{index}] Click <here> to download {cited_file.filename}")
                except Exception as e:
                    print(f"Error retrieving file citation: {e}")
                # Note: File download functionality not implemented above for brevity

        # Add footnotes to the end of the message before displaying to user
        # message_content.value += "\n" + "\n".join(citations)
        return message_content.value



    def format_assistant_json_response(self, messages):
        """
        Accepts a list of message dicts (as you have).
        Formats the assistant's answer and sources nicely.
        """
        outputs = []
        for msg in messages:
            if msg.get("role") == "assistant":
                raw_content = msg.get("content", "").strip()
                # Sometimes there is a trailing newline, remove it.
                try:
                    parsed = json.loads(raw_content)
                    answer = parsed.get("answer") or parsed.get("Answer") or ""
                    sources = parsed.get("sources") or parsed.get("Sources") or []
                    # If sources is a single string in a list, flatten
                    if isinstance(sources, list) and len(sources) == 1 and isinstance(sources[0], str):
                        sources_str = sources[0]
                    elif isinstance(sources, list):
                        sources_str = ", ".join(sources)
                    else:
                        sources_str = str(sources)
                    # Format as markdown
                    outputs.append(f"""**Answer**:

{answer}

**Sources**:

{sources_str}
""")
                except Exception as e:
                    outputs.append(f"Could not parse content for message: {raw_content}...\nError: {e}")
        return "\n---\n".join(outputs)



        
    def _get_run_response(self, thread, run):
        while True:
            run = self._wait_for_run(run.id, thread.id)
            if run.status == "completed":
                response_messages = self.client.beta.threads.messages.list(thread.id, order="asc")

                # register cost 
                prompt_tokens = run.usage.prompt_tokens
                completion_tokens = run.usage.completion_tokens
                total_tokens = run.usage.total_tokens

                cost = get_cost(run)
                tokens_dict = {
                    "model": run.model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "cost": cost
                }
                print_usage_summary(tokens_dict, self.cost_dict)




                new_messages = []
                for msg in response_messages:
                    if msg.run_id == run.id:
                        for content in msg.content:
                            if content.type == "text":
                                # Remove numerical references from the content
                                cleaned_content = remove_numerical_references(self._format_assistant_message(content.text))
                                new_messages.append(
                                    {"role": msg.role, 
                                    "content": cleaned_content}
                                )
                return self.format_assistant_json_response(new_messages)



    def get_response(self, query: str):
        thread = self.client.beta.threads.create(
                messages=[],
            )

        parsed = self.client.beta.threads.messages.create(
                        thread_id=thread.id,
                        content=self.enhanced_query(query),
                        role='user',
                    )


        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.rag_assistant.id,
            # pass the latest system message as instructions
            instructions=self.rag_prompt,
            tool_choice={"type": "file_search", "function": {"name": "file_search"}}
        )

        return self._get_run_response(thread, run)

def remove_numerical_references(text):
    # Remove numerical references of format [0], [1], etc.
    cleaned_text = re.sub(r'\[\d+\]', '', text)
    return cleaned_text

def get_cost(run):
    """Calculate the cost of the run."""
    model = run.model
    if model not in OAI_PRICE1K:
        # log warning that the model is not found
        print(
            f'Model {model} is not found. The cost will be 0. In your config_list, add field {{"price" : [prompt_price_per_1k, completion_token_price_per_1k]}} for customized pricing.'
        )
        return 0

    n_input_tokens = run.usage.prompt_tokens if run.usage is not None else 0  # type: ignore [union-attr]
    n_output_tokens = run.usage.completion_tokens if run.usage is not None else 0  # type: ignore [union-attr]
    if n_output_tokens is None:
        n_output_tokens = 0
    tmp_price1K = OAI_PRICE1K[model]
    # First value is input token rate, second value is output token rate
    if isinstance(tmp_price1K, tuple):
        return (tmp_price1K[0] * n_input_tokens + tmp_price1K[1] * n_output_tokens) / 1000  # type: ignore [no-any-return]
    return tmp_price1K * (n_input_tokens + n_output_tokens) / 1000  # type: ignore [operator]



def print_usage_summary(tokens_dict, cost_dict):
    # Extracting values from the dictionary
    model = tokens_dict["model"]
    prompt_tokens = tokens_dict["prompt_tokens"]
    completion_tokens = tokens_dict["completion_tokens"]
    total_tokens = tokens_dict["total_tokens"]
    cost = tokens_dict["cost"]
    

    # Restructure tokens_dict to create a DataFrame
    df = pd.DataFrame([{
        "Model": model,
        "Cost": f"{cost:.5f}",
        "Prompt Tokens": prompt_tokens,
        "Completion Tokens": completion_tokens,
        "Total Tokens": total_tokens,
    }])

    # Update dictionary containing all costs
    cost_dict['Cost'].append(cost) 
    cost_dict['Prompt Tokens'].append(prompt_tokens)
    cost_dict['Completion Tokens'].append(completion_tokens)
    cost_dict['Total Tokens'].append(total_tokens)
