"""
McLeuker Agentic AI Platform - Output Formatter v2.1

Creates structured, well-formatted output responses like Manus AI
with proper reasoning display, emojis, sections, and professional layout.
Fixed follow-up questions to be contextually relevant.
"""

import re
import random
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OutputStyle(str, Enum):
    """Output formatting styles."""
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    DETAILED = "detailed"
    QUICK = "quick"
    RESEARCH = "research"


@dataclass
class FormattedSection:
    """A formatted section of output."""
    title: str
    content: str
    emoji: str = ""
    bullet_points: List[str] = field(default_factory=list)
    subsections: List['FormattedSection'] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert section to markdown."""
        parts = []
        
        if self.emoji:
            parts.append(f"### {self.emoji} {self.title}")
        else:
            parts.append(f"### {self.title}")
        
        if self.content:
            parts.append(self.content)
        
        if self.bullet_points:
            parts.append("")
            for point in self.bullet_points:
                parts.append(f"• {point}")
        
        for subsection in self.subsections:
            parts.append("")
            parts.append(subsection.to_markdown())
        
        return "\n".join(parts)


@dataclass
class FormattedOutput:
    """Complete formatted output response."""
    greeting: Optional[str] = None
    reasoning_display: Optional[str] = None
    main_content: str = ""
    sections: List[FormattedSection] = field(default_factory=list)
    sources: List[Dict[str, str]] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)
    closing: Optional[str] = None
    style: OutputStyle = OutputStyle.PROFESSIONAL
    
    def to_markdown(self) -> str:
        """Convert to markdown format."""
        parts = []
        
        if self.greeting:
            parts.append(self.greeting)
            parts.append("")
        
        if self.reasoning_display:
            parts.append("<details>")
            parts.append("<summary>🧠 View Reasoning Process</summary>")
            parts.append("")
            parts.append(self.reasoning_display)
            parts.append("</details>")
            parts.append("")
        
        if self.main_content:
            parts.append(self.main_content)
            parts.append("")
        
        for section in self.sections:
            parts.append(section.to_markdown())
            parts.append("")
        
        if self.sources:
            parts.append("### 📚 Sources")
            for i, source in enumerate(self.sources, 1):
                title = source.get("title", f"Source {i}")
                url = source.get("url", "")
                if url:
                    parts.append(f"{i}. [{title}]({url})")
                else:
                    parts.append(f"{i}. {title}")
            parts.append("")
        
        if self.files:
            parts.append("### 📁 Generated Files")
            for file in self.files:
                filename = file.get("filename", "file")
                file_type = file.get("type", "")
                size = file.get("size", "")
                parts.append(f"• **{filename}** ({file_type}) - {size}")
            parts.append("")
        
        if self.follow_up_questions:
            parts.append("### 💡 You might also want to know")
            for question in self.follow_up_questions:
                parts.append(f"• {question}")
            parts.append("")
        
        if self.closing:
            parts.append("---")
            parts.append(self.closing)
        
        return "\n".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "greeting": self.greeting,
            "reasoning_display": self.reasoning_display,
            "main_content": self.main_content,
            "sections": [
                {
                    "title": s.title,
                    "emoji": s.emoji,
                    "content": s.content,
                    "bullet_points": s.bullet_points
                }
                for s in self.sections
            ],
            "sources": self.sources,
            "follow_up_questions": self.follow_up_questions,
            "files": self.files,
            "closing": self.closing,
            "style": self.style.value,
            "markdown": self.to_markdown()
        }


class OutputFormatter:
    """
    Output formatter for creating Manus AI-style responses.
    """
    
    EMOJIS = {
        "overview": "📋",
        "summary": "📝",
        "details": "🔍",
        "recommendation": "⭐",
        "warning": "⚠️",
        "tip": "💡",
        "note": "📌",
        "important": "❗",
        "success": "✅",
        "error": "❌",
        "question": "❓",
        "answer": "💬",
        "list": "📃",
        "data": "📊",
        "chart": "📈",
        "location": "📍",
        "time": "🕐",
        "money": "💰",
        "shopping": "🛍️",
        "food": "🍽️",
        "travel": "✈️",
        "fashion": "👗",
        "technology": "💻",
        "health": "🏥",
        "education": "📚",
        "business": "💼",
        "creative": "🎨",
        "music": "🎵",
        "sports": "⚽",
        "nature": "🌿",
        "weather": "🌤️",
    }
    
    # Topic-specific follow-up templates
    FOLLOW_UP_TEMPLATES = {
        "fashion": [
            "What are the latest fashion trends for this season?",
            "Which designers are leading this movement?",
            "How can I incorporate this into my wardrobe?",
            "What are the price ranges for these items?"
        ],
        "technology": [
            "What are the technical specifications?",
            "How does this compare to competitors?",
            "What are the pros and cons?",
            "When will this be available?"
        ],
        "business": [
            "What are the market implications?",
            "Who are the key players in this space?",
            "What are the investment opportunities?",
            "What are the risks involved?"
        ],
        "travel": [
            "What's the best time to visit?",
            "What are the must-see attractions?",
            "What's the estimated budget?",
            "Are there any travel advisories?"
        ],
        "food": [
            "What are the popular dishes to try?",
            "Are there vegetarian/vegan options?",
            "What's the price range?",
            "Do I need reservations?"
        ],
        "health": [
            "What are the potential side effects?",
            "How long does treatment take?",
            "Are there alternative treatments?",
            "What does the research say?"
        ],
        "general": [
            "Can you provide more details?",
            "What are the alternatives?",
            "What are the pros and cons?",
            "How does this compare to others?"
        ]
    }
    
    def __init__(self):
        pass
    
    def format_response(
        self,
        content: str,
        style: OutputStyle = OutputStyle.PROFESSIONAL,
        reasoning: Optional[str] = None,
        sources: Optional[List[Dict[str, str]]] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> FormattedOutput:
        """Format a response with proper structure and styling."""
        output = FormattedOutput(style=style)
        
        if style == OutputStyle.CONVERSATIONAL:
            output.greeting = self._generate_greeting(context)
        
        if reasoning:
            output.reasoning_display = self._format_reasoning(reasoning)
        
        # Parse content into sections
        sections = self._parse_content_into_sections(content)
        
        if sections:
            output.sections = sections
        else:
            output.main_content = content
        
        if sources:
            output.sources = sources
        
        if files:
            output.files = files
        
        # Generate contextual follow-up questions
        output.follow_up_questions = self._generate_contextual_follow_ups(content)
        
        return output
    
    def format_search_response(
        self,
        query: str,
        answer: str,
        sources: List[Dict[str, str]],
        is_real_time: bool = True
    ) -> FormattedOutput:
        """Format a search response with the actual answer content."""
        output = FormattedOutput(style=OutputStyle.DETAILED)
        
        # Set the main content to the actual answer
        output.main_content = answer
        
        # Add sources if available
        if sources:
            output.sources = sources
        
        # Generate contextual follow-up questions based on the answer
        output.follow_up_questions = self._generate_contextual_follow_ups(answer, query)
        
        return output
    
    def format_file_generation_response(
        self,
        files: List[Dict[str, Any]],
        description: str
    ) -> FormattedOutput:
        """Format a file generation response."""
        output = FormattedOutput(style=OutputStyle.PROFESSIONAL)
        
        output.greeting = "✅ I've generated the requested files for you!"
        output.main_content = description
        output.files = files
        
        output.sections.append(FormattedSection(
            title="Download Instructions",
            emoji="📥",
            content="Click on the file names above to download. The files are ready for immediate use."
        ))
        
        return output
    
    def _generate_greeting(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate an appropriate greeting."""
        greetings = [
            "Great question! Let me help you with that.",
            "I'd be happy to help! Here's what I found:",
            "Thanks for asking! Here's the information you need:",
            "Let me look into that for you.",
        ]
        return random.choice(greetings)
    
    def _format_reasoning(self, reasoning: str) -> str:
        """Format reasoning for display."""
        lines = reasoning.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    formatted_lines.append(f"🔹 {line}")
                elif line.lower().startswith(('step', 'first', 'then', 'next', 'finally')):
                    formatted_lines.append(f"➡️ {line}")
                else:
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _parse_content_into_sections(self, content: str) -> List[FormattedSection]:
        """Parse content into formatted sections."""
        sections = []
        
        # Split by markdown headers
        header_pattern = r'^(#{1,3})\s+(.+)$'
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            header_match = re.match(header_pattern, line)
            
            if header_match:
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)
                
                # Start new section
                title = header_match.group(2).strip()
                emoji = self._get_emoji_for_content(title)
                current_section = FormattedSection(title=title, emoji=emoji, content="")
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)
        
        return sections
    
    def _get_emoji_for_content(self, text: str) -> str:
        """Get appropriate emoji for content."""
        text_lower = text.lower()
        
        for keyword, emoji in self.EMOJIS.items():
            if keyword in text_lower:
                return emoji
        
        # Default emojis based on common patterns
        if any(word in text_lower for word in ['trend', 'style', 'wear', 'outfit']):
            return "👗"
        if any(word in text_lower for word in ['price', 'cost', 'budget', 'money']):
            return "💰"
        if any(word in text_lower for word in ['tip', 'advice', 'recommend']):
            return "💡"
        if any(word in text_lower for word in ['list', 'top', 'best']):
            return "📋"
        if any(word in text_lower for word in ['step', 'how', 'guide']):
            return "📝"
        
        return "📌"
    
    def _detect_topic(self, content: str) -> str:
        """Detect the main topic from content."""
        content_lower = content.lower()
        
        topic_keywords = {
            "fashion": ["fashion", "style", "wear", "outfit", "designer", "clothing", "trend"],
            "technology": ["tech", "software", "app", "device", "digital", "ai", "computer"],
            "business": ["business", "market", "company", "invest", "finance", "economy"],
            "travel": ["travel", "trip", "destination", "hotel", "flight", "vacation"],
            "food": ["food", "restaurant", "recipe", "cuisine", "dish", "meal"],
            "health": ["health", "medical", "treatment", "symptom", "doctor", "wellness"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in content_lower for kw in keywords):
                return topic
        
        return "general"
    
    def _generate_contextual_follow_ups(
        self,
        content: str,
        original_query: str = ""
    ) -> List[str]:
        """Generate contextually relevant follow-up questions."""
        topic = self._detect_topic(content)
        templates = self.FOLLOW_UP_TEMPLATES.get(topic, self.FOLLOW_UP_TEMPLATES["general"])
        
        # Select 3 random follow-ups from the topic
        follow_ups = random.sample(templates, min(3, len(templates)))
        
        return follow_ups


# Global formatter instance
_formatter: Optional[OutputFormatter] = None


def get_formatter() -> OutputFormatter:
    """Get or create the global formatter."""
    global _formatter
    if _formatter is None:
        _formatter = OutputFormatter()
    return _formatter
