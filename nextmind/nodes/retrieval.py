import asyncio
from typing import List, Dict, Any
from nextmind.state.research_state import ResearchState
from nextmind.utils.node_helper import emit_progress, update_timestamps
from nextmind.tools.retrieval_tools import RetrievalTools
from nextmind.config.settings import settings

class RetrievalNodes:
    """
    Retrieval nodes that run in parallel using asyncio.gather().
    Section 9: Retrieval Rules.
    Section 10: Retrieval Parallel Rules.
    """

    @staticmethod
    async def openalex_retriever_node(state: ResearchState) -> Dict[str, Any]:
        updates = emit_progress(state, "OpenAlexRetrieverNode", "retrieval.openalex", 45, "Fetching from OpenAlex...")
        queries = state.get("queries", [])
        results = await RetrievalTools.fetch_openalex(queries)
        updates["documents"] = results
        return updates

    @staticmethod
    async def arxiv_retriever_node(state: ResearchState) -> Dict[str, Any]:
        updates = emit_progress(state, "ArxivRetrieverNode", "retrieval.arxiv", 45, "Fetching from Arxiv...")
        queries = state.get("queries", [])
        results = await RetrievalTools.fetch_arxiv(queries)
        updates["documents"] = results
        return updates

    @staticmethod
    async def semantic_scholar_retriever_node(state: ResearchState) -> Dict[str, Any]:
        """
        Retrieves from Semantic Scholar. Handles missing key by logging and skipping.
        """
        if not settings.SEMANTIC_SCHOLAR_API_KEY:
            return emit_progress(state, "SemanticScholarRetrieverNode", "retrieval.semanticscholar", 45, "Skipping Semantic Scholar: No API Key provided.")

        updates = emit_progress(state, "SemanticScholarRetrieverNode", "retrieval.semanticscholar", 45, "Fetching from Semantic Scholar...")
        queries = state.get("queries", [])
        results = await RetrievalTools.fetch_semantic_scholar(queries)
        updates["documents"] = results
        return updates

    @staticmethod
    async def patent_retriever_node(state: ResearchState) -> Dict[str, Any]:
        """
        Retrieves patents from Lens. Handles missing key by logging and skipping.
        """
        if not settings.LENS_API_KEY:
            return emit_progress(state, "PatentRetrieverNode", "retrieval.patent", 45, "Skipping Lens Patent: No API Key provided.")

        updates = emit_progress(state, "PatentRetrieverNode", "retrieval.patent", 45, "Fetching from Lens Patent...")
        queries = state.get("queries", [])
        results = await RetrievalTools.fetch_patent(queries)
        updates["documents"] = results
        return updates

    @staticmethod
    async def website_retriever_node(state: ResearchState) -> Dict[str, Any]:
        updates = emit_progress(state, "WebsiteRetrieverNode", "retrieval.website", 45, "Fetching from Tavily/Web...")
        queries = state.get("queries", [])
        results = await RetrievalTools.fetch_tavily(queries)
        updates["documents"] = results
        return updates

    @staticmethod
    async def wiki_retriever_node(state: ResearchState) -> Dict[str, Any]:
        updates = emit_progress(state, "WikiRetrieverNode", "retrieval.wiki", 45, "Fetching from Wikipedia...")
        queries = state.get("queries", [])
        results = await RetrievalTools.fetch_wiki(queries)
        updates["documents"] = results
        return updates

    @staticmethod
    async def blog_retriever_node(state: ResearchState) -> Dict[str, Any]:
        return emit_progress(state, "BlogRetrieverNode", "retrieval.blog", 45, "Fetching from Blogs...")

    @staticmethod
    async def retrieval_controller_node(state: ResearchState) -> Dict[str, Any]:
        """
        Orchestrate parallel retrievers.
        Section 10 requires asyncio.gather()
        """
        updates = {}
        updates.update(update_timestamps(state, "RetrievalControllerNode"))
        updates.update(emit_progress(state, "RetrievalControllerNode", "retrieval", 42, "Starting parallel retrieval..."))
        return updates
