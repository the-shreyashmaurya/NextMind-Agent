from nextmind.state.research_state import ResearchState
from nextmind.utils.node_helper import emit_progress, update_timestamps
from nextmind.agents.researcher import DiscoveryAgent

# Initialize Discovery Agent
discovery_agent = DiscoveryAgent()

class DiscoveryNodes:
    """
    Discovery nodes: Intent Analyzer and Topic Generator.
    Refactored to use DiscoveryAgent.
    """
    
    @staticmethod
    async def field_input_node(state: ResearchState) -> dict[str, any]:
        """
        Normalize field and initialize progress.
        """
        updates = {}
        updates.update(update_timestamps(state, "FieldInputNode"))
        updates.update(emit_progress(state, "FieldInputNode", "initialization", 10, f"Field received: {state.get('field', 'None')}"))
        
        # Simple normalization
        if "field" in state:
            updates["field"] = state["field"].strip().lower()
            
        return updates

    @staticmethod
    async def intent_analyzer_node(state: ResearchState) -> dict[str, any]:
        """
        Analyze research field intent.
        Section 17: Intent Analyzer Prompt.
        """
        updates = {}
        updates.update(update_timestamps(state, "IntentAnalyzerNode"))
        updates.update(emit_progress(state, "IntentAnalyzerNode", "intent_analysis", 20, "Analyzing research intent..."))
        
        try:
            intent_data = await discovery_agent.analyze_intent(state["field"])
            updates["intent"] = intent_data.get("research_intent", "Unknown")
            updates["field"] = intent_data.get("normalized_field", state["field"])
        except Exception as e:
            updates["errors"] = [f"IntentAnalyzer error: {str(e)}"]
            
        return updates

    @staticmethod
    async def topic_generator_node(state: ResearchState) -> dict[str, any]:
        """
        Generate research topics.
        Section 18: Topic Generator Prompt.
        """
        updates = {}
        updates.update(update_timestamps(state, "TopicGeneratorNode"))
        updates.update(emit_progress(state, "TopicGeneratorNode", "topic_generation", 30, "Generating research topics..."))
        
        try:
            print(f"DEBUG: TopicGeneratorNode starting for field: {state.get('field')}")
            topics_response = await discovery_agent.generate_topics(state["field"], state.get("intent", "N/A"))
            print(f"DEBUG: TopicGeneratorNode raw response: {topics_response}")
            
            # Robust list extraction from potentially wrapped JSON object
            topics_list = []
            if isinstance(topics_response, dict):
                for key in ['research_topics', 'topics', 'list', 'data']:
                    if key in topics_response and isinstance(topics_response[key], list):
                        topics_list = topics_response[key]
                        break
            elif isinstance(topics_response, list):
                topics_list = topics_response
            
            # If still empty or not a list, try to handle it
            if not topics_list and topics_response:
                topics_list = [str(topics_response)]
                
            print(f"DEBUG: TopicGeneratorNode finalized topics count: {len(topics_list)}")
            updates["topics"] = topics_list
        except Exception as e:
            print(f"ERROR: TopicGeneratorNode failed: {str(e)}")
            updates["errors"] = [f"TopicGenerator error: {str(e)}"]
            
        return updates
