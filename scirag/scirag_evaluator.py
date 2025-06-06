import pandas as pd
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
from pydantic import BaseModel, Field
import autogen
from autogen import UserProxyAgent, AssistantAgent

class ResponseEvaluation(BaseModel):
    """Structured evaluation of a scientific response"""
    accuracy_score: int = Field(
        description="Factual accuracy score (0-100), where 100 means perfectly matching the ideal answer", 
        ge=0, le=100
    )

    rationale: str = Field(
        description="Brief explanation of the evaluation scores and comparison with ideal answer"
    )

class AIEvaluator:
    """AI Evaluator for RAG system performance using AG2 (AutoGen 2)"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.1):
        """Initialize the AI Evaluator"""
        self.model = model
        self.temperature = temperature
        self.ai_judge = self._create_ai_judge_agent()
        self.user_proxy = self._create_user_proxy_agent()
        
        # Disable Docker for AutoGen
        os.environ["AUTOGEN_USE_DOCKER"] = "False"
    
    def _create_ai_judge_agent(self) -> AssistantAgent:
        """Create and configure the AI judge agent"""
        system_message = """You are an expert scientific evaluator assessing the quality of scientific response against reference answers.

Your task is to evaluate responses using one critical criterion:

ACCURACY (0-100):
CRITICAL: Use ONLY these two scores for accuracy:
- 100: The answer contains the core correct factual content, concepts, and conclusions from the ideal answer
- 0: The answer is fundamentally wrong or contradicts the ideal answer

This is a BINARY evaluation - either the answer is essentially correct (100) or incorrect (0).
No partial credit or intermediate scores allowed.

EVALUATION GUIDELINES:
- Focus ONLY on whether the main scientific concepts and conclusions are correct
- Check that the core factual claims from the ideal answer are present in the generated answer
- Verify the overall conceptual direction and main conclusions align
- Additional correct information beyond the ideal answer is acceptable
- Only award 0 if the answer contradicts the ideal answer or gets the main concepts completely wrong
- Award 100 if the answer captures the essential correct scientific understanding

Provide your evaluation using the evaluate_response function with the numerical score and detailed rationale explaining why you chose 100 or 0."""
        
        return AssistantAgent(
            name="ai_judge",
            system_message=system_message,
            llm_config={
                "model": self.model,
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "evaluate_response",
                            "description": "Evaluate a scientific response",
                            "parameters": ResponseEvaluation.model_json_schema()
                        }
                    }
                ]
            }
        )
    
    def _create_user_proxy_agent(self) -> UserProxyAgent:
        """Create and configure the user proxy agent"""
        return UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda x: True,
            code_execution_config={"use_docker": False}
        )
    
    def evaluate_single_response(
        self,
        question: str,
        generated_answer: str,
        ideal_answer: str,
        sources: Optional[List[str]] = None,
        system_name: str = "RAG System"
    ) -> Dict[str, Any]:
        """Evaluate a single RAG response"""
        
        # Format sources for citation evaluation
        # sources_text = "\n".join(sources) if sources else "No sources provided"
        
        evaluation_task = f"""
Please evaluate this system's response against the ideal answer:

QUESTION: {question}

GENERATED ANSWER:
{generated_answer}

IDEAL ANSWER:
{ideal_answer}


Evaluate based on:
Accuracy (0-100): How factually correct is the answer compared to the ideal?

Use the evaluate_response function to provide your structured evaluation with detailed rationale.
"""
        
        try:
            # Reset agents for fresh evaluation
            self.user_proxy.reset()
            self.ai_judge.reset()
            
            # Initiate the evaluation chat
            self.user_proxy.initiate_chat(
                self.ai_judge,
                message=evaluation_task,
                max_turns=1
            )
            
            # Extract evaluation results
            last_message = self.ai_judge.last_message()
            evaluation_result = None
            
            if last_message and "tool_calls" in last_message:
                tool_calls = last_message["tool_calls"]
                if tool_calls and len(tool_calls) > 0:
                    tool_call = tool_calls[0]
                    if tool_call.get("function", {}).get("name") == "evaluate_response":
                        try:
                            evaluation_result = json.loads(tool_call["function"].get("arguments", "{}"))
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse evaluation: {e}")
                            return self._create_error_result(f"Parse error: {e}")
            
            # Fallback to old function_call format for compatibility
            elif last_message and "function_call" in last_message:
                function_call = last_message["function_call"]
                if function_call.get("name") == "evaluate_response":
                    try:
                        evaluation_result = json.loads(function_call.get("arguments", "{}"))
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse evaluation: {e}")
                        return self._create_error_result(f"Parse error: {e}")
            
            if evaluation_result:
                # Calculate composite score
                accuracy_score = evaluation_result.get('accuracy_score', 0)
            
                
                return {
                    "eval_accuracy_score": accuracy_score,
                    "eval_rationale": evaluation_result.get('rationale', ''),
                    "eval_successful": True,
                    "eval_error": None
                }
            else:
                return self._create_error_result("No evaluation result obtained")
                
        except Exception as e:
            return self._create_error_result(f"Evaluation failed: {str(e)}")
    
    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Create a standardized error result"""
        return {
            "eval_accuracy_score": None,
            "eval_rationale": None,
            "eval_successful": False,
            "eval_error": error_msg
        }


class SingleRAGEvaluationSystem:
    """Generic RAG Evaluation System for Individual DataFrames"""
    
    def __init__(self, evaluator_model: str = "gpt-4o", results_dir: str = "rag_evaluation_results"):
        """
        Initialize the Single RAG Evaluation System
        
        Args:
            evaluator_model: Model to use for AI evaluation
            results_dir: Directory to store evaluation results
        """
        self.evaluator = AIEvaluator(model=evaluator_model)
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
    
    def check_required_columns(self, df: pd.DataFrame) -> bool:
        """
        Check if the dataframe has the required columns for evaluation
        
        Args:
            df: DataFrame to check
            
        Returns:
            Boolean indicating if required columns are present
        """
        required_columns = ['question', 'ideal_solution']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"ERROR: Missing required columns: {missing_columns}")
            print(f"Available columns: {list(df.columns)}")
            return False
        
        print("All required columns found")
        return True
    
    def evaluate_single_dataframe(
        self, 
        df: pd.DataFrame, 
        system_name: str,
        max_evaluations: Optional[int] = None,
        save_results: bool = True
    ) -> pd.DataFrame:
        """
        Evaluate a single RAG system dataframe with known column structure
        
        Args:
            df: DataFrame containing RAG responses with columns:
                - question: The question text
                - answer: The generated answer
                - ideal_solution: The reference/ideal answer
                - sources: Source citations (optional)
                - success: Success flag (optional)
            system_name: Name of the RAG system for identification
            max_evaluations: Maximum number of evaluations to perform (None for all)
            save_results: Whether to save results to file
            
        Returns:
            DataFrame with evaluation results added
        """
        print(f"\n{'='*60}")
        print(f"EVALUATING: {system_name}")
        print(f"{'='*60}")
        
        # Check required columns
        if not self.check_required_columns(df):
            return df
        
        print(f"Available columns: {list(df.columns)}")
        
        # Create a copy of the dataframe
        eval_df = df.copy()
        
        # Filter to successful responses if success column exists
        if 'success' in df.columns:
            evaluable_rows = eval_df[eval_df['success'] == True]
            print(f"Filtering by success column: {len(evaluable_rows)} successful out of {len(eval_df)} total")
        else:
            # Check for non-null answers and ideals
            if 'answer' in df.columns:
                evaluable_rows = eval_df[
                    eval_df['ideal_solution'].notna() & 
                    eval_df['answer'].notna()
                ]
            else:
                evaluable_rows = eval_df[eval_df['ideal_solution'].notna()]
            print(f"No success column found, filtering by non-null values: {len(evaluable_rows)} evaluable rows")
        
        # Limit evaluations if requested
        if max_evaluations:
            evaluable_rows = evaluable_rows.head(max_evaluations)
            print(f"Limited to: {len(evaluable_rows)} evaluations")
        
        if len(evaluable_rows) == 0:
            print("No evaluable rows found. Returning original dataframe.")
            return eval_df
        
        # Initialize evaluation columns
        eval_columns = [
            "eval_accuracy_score", "eval_rationale", "eval_successful", "eval_error",
            "eval_processing_time"
        ]
        for col in eval_columns:
            eval_df[col] = None
        
        # Perform evaluations
        start_time = time.time()
        successful_evaluations = 0
        
        for idx, (_, row) in enumerate(evaluable_rows.iterrows(), 1):
            print(f"\nEvaluating {idx}/{len(evaluable_rows)} - Question ID: {row.get('question_id', idx)}")
            
            # Extract data directly using known column names
            question = row['question']
            ideal = row['ideal_solution']
            
            # Get answer - prefer 'answer' column, fallback to 'response'
            if 'answer' in df.columns and pd.notna(row['answer']):
                answer = row['answer']
            elif 'response' in df.columns and pd.notna(row['response']):
                answer = row['response']
            else:
                answer = ""
                print(f"    Warning: No answer found for question {idx}")
            
            # Skip if no answer available
            if not answer or answer.strip() == "":
                print(f"    ✗ Skipping - No answer available")
                continue
            
            # Perform evaluation
            eval_start_time = time.time()
            evaluation_result = self.evaluator.evaluate_single_response(
                question=question,
                generated_answer=answer,
                ideal_answer=ideal,
                system_name=system_name
            )
            eval_time = time.time() - eval_start_time
            evaluation_result['eval_processing_time'] = eval_time
            
            # Update dataframe with results
            row_idx = row.name  # Get the original index
            for key, value in evaluation_result.items():
                eval_df.at[row_idx, key] = value
            
            # Print progress
            if evaluation_result.get('eval_successful'):
                successful_evaluations += 1
                print( f"Accuracy:{evaluation_result['eval_accuracy_score']}")
                print(f"  Time: {eval_time:.2f}s")
            else:
                print(f"  ✗ Failed: {evaluation_result.get('eval_error', 'Unknown error')}")
        
        total_time = time.time() - start_time
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"EVALUATION COMPLETE: {system_name}")
        print(f"{'='*60}")
        print(f"Total evaluation time: {total_time:.2f} seconds")
        print(f"Successful evaluations: {successful_evaluations}/{len(evaluable_rows)}")
        print(f"Success rate: {successful_evaluations/len(evaluable_rows)*100:.1f}%")
        
        if successful_evaluations > 0:
            successful_evals = eval_df[eval_df['eval_successful'] == True]
            print(f"\nAverage Scores:")

            print(f"  Accuracy: {successful_evals['eval_accuracy_score'].mean():.2f}")
        
        # Save results if requested
        if save_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{system_name.replace(' ', '_').lower()}_evaluated_{timestamp}.csv"
            filepath = os.path.join(self.results_dir, filename)
            eval_df.to_csv(filepath, index=False)
            print(f"\nResults saved to: {filepath}")
        
        return eval_df
    
   
    
    def _save_individual_results(self, df: pd.DataFrame, system_name: str):
        """Save individual system results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{system_name.replace(' ', '_').lower()}_evaluated_{timestamp}.csv"
        filepath = os.path.join(self.results_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Saved results: {filepath}")



# Usage Examples - One by One Evaluation
# if __name__ == "__main__":
#     # Initialize the evaluation system once
#     rag_evaluator = SingleRAGEvaluationSystem(
#         evaluator_model="gpt-4o",
#         results_dir="individual_rag_evaluations"
#     )
    
#     # Example 1: Evaluate VertexAI system
#     print("Evaluating VertexAI RAG System...")
#     # vertexai_evaluated = rag_evaluator.evaluate_single_dataframe(
#     #     df=vertexai_df,
#     #     system_name="VertexAI_RAG",
#     #     max_evaluations=5  # Test with 5 questions first
#     # )
    
#     # Example 2: Evaluate OpenAI system with custom column mapping
#     print("\nEvaluating OpenAI RAG System...")
#     # custom_mapping = {
#     #     'question': 'query_text',  # If your column is named differently
#     #     'answer': 'response',
#     #     'ideal': 'reference_answer',
#     #     'sources': 'citations'
#     # }
#     # openai_evaluated = rag_evaluator.evaluate_single_dataframe(
#     #     df=openai_df,
#     #     system_name="OpenAI_RAG",
#     #     column_mapping=custom_mapping,
#     #     max_evaluations=None  # Evaluate all
#     # )
    
#     # Example 3: Just check what columns would be detected
#     # schema = rag_evaluator.detect_dataframe_schema(your_dataframe)
#     # print(f"Detected schema: {schema}")
    
#     print("Ready to evaluate your RAG systems one by one!")


