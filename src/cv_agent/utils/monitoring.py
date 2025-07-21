import os
from typing import Dict, Any, Optional
import time
from langsmith import Client
from langsmith.run_helpers import traceable


class LangSmithMonitor:
    """LangSmith integration for monitoring and optimization."""
    
    def __init__(self, project_name: str = "cv-improvement-agent"):
        self.client = None
        self.project_name = project_name
        
        # Initialize LangSmith client if API key is available
        if os.getenv("LANGSMITH_API_KEY"):
            try:
                self.client = Client()
                self.enabled = True
            except Exception:
                self.enabled = False
        else:
            self.enabled = False
    
    @traceable(name="cv_processing_workflow")
    def trace_cv_processing(self, state: Dict[str, Any], node_name: str, 
                           result: Dict[str, Any]) -> Dict[str, Any]:
        """Trace CV processing workflow steps."""
        if not self.enabled:
            return result
        
        # Add tracing metadata
        metadata = {
            "node_name": node_name,
            "processing_time": result.get("processing_time"),
            "target_role": state.get("target_role"),
            "target_industry": state.get("target_industry"),
            "file_format": state.get("file_format"),
            "errors": len(result.get("processing_errors", []))
        }
        
        return result
    
    @traceable(name="cv_analysis_scoring")
    def trace_analysis_scoring(self, analysis_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Trace CV analysis and scoring."""
        if not self.enabled:
            return analysis_scores
        
        # Log scoring details for monitoring
        return analysis_scores
    
    @traceable(name="improvement_generation")
    def trace_improvement_generation(self, improvements: list, 
                                   target_role: Optional[str] = None) -> list:
        """Trace improvement generation process."""
        if not self.enabled:
            return improvements
        
        # Log improvement generation metrics
        improvement_types = {}
        for imp in improvements:
            imp_type = imp.get("type", "unknown")
            improvement_types[imp_type] = improvement_types.get(imp_type, 0) + 1
        
        return improvements
    
    def log_user_feedback(self, run_id: str, feedback: Dict[str, Any]):
        """Log user feedback for continuous improvement."""
        if not self.enabled or not self.client:
            return
        
        try:
            self.client.create_feedback(
                run_id=run_id,
                key="user_satisfaction",
                score=feedback.get("satisfaction_score", 0),
                comment=feedback.get("comment", "")
            )
        except Exception as e:
            print(f"Failed to log feedback: {e}")
    
    def get_performance_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Retrieve performance metrics from LangSmith."""
        if not self.enabled or not self.client:
            return {}
        
        try:
            # Get runs from the last N days
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                limit=100
            ))
            
            # Calculate metrics
            total_runs = len(runs)
            successful_runs = sum(1 for run in runs if not run.error)
            avg_processing_time = sum(
                (run.end_time - run.start_time).total_seconds() 
                for run in runs if run.end_time and run.start_time
            ) / total_runs if total_runs > 0 else 0
            
            return {
                "total_runs": total_runs,
                "success_rate": successful_runs / total_runs if total_runs > 0 else 0,
                "avg_processing_time_seconds": avg_processing_time,
                "error_rate": (total_runs - successful_runs) / total_runs if total_runs > 0 else 0
            }
            
        except Exception as e:
            print(f"Failed to retrieve metrics: {e}")
            return {}


# Decorators for easy tracing
def trace_cv_node(node_name: str):
    """Decorator for tracing CV processing nodes."""
    def decorator(func):
        @traceable(name=f"cv_node_{node_name}")
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # Add timing information
            if isinstance(result, dict):
                result["node_processing_time"] = end_time - start_time
            
            return result
        return wrapper
    return decorator


# Environment setup helper
def setup_langsmith_env():
    """Helper function to set up LangSmith environment variables."""
    
    env_vars = {
        "LANGSMITH_TRACING": "true",
        "LANGSMITH_PROJECT": "cv-improvement-agent"
    }
    
    missing_vars = []
    
    for var, default in env_vars.items():
        if not os.getenv(var):
            os.environ[var] = default
    
    # Check for required API key
    if not os.getenv("LANGSMITH_API_KEY"):
        missing_vars.append("LANGSMITH_API_KEY")
    
    if missing_vars:
        print(f"Warning: Missing LangSmith environment variables: {missing_vars}")
        print("LangSmith monitoring will be disabled.")
        return False
    
    return True