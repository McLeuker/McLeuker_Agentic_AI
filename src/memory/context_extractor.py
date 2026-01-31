"""
McLeuker Agentic AI Platform - Context Extraction System

Extracts and maintains context from conversations to enable
coherent multi-turn interactions like Manus AI and ChatGPT.
"""

import json
import re
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from src.memory.conversation_memory import (
    Conversation,
    ConversationContext,
    Message
)


class ContextExtractor:
    """
    Extracts context from conversations to maintain coherent dialogue.
    
    Identifies:
    - Topics being discussed
    - Named entities (people, places, things)
    - Key facts mentioned
    - User preferences and intent
    """
    
    def __init__(self, llm_provider=None):
        self.llm = llm_provider
    
    async def extract_context(
        self,
        conversation: Conversation,
        new_message: str
    ) -> ConversationContext:
        """
        Extract and update context from a conversation.
        
        Args:
            conversation: The conversation to analyze
            new_message: The new message to incorporate
            
        Returns:
            Updated ConversationContext
        """
        context = conversation.context
        
        # Extract entities from new message
        entities = self._extract_entities(new_message)
        context.entities.update(entities)
        
        # Extract topics
        topics = self._extract_topics(new_message)
        for topic in topics:
            if topic not in context.topics:
                context.topics.append(topic)
        
        # Keep only recent topics (last 10)
        context.topics = context.topics[-10:]
        
        # Extract key facts
        facts = self._extract_facts(new_message)
        context.key_facts.extend(facts)
        context.key_facts = context.key_facts[-20:]  # Keep last 20 facts
        
        # Determine intent
        context.last_intent = self._classify_intent(new_message)
        
        # Use LLM for deeper context extraction if available
        if self.llm and len(conversation.messages) > 2:
            await self._llm_context_update(conversation, new_message, context)
        
        return context
    
    def _extract_entities(self, text: str) -> Dict[str, str]:
        """Extract named entities from text using pattern matching."""
        entities = {}
        
        # Location patterns
        location_patterns = [
            r'\b(?:in|at|to|from|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:city|country|town|region|district)\b',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 2:
                    entities[match] = "location"
        
        # Common cities
        cities = [
            "Paris", "London", "New York", "Tokyo", "Berlin", "Rome", "Milan",
            "Barcelona", "Amsterdam", "Dubai", "Singapore", "Hong Kong", "Sydney",
            "Los Angeles", "San Francisco", "Chicago", "Miami", "Seattle"
        ]
        for city in cities:
            if city.lower() in text.lower():
                entities[city] = "city"
        
        # Price/money patterns
        money_pattern = r'\$[\d,]+(?:\.\d{2})?|\€[\d,]+(?:\.\d{2})?|[\d,]+\s*(?:dollars|euros|pounds)'
        money_matches = re.findall(money_pattern, text, re.IGNORECASE)
        for match in money_matches:
            entities[match] = "money"
        
        # Date patterns
        date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?\b'
        date_matches = re.findall(date_pattern, text)
        for match in date_matches:
            entities[match] = "date"
        
        return entities
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        topics = []
        
        # Topic keywords
        topic_keywords = {
            "fashion": ["fashion", "clothing", "style", "outfit", "wear", "dress", "designer"],
            "food": ["restaurant", "food", "dining", "cuisine", "eat", "meal", "chef"],
            "travel": ["travel", "trip", "visit", "hotel", "flight", "vacation", "tourism"],
            "shopping": ["shop", "store", "buy", "purchase", "retail", "second hand", "vintage"],
            "technology": ["tech", "ai", "software", "app", "digital", "computer", "phone"],
            "business": ["business", "company", "market", "industry", "startup", "investment"],
            "health": ["health", "fitness", "wellness", "medical", "exercise", "diet"],
            "entertainment": ["movie", "music", "concert", "show", "game", "entertainment"],
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_facts(self, text: str) -> List[str]:
        """Extract key facts from text."""
        facts = []
        
        # Look for statements that might be facts
        # Numbers with context
        number_pattern = r'(?:there are|has|have|is|was|were)\s+(\d+)\s+([a-zA-Z\s]+)'
        matches = re.findall(number_pattern, text, re.IGNORECASE)
        for num, context in matches:
            facts.append(f"{num} {context.strip()}")
        
        # Specific mentions
        if "best" in text.lower() or "top" in text.lower():
            # Extract what's being described as best/top
            best_pattern = r'(?:best|top)\s+(\d+)?\s*([a-zA-Z\s]+?)(?:\s+(?:in|for|of)|\.|,|$)'
            matches = re.findall(best_pattern, text, re.IGNORECASE)
            for num, item in matches:
                if item.strip():
                    fact = f"top {num} {item.strip()}" if num else f"best {item.strip()}"
                    facts.append(fact)
        
        return facts
    
    def _classify_intent(self, text: str) -> str:
        """Classify the intent of a message."""
        text_lower = text.lower()
        
        # Question patterns
        if text.strip().endswith("?") or any(q in text_lower for q in ["what", "where", "when", "who", "how", "why", "which"]):
            if "recommend" in text_lower or "suggest" in text_lower or "best" in text_lower:
                return "recommendation_request"
            elif "how to" in text_lower or "how do" in text_lower:
                return "how_to_question"
            else:
                return "information_question"
        
        # Command patterns
        if any(cmd in text_lower for cmd in ["create", "make", "generate", "build", "write"]):
            return "creation_request"
        
        if any(cmd in text_lower for cmd in ["find", "search", "look for", "show me"]):
            return "search_request"
        
        if any(cmd in text_lower for cmd in ["list", "give me", "tell me"]):
            return "list_request"
        
        if any(cmd in text_lower for cmd in ["compare", "difference", "versus", "vs"]):
            return "comparison_request"
        
        if any(cmd in text_lower for cmd in ["explain", "describe", "what is"]):
            return "explanation_request"
        
        return "general_conversation"
    
    async def _llm_context_update(
        self,
        conversation: Conversation,
        new_message: str,
        context: ConversationContext
    ):
        """Use LLM to extract deeper context."""
        if not self.llm:
            return
        
        try:
            # Get recent conversation history
            recent_messages = conversation.get_recent_messages(5)
            history = "\n".join([f"{m.role}: {m.content}" for m in recent_messages])
            
            prompt = f"""Analyze this conversation and extract key context:

Conversation:
{history}

New message: {new_message}

Extract:
1. Main topic being discussed
2. Any specific entities mentioned (places, people, things)
3. What the user is trying to accomplish
4. Any preferences expressed

Respond in JSON format:
{{"topic": "...", "entities": {{}}, "goal": "...", "preferences": {{}}}}"""

            messages = [
                {"role": "system", "content": "You are a context extraction assistant. Extract key information from conversations."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.llm.complete(
                messages=messages,
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.get("content", "")
            
            # Try to parse JSON from response
            try:
                # Find JSON in response
                json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    
                    if data.get("topic"):
                        if data["topic"] not in context.topics:
                            context.topics.append(data["topic"])
                    
                    if data.get("entities"):
                        context.entities.update(data["entities"])
                    
                    if data.get("goal"):
                        context.last_intent = data["goal"]
                    
                    if data.get("preferences"):
                        context.user_preferences.update(data["preferences"])
            except json.JSONDecodeError:
                pass
                
        except Exception as e:
            # Silently fail - context extraction is not critical
            pass
    
    def build_context_prompt(self, conversation: Conversation) -> str:
        """
        Build a context prompt to prepend to LLM requests.
        
        This ensures the LLM has full context of the conversation.
        """
        context = conversation.context
        parts = []
        
        # Add conversation summary
        if context.topics:
            parts.append(f"📌 Current topics: {', '.join(context.topics[-5:])}")
        
        if context.entities:
            # Group entities by type
            by_type = {}
            for name, type_ in context.entities.items():
                if type_ not in by_type:
                    by_type[type_] = []
                by_type[type_].append(name)
            
            for type_, names in by_type.items():
                parts.append(f"📍 {type_.title()}s mentioned: {', '.join(names[-5:])}")
        
        if context.key_facts:
            parts.append(f"📝 Key facts: {'; '.join(context.key_facts[-3:])}")
        
        if context.user_preferences:
            prefs = ", ".join([f"{k}: {v}" for k, v in list(context.user_preferences.items())[-3:]])
            parts.append(f"⚙️ User preferences: {prefs}")
        
        if parts:
            return "CONVERSATION CONTEXT:\n" + "\n".join(parts) + "\n\n"
        
        return ""
    
    def get_referenced_entities(
        self,
        text: str,
        conversation: Conversation
    ) -> Dict[str, str]:
        """
        Resolve references in text to entities from conversation context.
        
        Handles pronouns and references like "there", "it", "that place", etc.
        """
        context = conversation.context
        resolved = {}
        
        text_lower = text.lower()
        
        # Check for location references
        location_refs = ["there", "that place", "that city", "that location"]
        if any(ref in text_lower for ref in location_refs):
            # Find most recent location in context
            for entity, type_ in reversed(list(context.entities.items())):
                if type_ in ["location", "city", "country"]:
                    resolved["location_reference"] = entity
                    break
        
        # Check for "it" references
        if " it " in text_lower or text_lower.startswith("it ") or text_lower.endswith(" it"):
            # Try to find what "it" refers to from recent context
            if context.topics:
                resolved["it_reference"] = context.topics[-1]
        
        return resolved
