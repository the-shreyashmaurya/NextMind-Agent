from langchain_openai import ChatOpenAI
from nextmind.config.settings import settings
import json
from typing import List, Dict, Any, Optional

class BaseAgent:
    def __init__(self, model: str):
        self.llm = ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            model=model,
            base_url=settings.OPENROUTER_BASE_URL,
            temperature=0.2, # Section 2: Temperature default 0.2
            request_timeout=20.0 # Section 11: Timeout 20 sec
        )

    async def ask(self, prompt: str, is_json: bool = True):
        response = await self.llm.ainvoke(prompt)
        content = response.content
        if is_json:
            # Handle R1's reasoning block or triple backticks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "<think>" in content:
                content = content.split("</think>")[1].strip()
            
            try:
                return json.loads(content)
            except Exception as e:
                # If JSON parsing fails, return as-is or handle
                return {"error": "JSON parsing failed", "content": content}
        return content

class DiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__(settings.CHEAP_MODEL)

    async def analyze_intent(self, field: str):
        prompt = f"""Analyze research field: {field}
        
        Return JSON:
        {{
            "normalized_field": "string",
            "subfields": ["list"],
            "research_intent": "string"
        }}
        """
        return await self.ask(prompt)

    async def generate_topics(self, field: str, intent: str):
        prompt = f"""Generate 10 research topics for the field: {field}.
        Intent: {intent}
        
        Each topic must be:
        Specific
        Novel
        Researchable
        
        Return JSON list of strings.
        """
        return await self.ask(prompt)

    async def generate_queries(self, topic: str):
        prompt = f"""Generate 20 research queries for the topic: {topic}.
        
        Include:
        Technical queries
        Conceptual queries
        Patent queries
        
        Return JSON list of strings.
        """
        return await self.ask(prompt)

class AnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(settings.REASONING_MODEL)

    async def summarize_doc(self, title: str, abstract: str):
        prompt = f"Summarize the key research findings of this paper: {title}\n\nAbstract: {abstract}"
        return await self.ask(prompt, is_json=False)

    async def detect_gaps(self, summaries: List[str]):
        summaries_text = "\n".join(summaries)
        prompt = f"""Input summaries:
        {summaries_text}
        
        Identify research gaps.
        Each gap must:
        Be testable
        Be measurable
        Be realistic
        
        Return JSON list of objects with fields: 'title', 'description', 'impact', 'testability'.
        """
        return await self.ask(prompt)

class SynthesisAgent(BaseAgent):
    def __init__(self):
        super().__init__(settings.CRITICAL_MODEL)

    async def generate_hypothesis(self, gap: Dict[str, Any]):
        prompt = f"""Generate hypothesis for selected research gap: {gap.get('title')}
        Description: {gap.get('description')}
        
        Format:
        If X then Y because Z.
        
        Include:
        Variables
        Measurement
        Expected outcome
        
        Return JSON with fields: 'hypothesis_statement', 'variables', 'measurement_plan', 'expected_outcome'.
        """
        return await self.ask(prompt)

    async def validate_logic(self, hypothesis: Dict[str, Any]):
        prompt = f"""Analyze this research hypothesis for logical consistency and falsifiability:
        Hypothesis: {hypothesis.get('hypothesis_statement')}
        
        Return JSON:
        {{
            "is_valid": boolean,
            "critique": "string",
            "suggestions": ["list"]
        }}
        """
        return await self.ask(prompt)

    async def judge_novelty(self, hypothesis: Dict[str, Any]):
        prompt = f"""Evaluate novelty for the following research hypothesis:
        {hypothesis.get('hypothesis_statement')}
        
        Based on existing knowledge, provide a novelty score (0-1).
        
        Return JSON:
        {{
            "novelty_score": float,
            "reasoning": "string",
            "similar_research": ["list"]
        }}
        """
        return await self.ask(prompt)
