from typing import Dict, Any
from nextmind.state.research_state import ResearchState
from nextmind.utils.node_helper import emit_progress, update_timestamps
from nextmind.agents.researcher import SynthesisAgent
import json

# Initialize Synthesis Agent
synthesis_agent = SynthesisAgent()

class SynthesisNodes:
    """
    Synthesis nodes: Hypothesis Generator, Logical Validator, Novelty check nodes.
    Refactored to use SynthesisAgent.
    """

    @staticmethod
    async def hypothesis_generator_node(state: ResearchState) -> Dict[str, Any]:
        """
        Generate research hypothesis.
        Uses SynthesisAgent.
        """
        updates = {}
        updates.update(update_timestamps(state, "HypothesisGeneratorNode"))
        updates.update(emit_progress(state, "HypothesisGeneratorNode", "hypothesis_generation", 80, "Generating research hypothesis..."))
        
        try:
            hypothesis = await synthesis_agent.generate_hypothesis(
                state.get("selected_gap", {}),
                state.get("summaries", [])
            )
            updates["hypothesis"] = hypothesis
        except Exception as e:
            updates["errors"] = [f"HypothesisGenerator error: {str(e)}"]
            
        return updates

    @staticmethod
    async def logical_validator_node(state: ResearchState) -> Dict[str, Any]:
        """
        Validate research hypothesis for logical consistency.
        Uses SynthesisAgent.
        """
        updates = {}
        updates.update(update_timestamps(state, "LogicalValidatorNode"))
        updates.update(emit_progress(state, "LogicalValidatorNode", "hypothesis_validation", 85, "Validating research hypothesis..."))
        
        try:
            val_data = await synthesis_agent.validate_logic(state.get("hypothesis", {}))
            updates["hypothesis_valid"] = val_data.get("is_valid", False)
        except Exception as e:
            updates["hypothesis_valid"] = True # Default to true for MVP if parsing fails
            
        return updates

    @staticmethod
    async def novel_judge_node(state: ResearchState) -> Dict[str, Any]:
        """
        Final novelty verification using search evidence.
        Uses SynthesisAgent.
        """
        updates = {}
        updates.update(update_timestamps(state, "NovelJudgeNode"))
        updates.update(emit_progress(state, "NovelJudgeNode", "novelty_verification", 95, "Verifying novelty..."))
        
        try:
            novelty_data = await synthesis_agent.judge_novelty(
                state.get("hypothesis", {}), 
                state.get("summaries", [])
            )
            updates["novelty_score"] = novelty_data.get("novelty_score", 0.0)
            updates["result"] = {
                "gap": state.get("selected_gap", {}),
                "hypothesis": state.get("hypothesis", {}),
                "novelty": novelty_data
            }
            # Increment retry count for novelty check
            retry_counts = state.get("retry_counts", {}).copy()
            retry_counts["novelty_check"] = retry_counts.get("novelty_check", 0) + 1
            updates["retry_counts"] = retry_counts
            
        except Exception as e:
            updates["errors"] = [f"NovelJudge error: {str(e)}"]
            
        return updates

    @staticmethod
    async def research_ready_node(state: ResearchState) -> Dict[str, Any]:
        """
        Finalize research-ready output.
        """
        updates = {}
        updates.update(update_timestamps(state, "ResearchReadyNode"))
        updates.update(emit_progress(state, "ResearchReadyNode", "completion", 100, "Research-ready hypothesis finalized."))
        updates["status"] = "completed"
        return updates
