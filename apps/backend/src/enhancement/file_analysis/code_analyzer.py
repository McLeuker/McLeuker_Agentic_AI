"""
Code Analyzer - Code File Analysis
===================================

Analyzes code files:
- Code review
- Bug detection
- Style analysis
- Documentation generation
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Analyzes code files using kimi-2.5.
    
    Capabilities:
    - Code review
    - Bug detection
    - Style analysis
    - Documentation generation
    - Refactoring suggestions
    """
    
    LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "React JSX",
        ".tsx": "React TSX",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sql": "SQL",
        ".sh": "Shell",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".xml": "XML",
    }
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def analyze_code(
        self,
        file_path: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze code file.
        
        Args:
            file_path: Path to code file
            analysis_type: Type of analysis
            
        Returns:
            Analysis result
        """
        path = Path(file_path)
        
        # Detect language
        language = self._detect_language(path)
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            
            if not code.strip():
                return {"error": "Empty file"}
            
            # Build prompt based on analysis type
            prompts = {
                "general": f"Analyze this {language} code. Provide a summary, key functions, and overall structure.",
                "review": f"Review this {language} code. Identify bugs, issues, and improvement opportunities.",
                "style": f"Analyze the style of this {language} code. Check formatting, naming conventions, and best practices.",
                "security": f"Security review this {language} code. Identify vulnerabilities and security issues.",
                "performance": f"Performance analysis of this {language} code. Identify bottlenecks and optimization opportunities.",
                "document": f"Generate documentation for this {language} code. Explain functions, classes, and usage.",
            }
            
            prompt = prompts.get(analysis_type, prompts["general"])
            
            messages = [
                {
                    "role": "system",
                    "content": f"You are a {language} code analysis expert. Provide detailed, actionable feedback."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n```\n{code[:8000]}\n```"
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "language": language,
                "file_name": path.name,
                "lines_of_code": len(code.split("\n")),
                "analysis_type": analysis_type,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            return {"error": str(e)}
    
    async def compare_code(
        self,
        file_paths: List[str],
        comparison_focus: str = "general"
    ) -> Dict[str, Any]:
        """
        Compare multiple code files.
        
        Args:
            file_paths: List of code file paths
            comparison_focus: What to focus on
            
        Returns:
            Comparison result
        """
        try:
            code_contents = []
            for path in file_paths:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                code_contents.append(f"File: {Path(path).name}\n```\n{code[:3000]}\n```\n")
            
            prompt = f"Compare these code files. Focus on: {comparison_focus}"
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a code comparison expert."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{chr(10).join(code_contents)}"
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000
            )
            
            return {
                "files_compared": [Path(p).name for p in file_paths],
                "comparison": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Code comparison failed: {e}")
            return {"error": str(e)}
    
    async def generate_tests(
        self,
        file_path: str,
        test_framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate unit tests for code.
        
        Args:
            file_path: Path to code file
            test_framework: Test framework to use
            
        Returns:
            Generated tests
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            
            language = self._detect_language(Path(file_path))
            
            # Default test frameworks
            frameworks = {
                "Python": "pytest",
                "JavaScript": "Jest",
                "TypeScript": "Jest",
                "Java": "JUnit",
            }
            
            framework = test_framework or frameworks.get(language, "appropriate testing framework")
            
            messages = [
                {
                    "role": "system",
                    "content": f"You are a {language} testing expert. Generate comprehensive unit tests."
                },
                {
                    "role": "user",
                    "content": f"Generate {framework} unit tests for this {language} code:\n\n```\n{code[:5000]}\n```"
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000
            )
            
            return {
                "language": language,
                "test_framework": framework,
                "generated_tests": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return {"error": str(e)}
    
    def _detect_language(self, path: Path) -> str:
        """Detect programming language from file extension"""
        return self.LANGUAGE_MAP.get(path.suffix.lower(), "Unknown")
