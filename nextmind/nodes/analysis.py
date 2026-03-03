from typing import Dict, Any
from nextmind.state.research_state import ResearchState
from nextmind.utils.node_helper import emit_progress, update_timestamps
from nextmind.agents.researcher import AnalysisAgent
import json

# Initialize Analysis Agent
analysis_agent = AnalysisAgent()

class AnalysisNodes:
    """
    Analysis nodes: Summarizer, Concept Extractor, Coverage Analyzer, Gap Detector.
    Refactored to use AnalysisAgent.
    """

    @staticmethod
    async def document_aggregator_node(state: ResearchState) -> Dict[str, Any]:
        """
        Merge results from parallel retrievers and deduplicate.
        """
        updates = {}
        updates.update(update_timestamps(state, "DocumentAggregatorNode"))
        updates.update(emit_progress(state, "DocumentAggregatorNode", "aggregation", 50, "Merging retrieval results..."))
        
        docs = state.get("documents", [])
        # Simple deduplication by title
        unique_docs = {}
        for d in docs:
            title = d.get("title", "").lower()
            if title and title not in unique_docs:
                unique_docs[title] = d
        
        updates["clean_documents"] = list(unique_docs.values())
        return updates

    @staticmethod
    async def summarizer_node(state: ResearchState) -> Dict[str, Any]:
        """
        Summarize research documents.
        Uses AnalysisAgent.
        """
        updates = {}
        updates.update(update_timestamps(state, "SummarizerNode"))
        updates.update(emit_progress(state, "SummarizerNode", "summarization", 60, "Summarizing research findings..."))
        
        docs = state.get("clean_documents", [])[:5] # Limit for MVP
        summaries = []
        for doc in docs:
            title = doc.get("title")
            abstract = doc.get("abstract", "No abstract available")
            summary = await analysis_agent.summarize_doc(title, abstract)
            summaries.append(f"Paper: {title}\nSummary: {summary}")
        
        updates["summaries"] = summaries
        return updates

    @staticmethod
    async def gap_detector_node(state: ResearchState) -> Dict[str, Any]:
        """
        Identify research gaps.
        Uses AnalysisAgent.
        """
        updates = {}
        updates.update(update_timestamps(state, "GapDetectorNode"))
        updates.update(emit_progress(state, "GapDetectorNode", "gap_detection", 70, "Identifying research gaps..."))
        
        try:
            gaps = await analysis_agent.detect_gaps(state.get("summaries", []))
            
            # Robust list extraction from potentially wrapped JSON object
            if isinstance(gaps, dict):
                for key in ['gaps', 'research_gaps', 'list', 'data']:
                    if key in gaps and isinstance(gaps[key], list):
                        gaps = gaps[key]
                        break
            
            updates["gaps"] = gaps if isinstance(gaps, list) else [gaps]
            if gaps and isinstance(gaps, list):
                updates["selected_gap"] = gaps[0] # Auto-select best for MVP
        except Exception as e:
            updates["errors"] = [f"GapDetector error: {str(e)}"]
            
        return updates

    @staticmethod
    async def gap_scorer_node(state: ResearchState) -> Dict[str, Any]:
        """
        Score and filter identified gaps.
        """
        updates = {}
        updates.update(update_timestamps(state, "GapScorerNode"))
        updates.update(emit_progress(state, "GapScorerNode", "gap_scoring", 75, "Scoring and filtering gaps..."))
        
        # Simulation: In production, this would score gaps based on novelty search.
        gaps = state.get("gaps", [])
        updates["gap_scores"] = {g.get("title", f"Gap {i}"): 0.9 for i, g in enumerate(gaps)}
        return updates
