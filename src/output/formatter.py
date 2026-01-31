"""
McLeuker Agentic AI Platform - Output Formatter

Creates structured, well-formatted output responses like Manus AI
with reasoning display, emojis, sections, and professional layout.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OutputStyle(str, Enum):
    """Output formatting styles."""
    CONVERSATIONAL = "conversational"  # Friendly chat style
    PROFESSIONAL = "professional"      # Business/formal style
    DETAILED = "detailed"              # In-depth with sections
    QUICK = "quick"                    # Brief, to-the-point
    RESEARCH = "research"              # Academic/research style


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
        
        # Title with emoji
        if self.emoji:
            parts.append(f"### {self.emoji} {self.title}")
        else:
            parts.append(f"### {self.title}")
        
        # Content
        if self.content:
            parts.append(self.content)
        
        # Bullet points
        if self.bullet_points:
            parts.append("")
            for point in self.bullet_points:
                parts.append(f"• {point}")
        
        # Subsections
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
        
        # Greeting
        if self.greeting:
            parts.append(self.greeting)
            parts.append("")
        
        # Reasoning display (collapsible)
        if self.reasoning_display:
            parts.append("<details>")
            parts.append("<summary>🧠 View Reasoning Process</summary>")
            parts.append("")
            parts.append(self.reasoning_display)
            parts.append("</details>")
            parts.append("")
        
        # Main content
        if self.main_content:
            parts.append(self.main_content)
            parts.append("")
        
        # Sections
        for section in self.sections:
            parts.append(section.to_markdown())
            parts.append("")
        
        # Sources
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
        
        # Files
        if self.files:
            parts.append("### 📁 Generated Files")
            for file in self.files:
                filename = file.get("filename", "file")
                file_type = file.get("type", "")
                size = file.get("size", "")
                parts.append(f"• **{filename}** ({file_type}) - {size}")
            parts.append("")
        
        # Follow-up questions
        if self.follow_up_questions:
            parts.append("### 💡 You might also want to know")
            for question in self.follow_up_questions:
                parts.append(f"• {question}")
            parts.append("")
        
        # Closing
        if self.closing:
            parts.append("---")
            parts.append(self.closing)
        
        return "\n".join(parts)
    
    def to_html(self) -> str:
        """Convert to HTML format."""
        # Convert markdown to basic HTML
        md = self.to_markdown()
        
        # Basic markdown to HTML conversion
        html = md
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # Bullet points
        html = re.sub(r'^• (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Paragraphs
        html = re.sub(r'\n\n', r'</p><p>', html)
        
        return f"<div class='mcleuker-output'><p>{html}</p></div>"
    
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
    
    Creates well-structured, visually appealing responses with:
    - Appropriate emojis
    - Clear sections
    - Reasoning display
    - Source citations
    - Follow-up suggestions
    """
    
    # Emoji mappings for different content types
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
        """
        Format a response with proper structure and styling.
        
        Args:
            content: The main content to format
            style: Output style to use
            reasoning: Optional reasoning process to display
            sources: Optional list of sources
            files: Optional list of generated files
            context: Optional context for personalization
            
        Returns:
            FormattedOutput with structured response
        """
        output = FormattedOutput(style=style)
        
        # Add greeting based on style
        if style == OutputStyle.CONVERSATIONAL:
            output.greeting = self._generate_greeting(context)
        
        # Add reasoning display
        if reasoning:
            output.reasoning_display = self._format_reasoning(reasoning)
        
        # Parse and structure the content
        sections = self._parse_content_into_sections(content)
        
        if sections:
            output.sections = sections
        else:
            output.main_content = content
        
        # Add sources
        if sources:
            output.sources = sources
        
        # Add files
        if files:
            output.files = files
        
        # Generate follow-up questions
        output.follow_up_questions = self._generate_follow_ups(content, context)
        
        # Add closing
        if style in [OutputStyle.PROFESSIONAL, OutputStyle.DETAILED]:
            output.closing = self._generate_closing(context)
        
        return output
    
    def format_search_response(
        self,
        query: str,
        answer: str,
        sources: List[Dict[str, str]],
        is_real_time: bool = True
    ) -> FormattedOutput:
        """Format a search response."""
        output = FormattedOutput(style=OutputStyle.DETAILED)
        
        # Greeting
        output.greeting = f"🔍 Here's what I found about **{query}**:"
        
        # Main content
        output.main_content = answer
        
        # Add sources
        output.sources = sources
        
        # Add real-time indicator
        if is_real_time:
            output.sections.append(FormattedSection(
                title="Information Status",
                emoji="🕐",
                content="This information is based on real-time web search results."
            ))
        
        # Generate follow-ups
        output.follow_up_questions = [
            f"Tell me more about {query}",
            f"What are the latest updates on {query}?",
            f"Compare different aspects of {query}"
        ]
        
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
        
        # Add download instructions
        output.sections.append(FormattedSection(
            title="Download Instructions",
            emoji="📥",
            content="Click on the file names above to download. The files are ready for immediate use."
        ))
        
        return output
    
    def format_list_response(
        self,
        title: str,
        items: List[Dict[str, Any]],
        item_format: str = "default"
    ) -> FormattedOutput:
        """Format a list response."""
        output = FormattedOutput(style=OutputStyle.DETAILED)
        
        output.greeting = f"📋 Here's the list of **{title}**:"
        
        # Format items into sections
        for i, item in enumerate(items, 1):
            name = item.get("name", f"Item {i}")
            description = item.get("description", "")
            details = item.get("details", {})
            
            section = FormattedSection(
                title=f"{i}. {name}",
                emoji=self._get_emoji_for_content(name),
                content=description
            )
            
            # Add details as bullet points
            for key, value in details.items():
                section.bullet_points.append(f"**{key}**: {value}")
            
            output.sections.append(section)
        
        return output
    
    def format_comparison_response(
        self,
        items: List[str],
        comparison_data: Dict[str, Dict[str, Any]]
    ) -> FormattedOutput:
        """Format a comparison response."""
        output = FormattedOutput(style=OutputStyle.DETAILED)
        
        output.greeting = f"⚖️ Here's a comparison of **{', '.join(items)}**:"
        
        # Create comparison sections
        for item in items:
            data = comparison_data.get(item, {})
            
            section = FormattedSection(
                title=item,
                emoji="📊",
                content=data.get("summary", "")
            )
            
            # Add pros/cons
            if "pros" in data:
                section.bullet_points.extend([f"✅ {p}" for p in data["pros"]])
            if "cons" in data:
                section.bullet_points.extend([f"❌ {c}" for c in data["cons"]])
            
            output.sections.append(section)
        
        return output
    
    def _generate_greeting(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate an appropriate greeting."""
        greetings = [
            "Great question! Let me help you with that.",
            "I'd be happy to help! Here's what I found:",
            "Thanks for asking! Here's the information you need:",
            "Let me look into that for you.",
        ]
        
        import random
        return random.choice(greetings)
    
    def _format_reasoning(self, reasoning: str) -> str:
        """Format reasoning for display."""
        lines = reasoning.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Add emoji to reasoning steps
                if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    formatted_lines.append(f"🔹 {line}")
                elif line.lower().startswith(('step', 'first', 'then', 'next', 'finally')):
                    formatted_lines.append(f"➡️ {line}")
                else:
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _parse_content_into_sections(self, content: str) -> List[FormattedSection]:
        """Parse content into structured sections."""
        sections = []
        
        # Try to find markdown-style headers
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # Check for headers
            if line.startswith('### '):
                if current_section:
                    current_section.content = '\n'.join(current_content)
                    sections.append(current_section)
                
                title = line[4:].strip()
                current_section = FormattedSection(
                    title=title,
                    emoji=self._get_emoji_for_content(title),
                    content=""
                )
                current_content = []
            
            elif line.startswith('## '):
                if current_section:
                    current_section.content = '\n'.join(current_content)
                    sections.append(current_section)
                
                title = line[3:].strip()
                current_section = FormattedSection(
                    title=title,
                    emoji=self._get_emoji_for_content(title),
                    content=""
                )
                current_content = []
            
            elif line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
                if current_section:
                    current_section.bullet_points.append(line[2:].strip())
            
            elif line:
                current_content.append(line)
        
        # Add last section
        if current_section:
            current_section.content = '\n'.join(current_content)
            sections.append(current_section)
        
        return sections
    
    def _get_emoji_for_content(self, content: str) -> str:
        """Get appropriate emoji for content."""
        content_lower = content.lower()
        
        for keyword, emoji in self.EMOJIS.items():
            if keyword in content_lower:
                return emoji
        
        return "📌"
    
    def _generate_follow_ups(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate follow-up questions."""
        follow_ups = []
        
        # Extract topics from content
        content_lower = content.lower()
        
        if "fashion" in content_lower:
            follow_ups.append("What are the latest fashion trends?")
        
        if "restaurant" in content_lower or "food" in content_lower:
            follow_ups.append("What are the best dishes to try?")
        
        if "shop" in content_lower or "store" in content_lower:
            follow_ups.append("What are the price ranges?")
        
        if "travel" in content_lower:
            follow_ups.append("What's the best time to visit?")
        
        # Default follow-ups
        if not follow_ups:
            follow_ups = [
                "Can you tell me more about this?",
                "What are the alternatives?",
                "How does this compare to others?"
            ]
        
        return follow_ups[:3]
    
    def _generate_closing(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a closing message."""
        closings = [
            "Is there anything else you'd like to know?",
            "Feel free to ask if you need more details!",
            "Let me know if you have any other questions!",
            "I'm here to help if you need anything else!",
        ]
        
        import random
        return random.choice(closings)


# Global formatter instance
_formatter: Optional[OutputFormatter] = None


def get_formatter() -> OutputFormatter:
    """Get or create the global formatter."""
    global _formatter
    if _formatter is None:
        _formatter = OutputFormatter()
    return _formatter
