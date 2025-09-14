# Core SciRAG components (always available)
from .scirag import SciRag
from .dataset import SciRagDataSet
from .config import REPO_DIR, TOP_K, DISTANCE_THRESHOLD, OAI_PRICE1K

# Enhanced SciRAG components
try:
    from .scirag_enhanced import SciRagEnhanced
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# Provider-specific components (conditional imports)
try:
    from .scirag_openai import SciRagOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from .scirag_vertexai import SciRagVertexAI
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False

try:
    from .scirag_paperqa2 import SciRagPaperQA2
    PAPERQA_AVAILABLE = True
except ImportError:
    PAPERQA_AVAILABLE = False

try:
    from .scirag_hybrid import SciRagHybrid
    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False

try:
    from .ocr import MistralOCRProcessor
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from .scirag_perplexity import PerplexityAgent
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False

try:
    from .scirag_gemini import GeminiGroundedAgent
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from .scirag_evaluator import SingleRAGEvaluationSystem, GeminiEvaluator
    EVALUATOR_AVAILABLE = True
except ImportError:
    EVALUATOR_AVAILABLE = False

# Build __all__ dynamically based on available components
__all__ = [
    'SciRag',
    'SciRagDataSet',
    'REPO_DIR',
    'TOP_K',
    'DISTANCE_THRESHOLD',
    'OAI_PRICE1K']

if ENHANCED_AVAILABLE:
    __all__.append('SciRagEnhanced')

if OPENAI_AVAILABLE:
    __all__.append('SciRagOpenAI')

if VERTEXAI_AVAILABLE:
    __all__.append('SciRagVertexAI')

if PAPERQA_AVAILABLE:
    __all__.append('SciRagPaperQA2')

if HYBRID_AVAILABLE:
    __all__.append('SciRagHybrid')

if OCR_AVAILABLE:
    __all__.append('MistralOCRProcessor')

if PERPLEXITY_AVAILABLE:
    __all__.append('PerplexityAgent')

if GEMINI_AVAILABLE:
    __all__.append('GeminiGroundedAgent')

if EVALUATOR_AVAILABLE:
    __all__.extend(['SingleRAGEvaluationSystem', 'GeminiEvaluator'])
