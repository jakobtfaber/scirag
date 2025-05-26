import csv
import re
import os
from typing import Any, Dict, List, Optional
import logging
import nest_asyncio
from paperqa import ask
from .config import paperqa2_settings, AnswerFormat,index_settings

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PaperQAOCR")

from paperqa import Docs
from paperqa.agents.search import get_directory_index
from paperqa.settings import Settings, AgentSettings

import threading



class PaperQAClient:
    """A singleton client for PaperQA2 that builds the index once and reuses it."""
    _instance = None
    _lock = threading.Lock()  # For thread safety

    #accept both pdf files and txt files
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings: Optional[Settings] = paperqa2_settings, PAPERS_DIR=None,index_settings=index_settings):
        if hasattr(self, '_initialized') and self._initialized:
            return  # Prevent re-initialization
        self._initialized = True
        self._index_built = False
        self.paper_directory = PAPERS_DIR
        if settings is None:
            self.settings = Settings(
                temperature=0.1,
                llm='gpt-4o-mini',
                paper_directory=self.paper_directory,
                summary_llm='gpt-4o-mini',

            )
        else:
            self.settings = settings
            self.paper_directory = settings.paper_directory
        if index_settings is None:
            self.index_settings = Settings(
                paper_directory=self.paper_directory,
                agent={"index": {
                    "sync_with_paper_directory": True,
                    "recurse_subdirectories": True
                }}
            )
        else:
            self.index_settings = index_settings

    def build_index(self):
        """wrapper for the async build_index_if_needed"""
        loop = nest_asyncio.get_event_loop()
        return loop.run_until_complete(self.build_index_if_needed())

    
    async def build_index_if_needed(self):
        """Build the document index if not already built ."""
        if not self._index_built:
            print("Building PaperQA2 document index (only happens once)...")
            #check if the files are in the right place
            if not os.path.exists(self.paper_directory):
                raise FileNotFoundError(f"Paper directory not found: {self.paper_directory}")
            
            built_index=await get_directory_index(settings=self.index_settings)
            index_files = await built_index.index_files
            self._index_built = True
        return built_index
    
    async def query_paperqa(self,query: str) -> str:
            """Query PaperQA2 for scientific evidence using OCR-processed documents"""
            nest_asyncio.apply()
            response = ask(query, settings=self.settings)
            answer_text=response.dict()['session']['answer']
            return AnswerFormat(answer=answer_text, sources=[])


    def ask(self, question: str) -> AnswerFormat:
        """Synchronous method to query PaperQA2, returns AnswerFormat."""
        loop = nest_asyncio.get_event_loop()
        return loop.run_until_complete(self.query_paperqa(question))
