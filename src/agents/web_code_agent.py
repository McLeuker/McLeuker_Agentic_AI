"""
McLeuker Agentic AI Platform - Web/Code Execution Agent

Generates web content (HTML) and code files from structured data.
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.agents.base_agent import BaseExecutionAgent
from src.models.schemas import (
    StructuredOutput,
    GeneratedFile,
    OutputFormat
)
from src.utils.llm_provider import LLMProvider, LLMFactory


class WebCodeAgent(BaseExecutionAgent):
    """
    Web/Code Execution Agent
    
    Generates HTML content, dashboards, and code files.
    """
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        llm_provider: Optional[LLMProvider] = None
    ):
        super().__init__(output_dir)
        self.llm = llm_provider or LLMFactory.get_default()
    
    @property
    def supported_formats(self) -> List[OutputFormat]:
        return [OutputFormat.WEB, OutputFormat.DASHBOARD, OutputFormat.CODE]
    
    async def execute(
        self,
        structured_output: StructuredOutput,
        filename_prefix: Optional[str] = None
    ) -> List[GeneratedFile]:
        """
        Generate web and code files from structured output.
        
        Args:
            structured_output: The structured data
            filename_prefix: Optional prefix for filenames
            
        Returns:
            List[GeneratedFile]: List of generated files
        """
        generated_files = []
        
        # Generate HTML report if documents are present
        if structured_output.documents:
            for doc in structured_output.documents:
                html_file = await self._generate_html_report(doc, filename_prefix)
                if html_file:
                    generated_files.append(html_file)
        
        # Generate dashboard if tables are present
        if structured_output.tables:
            dashboard_file = await self._generate_dashboard(
                structured_output.tables,
                filename_prefix
            )
            if dashboard_file:
                generated_files.append(dashboard_file)
        
        return generated_files
    
    async def _generate_html_report(
        self,
        document: Dict[str, Any],
        filename_prefix: Optional[str] = None
    ) -> Optional[GeneratedFile]:
        """Generate an HTML report from a structured document."""
        try:
            title = document.title if hasattr(document, 'title') else document.get('title', 'Report')
            sections = document.sections if hasattr(document, 'sections') else document.get('sections', [])
            
            html_content = self._build_html_report(title, sections)
            
            filename = self._generate_filename(filename_prefix, "html", "report")
            filepath = self._get_file_path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return self._create_generated_file(filename, OutputFormat.WEB)
            
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return None
    
    def _build_html_report(self, title: str, sections: List[Dict[str, Any]]) -> str:
        """Build HTML content for a report."""
        sections_html = ""
        for section in sections:
            heading = section.get('heading', 'Section')
            content = section.get('content', '')
            
            # Convert newlines to paragraphs
            paragraphs = content.split('\n\n')
            content_html = ''.join([f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()])
            
            subsections_html = ""
            for subsection in section.get('subsections', []):
                sub_heading = subsection.get('heading', '')
                sub_content = subsection.get('content', '')
                sub_paragraphs = sub_content.split('\n\n')
                sub_content_html = ''.join([f'<p>{p.strip()}</p>' for p in sub_paragraphs if p.strip()])
                
                subsections_html += f"""
                <div class="subsection">
                    <h3>{sub_heading}</h3>
                    {sub_content_html}
                </div>
                """
            
            sections_html += f"""
            <section class="section">
                <h2>{heading}</h2>
                {content_html}
                {subsections_html}
            </section>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #1F4E79;
            --secondary-color: #2E75B6;
            --text-color: #333;
            --bg-color: #f5f5f5;
            --white: #fff;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: var(--white);
            padding: 40px 20px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 8px;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        header .meta {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .section {{
            background: var(--white);
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--secondary-color);
        }}
        
        .section p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        .subsection {{
            margin-top: 25px;
            padding-left: 20px;
            border-left: 3px solid var(--secondary-color);
        }}
        
        .subsection h3 {{
            color: var(--secondary-color);
            margin-bottom: 10px;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9rem;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .section {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <div class="meta">Generated by McLeuker AI | {datetime.now().strftime('%B %d, %Y')}</div>
        </header>
        
        <main>
            {sections_html}
        </main>
        
        <footer>
            <p>Powered by McLeuker AI Platform</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    async def _generate_dashboard(
        self,
        tables: List[Any],
        filename_prefix: Optional[str] = None
    ) -> Optional[GeneratedFile]:
        """Generate an HTML dashboard from tables."""
        try:
            tables_html = ""
            for table in tables:
                name = table.name if hasattr(table, 'name') else table.get('name', 'Data')
                columns = table.columns if hasattr(table, 'columns') else table.get('columns', [])
                rows = table.rows if hasattr(table, 'rows') else table.get('rows', [])
                
                # Build table HTML
                headers_html = ''.join([f'<th>{col}</th>' for col in columns])
                
                rows_html = ""
                for row in rows:
                    if isinstance(row, dict):
                        cells = [str(row.get(col, '')) for col in columns]
                    else:
                        cells = [str(c) for c in row]
                    cells_html = ''.join([f'<td>{cell}</td>' for cell in cells])
                    rows_html += f'<tr>{cells_html}</tr>'
                
                tables_html += f"""
                <div class="table-container">
                    <h2>{name}</h2>
                    <table>
                        <thead>
                            <tr>{headers_html}</tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """
            
            html = self._build_dashboard_html(tables_html)
            
            filename = self._generate_filename(filename_prefix, "html", "dashboard")
            filepath = self._get_file_path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return self._create_generated_file(filename, OutputFormat.DASHBOARD)
            
        except Exception as e:
            print(f"Error generating dashboard: {e}")
            return None
    
    def _build_dashboard_html(self, tables_html: str) -> str:
        """Build HTML for a dashboard."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Dashboard</title>
    <style>
        :root {{
            --primary-color: #1F4E79;
            --secondary-color: #2E75B6;
            --accent-color: #4472C4;
            --text-color: #333;
            --bg-color: #f0f2f5;
            --white: #fff;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: var(--white);
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        header h1 {{
            font-size: 2rem;
        }}
        
        .table-container {{
            background: var(--white);
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .table-container h2 {{
            color: var(--primary-color);
            margin-bottom: 20px;
            font-size: 1.3rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background-color: var(--primary-color);
            color: var(--white);
            font-weight: 600;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .table-container {{
                overflow-x: auto;
            }}
            
            table {{
                min-width: 600px;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <header>
            <h1>Data Dashboard</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        </header>
        
        <main>
            {tables_html}
        </main>
        
        <footer>
            <p>Powered by McLeuker AI Platform</p>
        </footer>
    </div>
</body>
</html>"""
    
    async def generate_code_file(
        self,
        code: str,
        language: str = "python",
        filename: Optional[str] = None,
        filename_prefix: Optional[str] = None
    ) -> Optional[GeneratedFile]:
        """
        Generate a code file.
        
        Args:
            code: The code content
            language: Programming language
            filename: Optional specific filename
            filename_prefix: Optional prefix for filename
            
        Returns:
            GeneratedFile or None if failed
        """
        try:
            # Determine file extension
            extensions = {
                "python": "py",
                "javascript": "js",
                "typescript": "ts",
                "html": "html",
                "css": "css",
                "json": "json",
                "sql": "sql",
                "bash": "sh",
                "shell": "sh"
            }
            ext = extensions.get(language.lower(), "txt")
            
            if filename:
                if not filename.endswith(f".{ext}"):
                    filename = f"{filename}.{ext}"
            else:
                filename = self._generate_filename(filename_prefix, ext, language)
            
            filepath = self._get_file_path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return self._create_generated_file(filename, OutputFormat.CODE)
            
        except Exception as e:
            print(f"Error generating code file: {e}")
            return None
    
    async def generate_code_from_prompt(
        self,
        prompt: str,
        language: str = "python",
        filename_prefix: Optional[str] = None
    ) -> Optional[GeneratedFile]:
        """
        Generate code from a natural language prompt using LLM.
        
        Args:
            prompt: Description of what the code should do
            language: Target programming language
            filename_prefix: Optional prefix for filename
            
        Returns:
            GeneratedFile or None if failed
        """
        messages = [
            {
                "role": "system",
                "content": f"""You are an expert {language} programmer. 
Generate clean, well-documented code based on the user's request.
Only output the code, no explanations.
Include appropriate comments and docstrings."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = await self.llm.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        
        code = response.get("content", "")
        
        # Clean up code (remove markdown code blocks if present)
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        return await self.generate_code_file(
            code,
            language,
            filename_prefix=filename_prefix
        )
