"""
Mathematical processing module for Enhanced SciRAG.

This module provides mathematical content processing capabilities using RAGBook's
mathematical processing functions.
"""

import re
from typing import Dict, List, Any, Optional
from .enhanced_chunk import MathematicalContent


class MathematicalProcessor:
    """Mathematical content processor using RAGBook's math processing."""
    
    def __init__(self, enable_sympy: bool = True):
        """
        Initialize mathematical processor.
        
        Args:
            enable_sympy: Whether to enable SymPy processing
        """
        self.enable_sympy = enable_sympy
        self._sympy_available = self._check_sympy_availability()
    
    def _check_sympy_availability(self) -> bool:
        """Check if SymPy is available."""
        try:
            import sympy
            return True
        except ImportError:
            return False
    
    def process_equation(self, equation_tex: str) -> Dict[str, Any]:
        """
        Process a mathematical equation.
        
        Args:
            equation_tex: LaTeX equation string
            
        Returns:
            Dictionary containing processed mathematical content
        """
        if not equation_tex:
            return self._create_empty_result()
        
        try:
            # Basic LaTeX normalization
            math_norm = self._normalize_latex(equation_tex)
            
            # Tokenize the normalized equation
            math_tokens = self._tokenize_equation(math_norm)
            
            # Generate k-grams
            math_kgrams = self._generate_kgrams(math_tokens)
            
            # Create result dictionary
            result = {
                'equation_tex': equation_tex,
                'math_norm': math_norm,
                'math_tokens': math_tokens,
                'math_kgrams': math_kgrams,
                'complexity_score': self._calculate_complexity(equation_tex),
                'equation_type': self._classify_equation_type(equation_tex)
            }
            
            # Add SymPy processing if available
            if self.enable_sympy and self._sympy_available:
                canonical = self._canonicalize_equation(equation_tex)
                if canonical:
                    result['math_canonical'] = canonical
            
            return result
            
        except Exception as e:
            # Return fallback result
            return self._create_fallback_result(equation_tex, str(e))
    
    def _normalize_latex(self, equation_tex: str) -> str:
        """Normalize LaTeX equation."""
        if not equation_tex:
            return ""
        
        # Basic normalization
        normalized = equation_tex.strip()
        
        # Remove common LaTeX commands
        normalized = re.sub(r'\\begin\{equation\}', '', normalized)
        normalized = re.sub(r'\\end\{equation\}', '', normalized)
        normalized = re.sub(r'\\begin\{align\}', '', normalized)
        normalized = re.sub(r'\\end\{align\}', '', normalized)
        normalized = re.sub(r'\\begin\{eqnarray\}', '', normalized)
        normalized = re.sub(r'\\end\{eqnarray\}', '', normalized)
        
        # Replace common LaTeX symbols
        replacements = {
            r'\\frac\{([^}]+)\}\{([^}]+)\}': r'(\1)/(\2)',
            r'\\sqrt\{([^}]+)\}': r'sqrt(\1)',
            r'\\sum_\{([^}]+)\}\^\{([^}]+)\}': r'sum(\1 to \2)',
            r'\\int_\{([^}]+)\}\^\{([^}]+)\}': r'int(\1 to \2)',
            r'\\alpha': 'alpha',
            r'\\beta': 'beta',
            r'\\gamma': 'gamma',
            r'\\delta': 'delta',
            r'\\epsilon': 'epsilon',
            r'\\theta': 'theta',
            r'\\lambda': 'lambda',
            r'\\mu': 'mu',
            r'\\pi': 'pi',
            r'\\sigma': 'sigma',
            r'\\tau': 'tau',
            r'\\phi': 'phi',
            r'\\omega': 'omega'
        }
        
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized.strip()
    
    def _tokenize_equation(self, equation: str) -> List[str]:
        """Tokenize equation into individual components."""
        if not equation:
            return []
        
        # Split on common mathematical operators and symbols
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|[+\-*/=<>(){}[\]^_|\\]', equation)
        return tokens
    
    def _generate_kgrams(self, tokens: List[str], k: int = 3) -> List[str]:
        """Generate k-grams from tokens."""
        if not tokens or k <= 0:
            return []
        
        kgrams = []
        for i in range(len(tokens) - k + 1):
            kgram = ' '.join(tokens[i:i+k])
            kgrams.append(kgram)
        
        return kgrams
    
    def _calculate_complexity(self, equation_tex: str) -> float:
        """Calculate equation complexity score."""
        if not equation_tex:
            return 0.0
        
        # Simple complexity calculation
        complexity = 0.0
        
        # Count LaTeX commands
        latex_commands = len(re.findall(r'\\[a-zA-Z]+', equation_tex))
        complexity += latex_commands * 0.5
        
        # Count mathematical operators
        operators = len(re.findall(r'[+\-*/=<>^]', equation_tex))
        complexity += operators * 0.3
        
        # Count parentheses and brackets
        brackets = len(re.findall(r'[(){}[\]|]', equation_tex))
        complexity += brackets * 0.2
        
        # Count variables and numbers
        variables = len(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', equation_tex))
        numbers = len(re.findall(r'\d+\.?\d*', equation_tex))
        complexity += (variables + numbers) * 0.1
        
        return min(complexity, 10.0)  # Cap at 10.0
    
    def _classify_equation_type(self, equation_tex: str) -> str:
        """Classify the type of equation."""
        if not equation_tex:
            return "unknown"
        
        equation_lower = equation_tex.lower()
        
        # Check for common equation types
        if '\\frac' in equation_tex or '/' in equation_tex:
            return "fraction"
        elif '\\sum' in equation_tex or 'sum' in equation_lower:
            return "summation"
        elif '\\int' in equation_tex or 'int' in equation_lower:
            return "integral"
        elif '\\sqrt' in equation_tex or 'sqrt' in equation_lower:
            return "radical"
        elif '=' in equation_tex:
            return "equation"
        elif '\\in' in equation_tex or 'in' in equation_lower:
            return "set_membership"
        elif '\\subset' in equation_tex or 'subset' in equation_lower:
            return "set_relation"
        else:
            return "expression"
    
    def _canonicalize_equation(self, equation_tex: str) -> Optional[str]:
        """Canonicalize equation using SymPy."""
        if not self._sympy_available or not equation_tex:
            return None
        
        try:
            import sympy as sp
            
            # Parse the equation
            expr = sp.sympify(equation_tex)
            
            # Simplify the expression
            simplified = sp.simplify(expr)
            
            # Convert back to string
            return str(simplified)
            
        except Exception:
            return None
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result dictionary."""
        return {
            'equation_tex': '',
            'math_norm': '',
            'math_tokens': [],
            'math_kgrams': [],
            'complexity_score': 0.0,
            'equation_type': 'unknown'
        }
    
    def _create_fallback_result(self, equation_tex: str, error: str) -> Dict[str, Any]:
        """Create fallback result when processing fails."""
        return {
            'equation_tex': equation_tex,
            'math_norm': equation_tex,  # Use original as fallback
            'math_tokens': [equation_tex],  # Single token fallback
            'math_kgrams': [equation_tex],  # Single k-gram fallback
            'complexity_score': 0.0,
            'equation_type': 'unknown',
            'error': error
        }
    
    def create_mathematical_content(self, equation_tex: str) -> MathematicalContent:
        """
        Create MathematicalContent object from equation.
        
        Args:
            equation_tex: LaTeX equation string
            
        Returns:
            MathematicalContent object
        """
        result = self.process_equation(equation_tex)
        
        return MathematicalContent(
            equation_tex=result['equation_tex'],
            math_norm=result['math_norm'],
            math_tokens=result['math_tokens'],
            math_kgrams=result['math_kgrams'],
            complexity_score=result['complexity_score'],
            equation_type=result['equation_type'],
            math_canonical=result.get('math_canonical'),
            error=result.get('error')
        )