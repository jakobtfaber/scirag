from typing import List
# from IPython.display import display, Markdown
import asyncio
import time
import os
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


from .config import (REPO_DIR, client,
                     credentials, 
                     EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
                     TOP_K, DISTANCE_THRESHOLD,
                     GEN_MODEL)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class Scirag:
    def __init__(self, 
                 credentials = credentials,
                 markdown_files_path = REPO_DIR / "markdowns",
                 ):
        self.credentials = credentials
        self.markdown_files_path = markdown_files_path
        self.drive_service = None
        self.rag_retrieval_tool = None
        self.client = client


        print("Listing RAG Corpora:")

        corpora_found = False
        for corpus in rag.list_corpora():
            corpora_found = True
            print(f"--- Corpus: {corpus.display_name} ---")
            print(f"  Name (Resource Path): {corpus.name}")
            print(f"  Display Name: {corpus.display_name}")

            # Access other common attributes:
            # Use hasattr() to safely check if an attribute exists before trying to access it,
            # as some fields might not be present for all corpora or in all states.


            if hasattr(corpus, 'create_time') and corpus.create_time:
                # Directly use corpus.create_time (which is a DatetimeWithNanoseconds object
                # or similar datetime-compatible object) with strftime
                print(f"  Create Time: {corpus.create_time.strftime('%Y-%m-%d %H:%M:%S')}")

            if hasattr(corpus, 'update_time') and corpus.update_time:
                # Directly use corpus.update_time with strftime
                print(f"  Update Time: {corpus.update_time.strftime('%Y-%m-%d %H:%M:%S')}")

            if hasattr(corpus, 'state') and corpus.state:
                print(f"  State: {corpus.state}") # e.g., Corpus.State.ACTIVE, Corpus.State.CREATING


            # You can inspect the object's attributes further if needed
            # print(f"  Full object representation: {corpus}") # This can be very verbose

            self.rag_corpus = corpus

            self.rag_retrieval_tool = Tool(
                retrieval=Retrieval(
                    vertex_rag_store=VertexRagStore(
                        rag_resources=[
                            VertexRagStoreRagResource(
                                rag_corpus=self.rag_corpus.name  # Currently only 1 corpus is allowed.
                            )
                        ],
                        similarity_top_k=TOP_K,
                        vector_distance_threshold=DISTANCE_THRESHOLD,
                    )
                )
            )

            print("-" * 30)

        if not corpora_found:
            print("No RAG corpora found in your project/region.")

    def load_markdown_files(self):
        markdown_files = list(self.markdown_files_path.glob("*.md"))
        return markdown_files
    
    def _get_drive_service(self):
        """Initialize and return Google Drive service."""
        if not self.drive_service:
            creds = None
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        REPO_DIR / 'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.drive_service = build('drive', 'v3', credentials=creds)
        return self.drive_service

    def upload_to_drive(self, folder_id: str) -> List[str]:
        """
        Upload all markdown files to the specified Google Drive folder.
        
        Args:
            folder_id (str): The ID of the Google Drive folder to upload to
            
        Returns:
            List[str]: List of file IDs of uploaded files
        """
        service = self._get_drive_service()
        markdown_files = self.load_markdown_files()
        uploaded_file_ids = []

        for file_path in markdown_files:
            file_metadata = {
                'name': file_path.name,
                'parents': [folder_id],
                'mimeType': 'text/markdown'
            }
            
            media = MediaFileUpload(
                str(file_path),
                mimetype='text/markdown',
                resumable=True
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            uploaded_file_ids.append(file.get('id'))
            
        return uploaded_file_ids
    
    


    def create_vector_db(self, display_name: str, folder_id: str):

        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=rag.RagEmbeddingModelConfig(
                    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                        publisher_model=EMBEDDING_MODEL
                    )
                )
            ),
        )

        rag.import_files(
            # corpus_name=rag_corpus.name,
            corpus_name=rag_corpus.name,
            # https://drive.google.com/drive/u/0/folders/
            paths=[f"https://drive.google.com/drive/folders/{folder_id}"],
            # Optional
            transformation_config=rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            ),
        )

        self.rag_corpus = rag_corpus


    def get_chunks(self, query: str):
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=self.rag_corpus.name,
                    # Optional: supply IDs from `rag.list_files()`.
                    # rag_file_ids=["rag-file-1", "rag-file-2", ...],
                )
            ],
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=TOP_K,  # Optional
                filter=rag.Filter(
                    vector_distance_threshold=DISTANCE_THRESHOLD,  # Optional
                ),
            ),
                    text=query,
                )
        return response
    
    def delete_vector_db(self):
        rag.delete_corpus(name=self.rag_corpus.name)


    def get_response(self, query: str):
        enhanced_query = (
rf"""Answer the following question concisely, at most two sentences long. 
If the answer is a number, just provide the number. 
Question: {query}
You must add precise source from where you got the answer.
Your answer should be in markdown format with the following format: 

**Answer**:

{{answer}}

**Sources**:

{{sources}}

You must search your knowledge base calling your tool. The sources must be from the retrieval only.
You must report the source names in the sources field, if possible, the page number, equation number, table number, section number, etc.
            """
        )
        response = self.client.models.generate_content(
            model=GEN_MODEL,
            contents=enhanced_query,
            config=GenerateContentConfig(tools=[self.rag_retrieval_tool],temperature=0.0,),
        )
        return response


        

