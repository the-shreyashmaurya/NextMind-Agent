from nextmind.state.research_state import ResearchState
from nextmind.utils.node_helper import emit_progress, update_timestamps
from nextmind.agents.researcher import DiscoveryAgent

# Initialize Discovery Agent
discovery_agent = DiscoveryAgent()

class QueryNodes:
    """
    Nodes related to query generation.
    Refactored to use DiscoveryAgent.
    """

    @staticmethod
    async def query_generator_node(state: ResearchState) -> dict[str, any]:
        """
        Generate 20 queries for multi-faceted research.
        """
        updates = {}
        updates.update(update_timestamps(state, "QueryGeneratorNode"))
        updates.update(emit_progress(state, "QueryGeneratorNode", "query_generation", 40, "Generating research queries..."))
        
        try:
            queries = await discovery_agent.generate_queries(state['selected_topic'])
            
            # Robust list extraction from potentially wrapped JSON object
            if isinstance(queries, dict):
                for key in ['queries', 'research_queries', 'list', 'data']:
                    if key in queries and isinstance(queries[key], list):
                        queries = queries[key]
                        break
            
            updates["queries"] = queries if isinstance(queries, list) else [str(queries)]
        except Exception as e:
            updates["errors"] = [f"QueryGenerator error: {str(e)}"]
            
        return updates
