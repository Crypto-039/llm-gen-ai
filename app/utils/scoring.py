# Multi-factor patch scoring system
from typing import Dict, Any

class PatchScorer:
    def calculate_composite_score(
        self, 
        feasibility: float, 
        safety: float, 
        complexity: int, 
        context: Dict[str, Any]
    ) -> float:
        """Calculate composite score for patch ranking"""
        
        # NOVEL: Multi-factor scoring algorithm
        base_score = (feasibility * 0.4) + (safety * 0.4)
        complexity_penalty = max(0, (complexity - 5) * 0.05)
        context_bonus = self._calculate_context_bonus(context)
        
        final_score = base_score - complexity_penalty + context_bonus
        return max(0.0, min(10.0, final_score))
    
    def _calculate_context_bonus(self, context: Dict[str, Any]) -> float:
        """Calculate bonus based on context factors"""
        bonus = 0.0
        
        if context.get("urgency") == "high":
            bonus += 0.5
        if context.get("has_tests"):
            bonus += 0.3
        if context.get("peer_reviewed"):
            bonus += 0.2
            
        return bonus
    
    def validate_execution_result(self, result: Dict[str, Any]) -> float:
        """Validate execution result and return confidence score"""
        
        if not result.get("success"):
            return 0.0
        
        test_score = 0.4 if result.get("test_results", {}).get("return_code") == 0 else 0.0
        perf_score = result.get("performance_delta", 0) * 0.3
        safety_score = 0.3  # Would be calculated based on security checks
        
        return test_score + perf_score + safety_score
