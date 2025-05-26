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


from .config import (vertex_client,
                     credentials, 
                     EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
                     TOP_K, DISTANCE_THRESHOLD,
                     GEN_MODEL,
                     markdown_files_path,
                     SCOPES,
                     display_name,
                     folder_id)



class SciRag:
    def __init__(self, 
                 client = vertex_client,
                 credentials = credentials,
                 markdown_files_path = markdown_files_path,
                 corpus_name = display_name,
                 gen_model = GEN_MODEL,
                 ):
        self.credentials = credentials
        self.markdown_files_path = markdown_files_path
        self.drive_service = None
        self.client = client
        self.corpus_name = corpus_name
        self.gen_model = gen_model
        self.rag_prompt = rf"""
You are a retrieval agent. 
You must add precise source from where you got the answer.
Your answer should be in markdown format with the following structure: 

**Answer**:

{{answer}}

**Sources**:

{{sources}}

You must search your knowledge base calling your tool. The sources must be from the retrieval only.
You must report the source names in the sources field, if possible, the page number, equation number, table number, section number, etc.

"""
        self.enhanced_query = lambda query: (
rf"""
Question: {query}
"""
        )

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
    
    


    def create_vector_db(self, folder_id = folder_id):
        pass


    def get_chunks(self, query: str):
        pass
    
    def delete_vector_db(self):
        pass


    def get_response(self, query: str):
        pass


        

