import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
import google.generativeai as genai

# Import the base SciRag class
from .scirag import SciRag
from .config import GEMINI_GEN_MODEL, AnswerFormat

@dataclass
class Paper:
    """Represents a cosmology paper in our knowledge base"""
    id: int
    title: str
    authors: str
    journal: str
    year: int
    citation: str
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None

class GeminiGroundedAgent(SciRag):
    """A Gemini-based agent for cosmology questions without Google Search grounding"""
    
    def __init__(self, 
                 client=None,
                 credentials=None, 
                 markdown_files_path=None,
                 corpus_name=None,
                 gen_model=GEMINI_GEN_MODEL,
                 **kwargs):
        # Initialize parent SciRag class
        super().__init__(
            client=client,
            credentials=credentials,
            markdown_files_path=markdown_files_path,
            corpus_name=corpus_name,
            gen_model=gen_model,
            **kwargs
        )
        
        # Core paper database - exactly as specified
        self.papers = [
            Paper(
                id=1,
                title="Planck 2018 results. VI. Cosmological parameters",
                authors="Planck Collaboration",
                journal="Astron.Astrophys.",
                year=2020,
                citation="Planck Collaboration, Planck 2018 results. VI. Cosmological parameters, Astron.Astrophys. 641 (2020) A6",
                doi="10.1051/0004-6361/201833910"
            ),
            Paper(
                id=2,
                title="The CAMELS project: Cosmology and Astrophysics with MachinE Learning Simulations",
                authors="Villaescusa-Navarro et al.",
                journal="Astrophys.J.",
                year=2021,
                citation="Villaescusa-Navarro et al., The CAMELS project: Cosmology and Astrophysics with MachinE Learning Simulations, Astrophys.J. 915 (2021) 71",
                arxiv_id="2010.00619"
            ),
            Paper(
                id=3,
                title="Cosmology with one galaxy?",
                authors="Villaescusa-Navarro et al.",
                journal="Astrophys.J.",
                year=2022,
                citation="Villaescusa-Navarro et al., Cosmology with one galaxy? Astrophys.J. 929 (2022) 2, 132",
                arxiv_id="2109.04484"
            ),
            Paper(
                id=4,
                title="A 2.4% Determination of the Local Value of the Hubble Constant",
                authors="Riess et al.",
                journal="Astrophys.J.",
                year=2016,
                citation="Riess et al., A 2.4% Determination of the Local Value of the Hubble Constant, Astrophys.J. 826 (2016) 1, 56",
                arxiv_id="1604.01424"
            ),
            Paper(
                id=5,
                title="The Atacama Cosmology Telescope: DR6 Constraints on Extended Cosmological Models",
                authors="Calabrese et al.",
                journal="arXiv",
                year=2025,
                citation="Calabrese et al., The Atacama Cosmology Telescope: DR6 Constraints on Extended Cosmological Models, arXiv:2503.14454v1 (2025)",
                arxiv_id="2503.14454"
            )
        ]
        
        # Create a mapping of citation numbers to paper info for sources
        self.citation_to_paper = {
            str(i): paper for i, paper in enumerate(self.papers, 1)
        }
        
        # Initialize Gemini client (without Google Search)
        self._initialize_gemini()
        
        # Override the rag_prompt with Gemini-specific prompt
        self.rag_prompt = self._create_gemini_prompt()
    
    def _initialize_gemini(self):
        """Initialize Gemini client with credentials (no Google Search)"""
        try:
            # Configure the generative AI client
            if self.credentials:
                genai.configure(credentials=self.credentials)
            else:
                # Fallback to API key if available
                api_key = os.getenv("GOOGLE_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                else:
                    raise ValueError("No Google credentials or API key found")
            
            # Create a simplified schema that Gemini can understand
            response_schema = {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The answer to the question using your knowledge of cosmology. Must be concise. At most 2 sentences."
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of relevant paper citations from the provided knowledge base that relate to the answer."
                    }
                },
                "required": ["answer", "sources"]
            }
            
            generation_config = {
                "temperature": 0.0,  # For consistent results
                "response_mime_type": "application/json",
                "response_schema": response_schema
            }
            
            # Initialize the model WITHOUT Google Search grounding
            self.model = genai.GenerativeModel(
                model_name=self.gen_model,
                generation_config=generation_config
            )
            
            ß
            
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            self.model = None
    
    def _create_gemini_prompt(self) -> str:
        """Create the specialized prompt for Gemini without Google Search"""
        paper_list = "\n".join([f"{i}. {paper.citation}" for i, paper in enumerate(self.papers, 1)])
        
        return f"""You are a scientific literature agent specializing in cosmology.

You have access to the following key cosmology papers in your knowledge base:
{paper_list}

Your task is to answer cosmology questions using your knowledge of these papers and general cosmology knowledge.

Instructions:
1. Answer the question based on your knowledge of cosmology and the listed papers
2. Provide a CONCISE answer in EXACTLY 1-2 sentences maximum
3. Add numerical references [1], [2], [3], etc. when citing the specific papers listed above
4. Focus ONLY on the most important quantitative results or key findings
5. Be precise, direct, and avoid any unnecessary elaboration

Paper reference guide:
[1] - Planck 2018 cosmological parameters
[2] - CAMELS machine learning cosmology simulations  
[3] - Single galaxy cosmology analysis
[4] - Local Hubble constant measurement (Riess et al.)
[5] - Atacama Cosmology Telescope DR6 results

CRITICAL: Your answer must be no more than 2 sentences total. Count your sentences carefully.

Your response must be in JSON format with exactly these fields:
- "answer": Your 1-2 sentence response with citations
- "sources": Array of paper citations [1]-[5] that are relevant to your answer

Example format:
{{
  "answer": "The Hubble constant from Planck is 67.4 ± 0.5 km/s/Mpc [1]. Local measurements give 73.04 ± 1.04 km/s/Mpc [4].",
  "sources": ["[1] Planck 2018 results", "[4] Riess et al. 2016 paper"]
}}
"""
    
    def get_response(self, query: str) -> str:
        """
        Override SciRag's get_response method to use Gemini without Google Search
        
        Args:
            query: The cosmology question to answer
            
        Returns:
            str: Formatted response with citations
        """
        
        if not self.model:
            raise RuntimeError("Gemini model not initialized. Check your credentials.")
        
        # Create the full prompt with the question
        full_prompt = f"{self.rag_prompt}\n\nQuestion: {query}"
        
        try:
            # Generate response using Gemini's knowledge only
            response = self.model.generate_content(full_prompt)
            
            # Extract the JSON response
            response_text = response.text
            
            # Parse and format the structured response
            final_response = self.parse_structured_response(response_text)
            
            return final_response
            
        except Exception as e:
            raise RuntimeError(f"Error generating Gemini response: {e}")
    
    def parse_structured_response(self, json_response: str) -> str:
        """Parse the structured JSON response and format it properly"""
        try:
            # Parse the JSON response
            parsed = json.loads(json_response)
            answer = parsed.get("answer", "")
            source_info = parsed.get("sources", [])
            
            # Debug: Print what we received
            print(f"Gemini parsed answer: {answer[:100]}...")
            print(f"Gemini parsed sources: {source_info}")
            
            # Format sources using our paper database
            formatted_sources = self._format_sources(source_info)
            
            return f"""**Answer**:

{answer}

**Sources**:

{formatted_sources}
"""
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini JSON response: {e}")
            print(f"Raw response: {json_response[:300]}...")
            
            # Fallback formatting
            return self._format_fallback_response(json_response)
    
    def _format_sources(self, source_info: List[str]) -> str:
        """Format sources using our paper database"""
        formatted_sources = []
        
        # Process provided sources
        for source in source_info:
            # Check if it's a paper citation [1]-[5]
            if any(f"[{i}]" in source for i in range(1, 6)):
                # Extract paper number and format with full info
                for i in range(1, 6):
                    if f"[{i}]" in source:
                        paper = self.citation_to_paper.get(str(i))
                        if paper:
                            formatted_sources.append(f"[{i}] {paper.title} - {paper.citation}")
                        break
            else:
                # Regular source description
                formatted_sources.append(source)
        
        return "\n".join(formatted_sources) if formatted_sources else "(No sources provided)"
    
    def _format_fallback_response(self, response_text: str) -> str:
        """Fallback formatting when JSON parsing fails"""
        print(f"Using Gemini fallback formatting for response: {response_text[:200]}...")
        
        # Try to extract paper citations from the response
        citations_found = []
        for i in range(1, 6):
            if f"[{i}]" in response_text:
                paper = self.citation_to_paper.get(str(i))
                if paper:
                    citations_found.append(f"[{i}] {paper.title} - {paper.citation}")
        
        sources_text = "\n".join(citations_found) if citations_found else "(Sources not found in standard format)"
        
        return f"""**Answer**:

{response_text}

**Sources**:

{sources_text}
"""