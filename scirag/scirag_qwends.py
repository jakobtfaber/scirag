# from typing import List, Dict, Any, Optional
# import json
# import numpy as np
# from pathlib import Path
# import chromadb
# from chromadb.config import Settings
# import torch
# import torch.nn.functional as F
# from torch import Tensor
# from transformers import AutoTokenizer, AutoModel

# # OpenAI client for DeepSeek (OpenAI-compatible API)
# from openai import OpenAI

# from .scirag import SciRag, DocumentChunk
# from .config import (
#     TOP_K,
#     TEMPERATURE,
#     embeddings_path,
# )


# def last_token_pool(last_hidden_states: Tensor,
#                  attention_mask: Tensor) -> Tensor:
#     left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
#     if left_padding:
#         return last_hidden_states[:, -1]
#     else:
#         sequence_lengths = attention_mask.sum(dim=1) - 1
#         batch_size = last_hidden_states.shape[0]
#         return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


# def get_detailed_instruct(task_description: str, query: str) -> str:
#     return f'Instruct: {task_description}\nQuery: {query}'


# class QwenDeepSeekRag(SciRag):
#     """
#     Clean RAG system using:
#     - Qwen embeddings for retrieval (direct transformers implementation)
#     - DeepSeek R1 for generation  
#     - ChromaDB for vector storage
#     - Semantic search only
#     - Base SciRag DocumentChunk for preprocessing
#     """
    
#     def __init__(self,
#                  # DeepSeek configuration
#                  deepseek_api_key: str,
#                  deepseek_model: str = "deepseek-r1",
#                  deepseek_base_url: str = "https://api.deepseek.com",
                 
#                  # Qwen embedding configuration
#                  qwen_embedding_model: str = "Alibaba-NLP/gte-Qwen2-7B-instruct",
#                  max_length: int = 8192,
                 
#                  # ChromaDB configuration
#                  chroma_collection_name: str = "qwen_deepseek_rag",
#                  chroma_db_path: Optional[str] = None,
                 
#                  # Search configuration
#                  top_k: int = TOP_K,
                 
#                  # Base class parameters
#                  **kwargs):
        
#         # Initialize base class first
#         super().__init__(**kwargs)
        
#         # Store configuration
#         self.deepseek_model = deepseek_model
#         self.qwen_embedding_model = qwen_embedding_model
#         self.max_length = max_length
#         self.chroma_collection_name = chroma_collection_name
#         self.top_k = top_k
        
#         # Task description for embeddings
#         self.embedding_task = 'Given a web search query, retrieve relevant passages that answer the query'
        
#         # Set ChromaDB path
#         if chroma_db_path is None:
#             chroma_db_path = str(embeddings_path / "chromadb")
#         self.chroma_db_path = chroma_db_path
        
#         # Initialize DeepSeek client
#         self.deepseek_client = OpenAI(
#             api_key=deepseek_api_key,
#             base_url=deepseek_base_url
#         )
        
#         # Initialize Qwen embedding model
#         self._initialize_qwen_model()
        
#         # Initialize ChromaDB
#         self.chroma_collection = None
        
#         # Override prompts for JSON format
#         self._setup_prompts()
        
#         print("QwenDeepSeek RAG system initialized successfully!")
    
#     def _initialize_qwen_model(self):
#         """Initialize Qwen embedding model with direct transformers implementation."""
#         try:
#             # Determine the best device
#             if torch.backends.mps.is_available():
#                 self.device = torch.device("mps")
#                 print("🚀 Using MPS (Apple Silicon GPU) acceleration")
#             elif torch.cuda.is_available():
#                 self.device = torch.device("cuda")
#                 print("🚀 Using CUDA GPU acceleration")
#             else:
#                 self.device = torch.device("cpu")
#                 print("⚠️  Using CPU (no GPU acceleration available)")
            
#             print(f"Loading tokenizer: {self.qwen_embedding_model}")
#             self.tokenizer = AutoTokenizer.from_pretrained(
#                 self.qwen_embedding_model, 
#                 trust_remote_code=True
#             )
            
#             print(f"Loading model: {self.qwen_embedding_model}")
#             self.model = AutoModel.from_pretrained(
#                 self.qwen_embedding_model, 
#                 trust_remote_code=True
#             )
            
#             # Move model to device and set to evaluation mode
#             self.model = self.model.to(self.device)
#             self.model.eval()
#             print(f"Model moved to device: {self.device}")
            
#             # Get embedding dimension
#             test_embedding = self._encode_texts(["test"])
#             self.embedding_dim = test_embedding.shape[1]
#             print(f"Embedding dimension: {self.embedding_dim}")
            
#         except Exception as e:
#             print(f"Failed to load model: {e}")
#             raise
    
#     def _encode_texts(self, texts: List[str], is_query: bool = False) -> torch.Tensor:
#         """Encode texts using the Qwen model with proper instruction formatting."""
#         if is_query:
#             # Add instruction for queries
#             input_texts = [get_detailed_instruct(self.embedding_task, text) for text in texts]
#         else:
#             # No instruction needed for documents
#             input_texts = texts
        
#         # Tokenize the input texts
#         batch_dict = self.tokenizer(
#             input_texts, 
#             max_length=self.max_length, 
#             padding=True, 
#             truncation=True, 
#             return_tensors='pt'
#         )
        
#         # Move tensors to device
#         batch_dict = {k: v.to(self.device) for k, v in batch_dict.items()}
        
#         # Generate embeddings
#         with torch.no_grad():
#             outputs = self.model(**batch_dict)
#             embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
#             # Normalize embeddings
#             embeddings = F.normalize(embeddings, p=2, dim=1)
        
#         return embeddings
    
#     def _setup_prompts(self):
#         """Setup prompts for JSON format responses."""
#         self.rag_prompt = """You are a helpful assistant. Answer based on the provided context.
# You must respond in valid JSON format with the following structure:

# {
#   "answer": "your detailed answer here",
#   "sources": ["source1", "source2", "source3"]
# }

# The sources must be from the **Context** material provided.
# Include source names, page numbers, equation numbers, table numbers, section numbers when available.
# Ensure your response is valid JSON only."""

#         self.enhanced_query = lambda context, query: f"""Question: {query}

# Context:
# {context}

# Instructions: Based on the context provided above, answer the question in valid JSON format:
# {{
#   "answer": "your detailed answer here",
#   "sources": ["source1", "source2"]
# }}"""
    
#     def create_vector_db(self, folder_id=None):
#         """Create vector database from processed documents."""
#         print("Creating vector database...")
        
#         # 1. Load and process documents using base class
#         print("Loading markdown documents...")
#         self.docs = self.load_markdown_files()
        
#         print("Splitting documents into chunks...")
#         self.split_documents()
        
#         # 2. Convert to DocumentChunk objects (base class format)
#         print("Converting to DocumentChunk objects...")
#         self.document_chunks = self._create_document_chunks()
        
#         # 3. Generate embeddings
#         print("Generating embeddings...")
#         self._generate_embeddings()
        
#         # 4. Initialize ChromaDB and store vectors
#         print("Storing in ChromaDB...")
#         self._initialize_chromadb()
        
#         print(f"Vector database created with {len(self.document_chunks)} chunks")
#         return True
    
#     def _create_document_chunks(self) -> List[DocumentChunk]:
#         """Convert LangChain chunks to DocumentChunk objects."""
#         document_chunks = []
        
#         for i, chunk in enumerate(self.all_chunks):
#             doc_chunk = DocumentChunk(
#                 original_text=chunk.page_content,
#                 contextualized_text=chunk.page_content,  # No contextualization for now
#                 embedding=None,  # Will be filled later
#                 tfidf_vector=None,  # Not used in semantic-only search
#                 metadata={
#                     **chunk.metadata,
#                     'chunk_id': f"chunk_{i}",
#                 },
#                 chunk_id=f"chunk_{i}"
#             )
#             document_chunks.append(doc_chunk)
        
#         return document_chunks
    
#     def _generate_embeddings(self):
#         """Generate embeddings for all document chunks."""
#         texts = [chunk.original_text for chunk in self.document_chunks]
        
#         print(f"Generating embeddings for {len(texts)} chunks...")
        
#         # Generate embeddings in batches
#         batch_size = 8
#         all_embeddings = []
        
#         for i in range(0, len(texts), batch_size):
#             batch_texts = texts[i:i+batch_size]
            
#             try:
#                 # Generate embeddings for documents (no instruction needed)
#                 batch_embeddings = self._encode_texts(batch_texts, is_query=False)
                
#                 # Convert to numpy and add to list
#                 batch_embeddings_np = batch_embeddings.cpu().numpy()
#                 all_embeddings.extend(batch_embeddings_np)
                
#                 if (i // batch_size + 1) % 10 == 0:
#                     print(f"Processed {i + len(batch_texts)}/{len(texts)} chunks")
                
#             except Exception as e:
#                 print(f"Error generating embeddings for batch starting at {i}: {e}")
#                 # Fill with zero embeddings as fallback
#                 zero_embeddings = np.zeros((len(batch_texts), self.embedding_dim), dtype=np.float32)
#                 all_embeddings.extend(zero_embeddings)
        
#         # Store embeddings in DocumentChunk objects
#         for chunk, embedding in zip(self.document_chunks, all_embeddings):
#             chunk.embedding = np.array(embedding, dtype=np.float32)
        
#         print(f"Generated {len(all_embeddings)} embeddings")
    
#     def _initialize_chromadb(self):
#         """Initialize ChromaDB and store document chunks."""
#         # Ensure directory exists
#         chroma_path = Path(self.chroma_db_path)
#         chroma_path.mkdir(parents=True, exist_ok=True)
        
#         # Create ChromaDB client
#         client = chromadb.PersistentClient(
#             path=self.chroma_db_path,
#             settings=Settings(allow_reset=True, anonymized_telemetry=False)
#         )
        
#         # Generate unique collection name
#         model_name_clean = self.qwen_embedding_model.replace('/', '_').replace('-', '_')
#         collection_name = f"{self.chroma_collection_name}_{model_name_clean}"
        
#         try:
#             # Try to delete existing collection if it exists
#             try:
#                 client.delete_collection(name=collection_name)
#                 print(f"Deleted existing collection: {collection_name}")
#             except:
#                 pass
            
#             # Create new collection
#             self.chroma_collection = client.create_collection(
#                 name=collection_name,
#                 metadata={"hnsw:space": "cosine", "embedding_provider": "qwen"}
#             )
#             print(f"Created new ChromaDB collection: {collection_name}")
            
#             # Prepare data for ChromaDB
#             ids = [chunk.chunk_id for chunk in self.document_chunks]
#             embeddings = [chunk.embedding.tolist() for chunk in self.document_chunks]
#             documents = [chunk.original_text for chunk in self.document_chunks]
#             metadatas = [chunk.metadata for chunk in self.document_chunks]
            
#             # Add to ChromaDB in batches
#             batch_size = 1000
#             for start in range(0, len(ids), batch_size):
#                 end = min(start + batch_size, len(ids))
#                 self.chroma_collection.add(
#                     ids=ids[start:end],
#                     embeddings=embeddings[start:end],
#                     documents=documents[start:end],
#                     metadatas=metadatas[start:end],
#                 )
#                 print(f"Added batch {start//batch_size + 1}: {end - start} chunks")
            
#             print(f"Stored {len(ids)} chunks in ChromaDB")
            
#         except Exception as e:
#             print(f"Error initializing ChromaDB: {e}")
#             raise
    
#     def get_chunks(self, query: str) -> List[Dict]:
#         """Get relevant chunks using semantic search only."""
#         return self.semantic_search(query, n_results=self.top_k)
    
#     def semantic_search(self, query: str, n_results: int = None) -> List[Dict]:
#         """Perform semantic search using ChromaDB with proper query embedding."""
#         if self.chroma_collection is None:
#             raise ValueError("Vector database not initialized. Call create_vector_db() first.")
        
#         if n_results is None:
#             n_results = self.top_k
        
#         # Generate query embedding with instruction formatting
#         query_embedding = self._encode_texts([query], is_query=True)
#         query_embedding_np = query_embedding.cpu().numpy()[0]
        
#         # Search ChromaDB
#         results = self.chroma_collection.query(
#             query_embeddings=[query_embedding_np.tolist()],
#             n_results=n_results,
#             include=["documents", "metadatas", "distances"]
#         )
        
#         # Format results
#         search_results = []
#         for document, metadata, distance in zip(
#             results["documents"][0],
#             results["metadatas"][0], 
#             results["distances"][0]
#         ):
#             search_results.append({
#                 'text': document,
#                 'metadata': metadata,
#                 'similarity': 1 - distance,  # Convert distance to similarity
#                 'score': 1 - distance
#             })
        
#         return search_results
    
#     def get_response(self, query: str) -> str:
#         """Get response for a query using semantic search and DeepSeek generation."""
#         # Get relevant contexts
#         contexts = self.semantic_search(query)
        
#         # Prepare context text
#         context_pieces = []
#         for i, ctx in enumerate(contexts, 1):
#             source = ctx['metadata'].get('file_name', 'Unknown')
#             context_pieces.append(f"[Context {i} - Source: {source}]\n{ctx['text']}\n")
        
#         context_text = "\n".join(context_pieces)
        
#         # Generate enhanced query
#         content = self.enhanced_query(context_text, query)
        
#         # Generate response using DeepSeek
#         response_text = self._generate_response_deepseek(content)
        
#         # Format output
#         return self._format_agent_output(response_text)
    
#     def _generate_response_deepseek(self, content: str) -> str:
#         """Generate response using DeepSeek R1."""
#         try:
#             messages = [
#                 {"role": "system", "content": self.rag_prompt},
#                 {"role": "user", "content": content}
#             ]
            
#             response = self.deepseek_client.chat.completions.create(
#                 model=self.deepseek_model,
#                 messages=messages,
#                 temperature=TEMPERATURE,
#                 max_tokens=4000,
#                 response_format={"type": "json_object"}
#             )
            
#             return response.choices[0].message.content
            
#         except Exception as e:
#             print(f"Error generating response with DeepSeek: {e}")
#             return json.dumps({
#                 "answer": f"Error generating response: {str(e)}",
#                 "sources": []
#             })
    
#     def _format_agent_output(self, response: str) -> str:
#         """Format agent output with robust JSON parsing."""
#         try:
#             parsed = json.loads(response)
#             answer = parsed.get("answer", "")
#             sources = parsed.get("sources", [])
            
#             if isinstance(sources, list):
#                 sources_str = ", ".join(sources)
#             else:
#                 sources_str = str(sources)
                
#             return f"""**Answer**:

# {answer}

# **Sources**:

# {sources_str}"""
            
#         except json.JSONDecodeError as e:
#             print(f"JSON parsing failed: {e}")
#             print(f"Raw response: {response[:200]}...")
            
#             # Fallback: return raw response
#             return f"""**Answer**:

# {response}

# **Sources**:

# Unable to parse sources from response"""
    
#     def delete_vector_db(self):
#         """Delete the vector database."""
#         try:
#             import shutil
#             chroma_path = Path(self.chroma_db_path)
#             if chroma_path.exists():
#                 shutil.rmtree(chroma_path)
#                 print("Vector database deleted successfully.")
#             else:
#                 print("Vector database path does not exist.")
#         except Exception as e:
#             print(f"Error deleting vector database: {e}")
    
#     def get_model_info(self) -> Dict[str, Any]:
#         """Get information about the configured models."""
#         return {
#             "embedding_provider": "qwen_direct_transformers",
#             "embedding_model": self.qwen_embedding_model,
#             "embedding_dimension": self.embedding_dim,
#             "generation_provider": "deepseek",
#             "generation_model": self.deepseek_model,
#             "vector_db_backend": "chromadb",
#             "search_method": "semantic_only",
#             "total_chunks": len(self.document_chunks) if hasattr(self, 'document_chunks') else 0,
#             "top_k": self.top_k,
#             "max_length": self.max_length,
#             "embedding_task": self.embedding_task
#         }