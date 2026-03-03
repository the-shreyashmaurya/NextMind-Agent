import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from nextmind.config.settings import settings
from tavily import TavilyClient

class RetrievalTools:
    """
    Retrieval tools for each source specified in Section 9 of master-rules.md.
    """

    @staticmethod
    async def fetch_openalex(queries: List[str]) -> List[Dict[str, Any]]:
        results = []
        async with aiohttp.ClientSession() as session:
            for query in queries[:3]: # Limit queries for MVP
                url = f"https://api.openalex.org/works?search={query}"
                if settings.OPENALEX_EMAIL:
                    url += f"&mailto={settings.OPENALEX_EMAIL}"
                async with session.get(url, timeout=20) as response:
                    if response.status == 200:
                        data = await response.json()
                        for work in data.get("results", []):
                            results.append({
                                "title": work.get("title"),
                                "abstract": work.get("abstract_inverted_index"), # Needs parsing
                                "url": work.get("doi"),
                                "source": "openalex"
                            })
        return results

    @staticmethod
    async def fetch_arxiv(queries: List[str]) -> List[Dict[str, Any]]:
        # Simulation for Arxiv (would use arxiv python library or direct API)
        return [{"title": "Arxiv Simulation Result", "abstract": "Simulated abstract", "source": "arxiv"}]

    @staticmethod
    async def fetch_semantic_scholar(queries: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch papers from Semantic Scholar with rate limiting (1 req/sec).
        Gracefully handles missing API key by returning empty list.
        """
        if not settings.SEMANTIC_SCHOLAR_API_KEY:
            # Silently return empty list if key is missing as requested
            return []

        results = []
        headers = {"x-api-key": settings.SEMANTIC_SCHOLAR_API_KEY}
        
        async with aiohttp.ClientSession() as session:
            for query in queries[:3]: # Limit for MVP
                url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&fields=title,abstract,url&limit=5"
                try:
                    async with session.get(url, headers=headers, timeout=settings.RETRY_TIMEOUT if hasattr(settings, 'RETRY_TIMEOUT') else 20) as response:
                        if response.status == 200:
                            data = await response.json()
                            for paper in data.get("data", []):
                                results.append({
                                    "title": paper.get("title"),
                                    "abstract": paper.get("abstract"),
                                    "url": paper.get("url"),
                                    "source": "semanticscholar"
                                })
                        elif response.status == 429:
                            # Rate limit hit, log error but continue
                            continue
                except Exception:
                    continue
                
                # Respect 1 request per second limit
                await asyncio.sleep(1.0)
                
        return results

    @staticmethod
    async def fetch_patent(queries: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch patents from Lens API.
        Gracefully handles missing API key by returning empty list.
        """
        if not settings.LENS_API_KEY:
            # Silently return empty list if key is missing as requested
            return []

        results = []
        headers = {
            "Authorization": f"Bearer {settings.LENS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            for query in queries[:2]: # Limit for MVP
                url = "https://api.lens.org/patent/search"
                payload = {
                    "query": query,
                    "size": 5,
                    "include": ["title", "abstract", "lens_id"]
                }
                try:
                    async with session.post(url, json=payload, headers=headers, timeout=20) as response:
                        if response.status == 200:
                            data = await response.json()
                            for patent in data.get("data", []):
                                results.append({
                                    "title": patent.get("title", {}).get("value", "N/A"),
                                    "abstract": patent.get("abstract", {}).get("value", "N/A"),
                                    "url": f"https://www.lens.org/lens/patent/{patent.get('lens_id')}",
                                    "source": "lens_patent"
                                })
                        elif response.status == 429:
                            continue
                except Exception:
                    continue
                
                # Respect potential rate limits
                await asyncio.sleep(1.0)
                
        return results

    @staticmethod
    async def fetch_tavily(queries: List[str]) -> List[Dict[str, Any]]:
        if not settings.TAVILY_API_KEY:
            return []
        tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = []
        for query in queries[:2]:
            response = tavily.search(query=query, search_depth="advanced")
            for res in response.get("results", []):
                results.append({
                    "title": res.get("title"),
                    "abstract": res.get("content"),
                    "url": res.get("url"),
                    "source": "tavily"
                })
        return results

    @staticmethod
    async def fetch_wiki(queries: List[str]) -> List[Dict[str, Any]]:
        # Simulation for Wikipedia
        return [{"title": "Wiki Simulation Result", "abstract": "Simulated abstract", "source": "wikipedia"}]
