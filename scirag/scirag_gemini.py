from typing import List, Dict, Any
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

from .config import AnswerFormat
import json

from google.genai.types import (
    GenerateContentConfig,
    Retrieval,
    Tool,
    VertexRagStore,
    VertexRagStoreRagResource,
)

from vertexai import rag
import faiss
import pickle

import numpy as np


from .config import (vertex_client,
                     credentials, 
                     GEMINI_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
                     TOP_K, DISTANCE_THRESHOLD,
                     TEMPERATURE,
                     GEMINI_GEN_MODEL,
                     display_name,
                     folder_id,
                     markdown_files_path,
                     embeddings_path,
                     semantic_weight)

from .scirag import SciRag, DocumentChunk
from tqdm.notebook import tqdm

# Google Cloud imports
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from vertexai.generative_models import GenerativeModel
import google.generativeai as genai
import tiktoken


# LangChain imports for document processing and utilities
from langchain.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    CSVLoader,
    JSONLoader,
    UnstructuredWordDocumentLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.messages import BaseMessage
# Scikit-learn for TF-IDF
from sklearn.feature_extraction.text import TfidfVectorizer
import glob
import json
import time


class SciRagGeminiAI(SciRag):
    def __init__(self, 
                 client = vertex_client,
                 credentials = credentials,
                 markdown_files_path = markdown_files_path,
                 corpus_name = display_name,
                 gen_model = GEMINI_GEN_MODEL,
                 vector_db_backend="chromadb",#"faiss",   # <--- add this line
                 chroma_collection_name="sci_rag_chunks",
                 chroma_db_path=str(embeddings_path / "chromadb"),
                 n_chunks = None,
                 ):
        super().__init__(client, credentials, markdown_files_path, corpus_name, gen_model)

        self.vector_db_backend = vector_db_backend
        self.chroma_collection_name = chroma_collection_name
        self.chroma_db_path = chroma_db_path
        self.chromadb_built = False
        self.embedding_model = TextEmbeddingModel.from_pretrained(GEMINI_EMBEDDING_MODEL)


        self.docs = self.load_markdown_files()
        self.split_documents() ## create self.all_chunks

        self.rate_limit_seconds = 0.2
        self.max_tokens_per_minute = 200000

        self._token_bucket = 0
        self._bucket_start_time = 0
        self.embedding_dim = 758


        # TF-IDF for lexical search
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=10000,
            ngram_range=(1, 2)
        )

        self.n_chunks = n_chunks

        self.chunks_store = []
        self.chunk_id_to_index = {}

        self._get_texts()



        self.rag_prompt = rf"""
You are a helpful assistant. 
Your answer should be in markdown format with the following structure: 

**Answer**:

{{answer}}

**Sources**:

{{sources}}

The sources must be from the **Context** material provided in the *Context* section.
You must report the source names in the sources field, if possible, the page number, equation number, table number, section number, etc.

"""

        self.enhanced_query = lambda context, query: (
rf"""
*Question*: 
{query}

*Context*:
{context}
"""
        )

        self.create_vector_db()




    def store_to_chromadb(self):
        import chromadb
        from chromadb.config import Settings
        client = chromadb.PersistentClient(path=self.chroma_db_path, settings=Settings(allow_reset=True))
        collection = client.get_or_create_collection(
            name=self.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        ids = [m.get('chunk_id', f'chunk_{i}') for i, m in enumerate(self.all_metadata)]
        embeddings = self.embeddings.tolist() if isinstance(self.embeddings, np.ndarray) else self.embeddings
        documents = self.all_texts
        metadatas = self.all_metadata
        batch_size = 1000
        for start in range(0, len(ids), batch_size):
            collection.add(
                ids=ids[start:start+batch_size],
                embeddings=embeddings[start:start+batch_size],
                documents=documents[start:start+batch_size],
                metadatas=metadatas[start:start+batch_size],
            )
        print(f"Stored {len(ids)} chunks in ChromaDB collection '{self.chroma_collection_name}' at {self.chroma_db_path}")

    def load_chromadb_collection(self):
        import chromadb
        client = chromadb.PersistentClient(path=self.chroma_db_path)
        self.chroma_collection = client.get_collection(name=self.chroma_collection_name)

    def query_chromadb(self, query, n_results=5):
            
        self._embed_query(query)
        query_embedding = self.query_embedding[0]
        results = self.chroma_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        # Flatten results to match your semantic_search interface
        return {
            "chunks": results["documents"][0],
            "metadata": results["metadatas"][0],
            "similarities": [1 - d for d in results["distances"][0]]  # Chroma returns L2, invert if using cosine
        }


    def _count_tokens(self, text: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


    def _get_texts(self):
        print("Building contextual retrieval index...")

        all_original_texts = []
        all_metadata = []

        # Group chunks by document for contextualization
        doc_groups = {}
        for chunk in self.all_chunks[:self.n_chunks]:
            source = chunk.metadata.get('source_file', chunk.metadata.get('source', 'unknown'))
            if source not in doc_groups:
                doc_groups[source] = []
            doc_groups[source].append(chunk)

        chunk_counter = 0

        # Process each document group
        for source, doc_chunks in doc_groups.items():
            # print(f"Processing {len(doc_chunks)} chunks from {source}")
            
            # Reconstruct full document text for context
            full_doc_text = "\n\n".join([chunk.page_content for chunk in doc_chunks])
            
            # Contextualize each chunk
            for chunk in doc_chunks:
                # if self.verbose:
                # print(f" Processing chunk {chunk_counter + 1}")
                
                all_original_texts.append(chunk.page_content)
                all_metadata.append({
                    **chunk.metadata,
                    'chunk_id': f"chunk_{chunk_counter}",
                })
                
                chunk_counter += 1
        print(f"Processed {chunk_counter} chunks")
        self.all_metadata = all_metadata
        self.all_texts = all_original_texts

    def _build_tf_idf_index(self):
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.all_texts)
        self.tfidf_fitted = True


    def _embed_texts(self) -> np.ndarray:
        """Generate embeddings using Google's embedding model, with token-based rate limiting and robust 429 error handling, with progress bar."""

        embeddings = []

        texts = self.all_texts

        # Use tqdm notebook for progress bar
        for i, text in enumerate(tqdm(texts, desc="Embedding texts", unit="doc")):
            tokens = self._count_tokens(text)
            now = time.time()
            # Reset token bucket every minute
            if now - self._bucket_start_time > 60 or self._bucket_start_time == 0:
                # print(f"[TokenTracker] Resetting token bucket. Sent {self._token_bucket} tokens in the last minute.")
                self._token_bucket = 0
                self._bucket_start_time = now

            # If adding this text would exceed the quota, wait for the next minute
            if self._token_bucket + tokens > self.max_tokens_per_minute:
                sleep_time = 60 - (now - self._bucket_start_time)
                if sleep_time > 0:
                    print(f"[TokenTracker] Token quota reached ({self._token_bucket} tokens). Sleeping for {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                self._token_bucket = 0
                self._bucket_start_time = time.time()

            while True:
                try:
                    batch_embeddings = self.embedding_model.get_embeddings([text])
                    for emb in batch_embeddings:
                        embeddings.append(emb.values)
                    break  # Success, break out of retry loop
                except Exception as e:
                    if "429" in str(e):
                        print("[TokenTracker] 429 error: Quota exceeded. Sleeping for 60 seconds before retrying...")
                        time.sleep(60)
                        self._token_bucket = 0
                        self._bucket_start_time = time.time()
                    else:
                        print(f"Error generating embeddings for text {i}: {e}")
                        embeddings.append([0.0] * self.embedding_dim)
                        break

            self._token_bucket += tokens

            # Optional: tqdm.write prints above the progress bar
            # tqdm.write(f"[TokenTracker] Sent {tokens} tokens (total this minute: {self._token_bucket}/{self.max_tokens_per_minute})")
            time.sleep(self.rate_limit_seconds)  # Still respect per-request delay

        self.embeddings = np.array(embeddings, dtype=np.float32)
        np.save(embeddings_path/f'{GEMINI_EMBEDDING_MODEL}_embeddings.npy', embeddings)





    def _embed_query(self, query: str) -> np.ndarray:
        """Generate embeddings using Google's embedding model, with token-based rate limiting and robust 429 error handling, with progress bar."""

        embeddings = []

        texts = [query]

        # Use tqdm notebook for progress bar
        for i, text in enumerate(tqdm(texts, desc="Embedding texts", unit="doc")):
            tokens = self._count_tokens(text)
            now = time.time()
            # Reset token bucket every minute
            if now - self._bucket_start_time > 60 or self._bucket_start_time == 0:
                # print(f"[TokenTracker] Resetting token bucket. Sent {self._token_bucket} tokens in the last minute.")
                self._token_bucket = 0
                self._bucket_start_time = now

            # If adding this text would exceed the quota, wait for the next minute
            if self._token_bucket + tokens > self.max_tokens_per_minute:
                sleep_time = 60 - (now - self._bucket_start_time)
                if sleep_time > 0:
                    print(f"[TokenTracker] Token quota reached ({self._token_bucket} tokens). Sleeping for {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                self._token_bucket = 0
                self._bucket_start_time = time.time()

            while True:
                try:
                    batch_embeddings = self.embedding_model.get_embeddings([text])
                    for emb in batch_embeddings:
                        embeddings.append(emb.values)
                    break  # Success, break out of retry loop
                except Exception as e:
                    if "429" in str(e):
                        print("[TokenTracker] 429 error: Quota exceeded. Sleeping for 60 seconds before retrying...")
                        time.sleep(60)
                        self._token_bucket = 0
                        self._bucket_start_time = time.time()
                    else:
                        print(f"Error generating embeddings for text {i}: {e}")
                        embeddings.append([0.0] * self.embedding_dim)
                        break

            self._token_bucket += tokens

            # Optional: tqdm.write prints above the progress bar
            # tqdm.write(f"[TokenTracker] Sent {tokens} tokens (total this minute: {self._token_bucket}/{self.max_tokens_per_minute})")
            time.sleep(self.rate_limit_seconds)  # Still respect per-request delay

        self.query_embedding = np.array(embeddings, dtype=np.float32)




    def get_embeddings(self):
        self._embed_texts()



    def load_embeddings(self):
        try:
            self.embeddings = np.load(embeddings_path/f'{GEMINI_EMBEDDING_MODEL}_embeddings.npy').astype(np.float32)
        except FileNotFoundError:
            # print(f"Embeddings file not found. You must call get_embeddings() first...")
            raise FileNotFoundError(f"Embeddings file not found. You must call get_embeddings() first...")




    def _create_faiss_index(self, use_gpu: bool = False) -> faiss.Index:
        """Create and populate FAISS index."""
        d = self.embeddings.shape[1]
        
        if len(self.embeddings) > 1000:
            nlist = min(int(np.sqrt(len(self.embeddings))), 100)
            quantizer = faiss.IndexFlatIP(d)
            index = faiss.IndexIVFFlat(quantizer, d, nlist)
            print("Training FAISS index...")
            index.train(self.embeddings)
        else:
            index = faiss.IndexFlatIP(d)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(self.embeddings)
        
        print(f"Adding {len(self.embeddings)} vectors to FAISS index...")
        index.add(self.embeddings)
        # print(index)
        
        if use_gpu and faiss.get_num_gpus() > 0:
            print("Moving FAISS index to GPU...")
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 0, index)
        
        return index


    def create_vector_db(self):
        self.load_embeddings()
        if self.vector_db_backend == "faiss":
            self.faiss_index = self._create_faiss_index()
            self.index_built = True
            self._build_tf_idf_index()
            self.chunks_store = []
            for i in range(len(self.all_texts)):
                chunk_obj = DocumentChunk(
                    original_text=self.all_texts[i],
                    contextualized_text=None,
                    embedding=self.embeddings[i],
                    tfidf_vector=self.tfidf_matrix[i],
                    metadata=self.all_metadata[i],
                    chunk_id=self.all_metadata[i]['chunk_id']
                )
                self.chunks_store.append(chunk_obj)
                self.chunk_id_to_index[chunk_obj.chunk_id] = i
            print(f"FAISS index built successfully with {len(self.chunks_store)} chunks")
            self._save_index()
        elif self.vector_db_backend == "chromadb":
            try:
                self.load_chromadb_collection()
            except FileNotFoundError:
                self.store_to_chromadb()
                print(f"ChromaDB vector DB built successfully with {len(self.all_texts)} chunks")
                self.chromadb_built = True
        else:
            raise ValueError(f"Unknown vector_db_backend: {self.vector_db_backend}")




    def _save_index(self):
        """Save the index to disk."""
        if self.faiss_index is not None:
            faiss.write_index(self.faiss_index, str(embeddings_path/f'{GEMINI_EMBEDDING_MODEL}_faiss.index'))
        else:
            print("Index not built. Call create_vector_db method first.")
        
        index_state = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'tfidf_fitted': self.tfidf_fitted,
            'chunks_count': len(self.chunks_store),
            'embedding_dim': self.embedding_dim,
            'chunk_id_to_index': self.chunk_id_to_index,
            'index_built': self.index_built
        }
        
        with open(embeddings_path/f'{GEMINI_EMBEDDING_MODEL}_index_state.pkl', 'wb') as f:
            pickle.dump(index_state, f)
        
        # Save chunks metadata
        chunks_metadata = []
        for chunk in self.chunks_store:
            chunks_metadata.append({
                'original_text': chunk.original_text,
                'contextualized_text': chunk.contextualized_text,
                'metadata': chunk.metadata,
                'chunk_id': chunk.chunk_id
            })
        
        with open(embeddings_path/f'{GEMINI_EMBEDDING_MODEL}_chunks_metadata.json', 'w') as f:
            json.dump(chunks_metadata, f, indent=2)

    def semantic_search(self, query: str, n_results: int = 20) -> Dict[str, Any]:
        if self.vector_db_backend == "faiss":
            if not self.index_built:
                raise ValueError("Index not built. Call build_index_* method first.")
            self._embed_query(query)
            query_embedding = self.query_embedding
            faiss.normalize_L2(query_embedding)
            similarities, indices = self.faiss_index.search(query_embedding, n_results)
            results = {'chunks': [], 'metadata': [], 'similarities': similarities[0].tolist()}
            for idx in indices[0]:
                if idx != -1:
                    chunk = self.chunks_store[idx]
                    results['chunks'].append(chunk.original_text)
                    results['metadata'].append(chunk.metadata)
            return results
        elif self.vector_db_backend == "chromadb":
            return self.query_chromadb(query, n_results)
        else:
            raise ValueError(f"Unknown vector_db_backend: {self.vector_db_backend}")




    def lexical_search(self, query: str, n_results: int = 20) -> List[Dict]:
        """Perform lexical search using TF-IDF."""
        if not self.tfidf_fitted:
            raise ValueError("TF-IDF not fitted. Build index first.")
        
        query_vector = self.tfidf_vectorizer.transform([query])
        
        similarities = []
        for i, chunk in enumerate(self.chunks_store):
            similarity = (query_vector * chunk.tfidf_vector.T).toarray()[0][0]
            similarities.append((similarity, i))
        
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        results = []
        for similarity, idx in similarities[:n_results]:
            chunk = self.chunks_store[idx]
            results.append({
                'text': chunk.original_text,
                'metadata': chunk.metadata,
                'similarity': similarity
            })
        
        return results

    def hybrid_search(self, query: str, n_results: int = TOP_K, 
                     semantic_weight: float = semantic_weight) -> List[Dict]:
        """Combine semantic and lexical search."""
        semantic_results = self.semantic_search(query, n_results)
        # lexical_results = self.lexical_search(query, n_results * 2)
        
        combined_scores = {}
        
        # Add semantic scores
        for chunk, metadata, similarity in zip(
            semantic_results['chunks'],
            semantic_results['metadata'], 
            semantic_results['similarities']
        ):
            chunk_id = metadata['chunk_id']
            combined_scores[chunk_id] = {
                'semantic_score': similarity * semantic_weight,
                'lexical_score': 0,
                'text': chunk,
                'metadata': metadata
            }
        

        # Calculate final scores
        final_results = []
        for chunk_id, scores in combined_scores.items():
            final_score = scores['semantic_score'] + scores['lexical_score']
            final_results.append({
                'text': scores['text'],
                'metadata': scores['metadata'],
                'final_score': final_score,
                'semantic_score': scores['semantic_score'],
                'lexical_score': 0.,
            })
        
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        return final_results[:n_results]




    def get_chunks(self, query: str):
        pass
    
    def delete_vector_db(self):
        pass


    def get_response(self, query: str):
        contexts = self.hybrid_search(query)
        # Prepare context text
        context_pieces = []
        for i, ctx in enumerate(contexts, 1):
            source = ctx['metadata'].get('file_name', ctx['metadata'].get('file_name', 'Unknown'))
            context_pieces.append(f"[Context {i} - Source: {source}]\n{ctx['text']}\n")
        
        context_text = "\n".join(context_pieces)
        self.context_text = context_text
        content = self.enhanced_query(context_text, query)
        response = self.client.models.generate_content(
            model=self.gen_model,
            contents=content,
            config=GenerateContentConfig(#tools=[self.rag_retrieval_tool],
                                         temperature=TEMPERATURE,
                                         system_instruction=self.rag_prompt,
                                         # tool_config=tool_config,
                                         response_mime_type='application/json',
                                         response_schema=AnswerFormat,
                                         ),
        )
        return self.format_agent_output(response.text)
    

    def format_agent_output(self, response):
        parsed = json.loads(response)
        answer = parsed.get("answer") or parsed.get("Answer") or ""
        sources = parsed.get("sources") or parsed.get("Sources") or []
        if isinstance(sources, list):
            sources_str = ", ".join(sources)
        else:
            sources_str = str(sources)
        return f"""**Answer**:

{answer}

**Sources**:

{sources_str}
"""
