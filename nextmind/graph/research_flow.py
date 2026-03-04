from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from nextmind.state.research_state import ResearchState
from nextmind.nodes.discovery import DiscoveryNodes
from nextmind.nodes.queries import QueryNodes
from nextmind.nodes.retrieval import RetrievalNodes
from nextmind.nodes.analysis import AnalysisNodes
from nextmind.nodes.synthesis import SynthesisNodes
from typing import Literal

def create_research_workflow():
    """
    Creates the complete NextMind LangGraph workflow (uncompiled).
    """
    workflow = StateGraph(ResearchState)
    
    # Add Nodes
    workflow.add_node("FieldInputNode", DiscoveryNodes.field_input_node)
    workflow.add_node("IntentAnalyzerNode", DiscoveryNodes.intent_analyzer_node)
    workflow.add_node("TopicGeneratorNode", DiscoveryNodes.topic_generator_node)
    
    workflow.add_node("QueryGeneratorNode", QueryNodes.query_generator_node)
    workflow.add_node("RetrievalControllerNode", RetrievalNodes.retrieval_controller_node)
    
    workflow.add_node("OpenAlexRetrieverNode", RetrievalNodes.openalex_retriever_node)
    workflow.add_node("ArxivRetrieverNode", RetrievalNodes.arxiv_retriever_node)
    workflow.add_node("SemanticScholarRetrieverNode", RetrievalNodes.semantic_scholar_retriever_node)
    workflow.add_node("PatentRetrieverNode", RetrievalNodes.patent_retriever_node)
    workflow.add_node("WebsiteRetrieverNode", RetrievalNodes.website_retriever_node)
    workflow.add_node("WikiRetrieverNode", RetrievalNodes.wiki_retriever_node)
    workflow.add_node("BlogRetrieverNode", RetrievalNodes.blog_retriever_node)
    
    workflow.add_node("DocumentAggregatorNode", AnalysisNodes.document_aggregator_node)
    workflow.add_node("SummarizerNode", AnalysisNodes.summarizer_node)
    workflow.add_node("GapDetectorNode", AnalysisNodes.gap_detector_node)
    workflow.add_node("GapScorerNode", AnalysisNodes.gap_scorer_node)
    
    workflow.add_node("HypothesisGeneratorNode", SynthesisNodes.hypothesis_generator_node)
    workflow.add_node("LogicalValidatorNode", SynthesisNodes.logical_validator_node)
    workflow.add_node("NovelJudgeNode", SynthesisNodes.novel_judge_node)
    workflow.add_node("ResearchReadyNode", SynthesisNodes.research_ready_node)
    
    # Define Edges
    workflow.set_entry_point("FieldInputNode")
    workflow.add_edge("FieldInputNode", "IntentAnalyzerNode")
    workflow.add_edge("IntentAnalyzerNode", "TopicGeneratorNode")
    
    # Interrupt after TopicGeneratorNode to wait for user selection
    workflow.add_edge("TopicGeneratorNode", "QueryGeneratorNode")
    
    workflow.add_edge("QueryGeneratorNode", "RetrievalControllerNode")
    
    # Parallel Fan-out
    workflow.add_edge("RetrievalControllerNode", "OpenAlexRetrieverNode")
    workflow.add_edge("RetrievalControllerNode", "ArxivRetrieverNode")
    workflow.add_edge("RetrievalControllerNode", "SemanticScholarRetrieverNode")
    workflow.add_edge("RetrievalControllerNode", "PatentRetrieverNode")
    workflow.add_edge("RetrievalControllerNode", "WebsiteRetrieverNode")
    workflow.add_edge("RetrievalControllerNode", "WikiRetrieverNode")
    workflow.add_edge("RetrievalControllerNode", "BlogRetrieverNode")
    
    # Fan-in
    workflow.add_edge("OpenAlexRetrieverNode", "DocumentAggregatorNode")
    workflow.add_edge("ArxivRetrieverNode", "DocumentAggregatorNode")
    workflow.add_edge("SemanticScholarRetrieverNode", "DocumentAggregatorNode")
    workflow.add_edge("PatentRetrieverNode", "DocumentAggregatorNode")
    workflow.add_edge("WebsiteRetrieverNode", "DocumentAggregatorNode")
    workflow.add_edge("WikiRetrieverNode", "DocumentAggregatorNode")
    workflow.add_edge("BlogRetrieverNode", "DocumentAggregatorNode")
    
    workflow.add_edge("DocumentAggregatorNode", "SummarizerNode")
    workflow.add_edge("SummarizerNode", "GapDetectorNode")
    workflow.add_edge("GapDetectorNode", "GapScorerNode")
    
    def check_gap_quality(state: ResearchState) -> Literal["HypothesisGeneratorNode", "QueryGeneratorNode"]:
        return "HypothesisGeneratorNode"
        
    workflow.add_conditional_edges("GapScorerNode", check_gap_quality)
    
    workflow.add_edge("HypothesisGeneratorNode", "LogicalValidatorNode")
    
    def check_logical_validity(state: ResearchState) -> Literal["NovelJudgeNode", "HypothesisGeneratorNode"]:
        if state.get("hypothesis_valid", False):
            return "NovelJudgeNode"
        return "HypothesisGeneratorNode"
        
    workflow.add_conditional_edges("LogicalValidatorNode", check_logical_validity)
    
    def check_novelty(state: ResearchState) -> Literal["ResearchReadyNode", "GapDetectorNode"]:
        novelty_score = state.get("novelty_score", 0.0)
        retries = state.get("retry_counts", {}).get("novelty_check", 0)
        
        # Proceed if novelty is good OR we've tried a few times (MVP safeguard)
        if novelty_score >= 0.1 or retries >= 2:
            return "ResearchReadyNode"
        return "GapDetectorNode"
        
    workflow.add_conditional_edges("NovelJudgeNode", check_novelty)
    
    workflow.add_edge("ResearchReadyNode", END)
    
    return workflow

# Get the workflow (uncompiled)
research_workflow = create_research_workflow()
