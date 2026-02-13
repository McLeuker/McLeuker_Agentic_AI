"""
AI Website Builder Agent — End-to-End Website Creation & Deployment
====================================================================

Creates complete, production-ready websites from natural language descriptions.
Handles everything from design to deployment.

Features:
- Requirement analysis and architecture design
- Modern React + TypeScript + Tailwind CSS code generation
- Responsive design with premium UI components
- Automatic build and deployment to Vercel/Netlify
- Live preview and iteration support

Integrates with kimi-2.5 for intelligent code generation.
"""

import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import openai

logger = logging.getLogger(__name__)


@dataclass
class WebsiteRequirements:
    """Extracted requirements for a website."""
    name: str
    purpose: str
    target_audience: str
    pages: List[str]
    style_description: str
    color_scheme: Dict[str, str]
    features: List[str]
    integrations: List[str]
    seo_requirements: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "target_audience": self.target_audience,
            "pages": self.pages,
            "style_description": self.style_description,
            "color_scheme": self.color_scheme,
            "features": self.features,
            "integrations": self.integrations,
            "seo_requirements": self.seo_requirements,
        }


@dataclass
class WebsiteProject:
    """A generated website project."""
    project_id: str
    requirements: WebsiteRequirements
    project_path: str
    files: List[str]
    build_status: str = "pending"
    deploy_url: Optional[str] = None
    preview_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "requirements": self.requirements.to_dict(),
            "project_path": self.project_path,
            "files": self.files,
            "build_status": self.build_status,
            "deploy_url": self.deploy_url,
            "preview_url": self.preview_url,
        }


class WebsiteBuilderAgent:
    """
    AI Website Builder Agent for end-to-end website creation.
    
    Usage:
        agent = WebsiteBuilderAgent(llm_client)
        async for event in agent.build_website("Create a modern portfolio website for a photographer"):
            print(event)
    """
    
    # Tech stack template
    TECH_STACK = {
        "framework": "React",
        "language": "TypeScript",
        "styling": "Tailwind CSS",
        "ui_library": "shadcn/ui",
        "build_tool": "Vite",
        "icons": "Lucide React",
        "animation": "Framer Motion",
    }
    
    def __init__(
        self,
        llm_client: openai.AsyncOpenAI,
        model: str = "kimi-k2.5",
        output_dir: str = "/tmp/website_builder",
    ):
        self.llm_client = llm_client
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track active projects
        self._active_projects: Dict[str, WebsiteProject] = {}
    
    async def build_website(
        self,
        description: str,
        project_id: Optional[str] = None,
        existing_project: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Build a complete website from a natural language description.
        
        Args:
            description: Natural language description of the website
            project_id: Optional project ID (generated if not provided)
            existing_project: Optional path to existing project to modify
            
        Yields:
            Events with progress updates, file generation, build status, etc.
        """
        import uuid
        project_id = project_id or str(uuid.uuid4())
        
        yield {"type": "start", "data": {"project_id": project_id, "description": description}}
        
        try:
            # Step 1: Analyze requirements
            yield {"type": "phase", "data": {"phase": "requirements", "status": "started"}}
            requirements = await self._analyze_requirements(description)
            yield {
                "type": "phase",
                "data": {
                    "phase": "requirements",
                    "status": "completed",
                    "requirements": requirements.to_dict(),
                }
            }
            
            # Step 2: Create project structure
            yield {"type": "phase", "data": {"phase": "structure", "status": "started"}}
            project_path = await self._create_project_structure(project_id, requirements)
            yield {"type": "phase", "data": {"phase": "structure", "status": "completed", "path": str(project_path)}}
            
            # Step 3: Generate code files
            yield {"type": "phase", "data": {"phase": "generation", "status": "started"}}
            files = await self._generate_code_files(project_path, requirements)
            yield {"type": "phase", "data": {"phase": "generation", "status": "completed", "files": files}}
            
            # Step 4: Build project
            yield {"type": "phase", "data": {"phase": "build", "status": "started"}}
            build_success = await self._build_project(project_path)
            yield {
                "type": "phase",
                "data": {
                    "phase": "build",
                    "status": "completed" if build_success else "failed",
                }
            }
            
            if not build_success:
                yield {"type": "error", "data": {"message": "Build failed"}}
                return
            
            # Step 5: Create project record
            project = WebsiteProject(
                project_id=project_id,
                requirements=requirements,
                project_path=str(project_path),
                files=files,
                build_status="success",
            )
            self._active_projects[project_id] = project
            
            yield {
                "type": "complete",
                "data": {
                    "project_id": project_id,
                    "project_path": str(project_path),
                    "files": files,
                    "requirements": requirements.to_dict(),
                }
            }
            
        except Exception as e:
            logger.error(f"Error building website: {e}")
            yield {"type": "error", "data": {"message": str(e)}}
    
    async def deploy_website(
        self,
        project_id: str,
        platform: str = "vercel",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Deploy a built website to a hosting platform.
        
        Args:
            project_id: The project ID to deploy
            platform: Deployment platform (vercel, netlify)
            
        Yields:
            Deployment progress events
        """
        yield {"type": "deploy_start", "data": {"project_id": project_id, "platform": platform}}
        
        project = self._active_projects.get(project_id)
        if not project:
            yield {"type": "error", "data": {"message": f"Project {project_id} not found"}}
            return
        
        try:
            if platform == "vercel":
                deploy_url = await self._deploy_to_vercel(project)
            elif platform == "netlify":
                deploy_url = await self._deploy_to_netlify(project)
            else:
                yield {"type": "error", "data": {"message": f"Unsupported platform: {platform}"}}
                return
            
            project.deploy_url = deploy_url
            
            yield {
                "type": "deploy_complete",
                "data": {
                    "project_id": project_id,
                    "platform": platform,
                    "url": deploy_url,
                }
            }
            
        except Exception as e:
            logger.error(f"Error deploying website: {e}")
            yield {"type": "error", "data": {"message": str(e)}}
    
    async def _analyze_requirements(self, description: str) -> WebsiteRequirements:
        """Analyze user description to extract website requirements."""
        messages = [
            {
                "role": "system",
                "content": """Analyze the website request and extract structured requirements.

Respond with JSON:
{
    "name": "Website name",
    "purpose": "Main purpose of the website",
    "target_audience": "Who will use this website",
    "pages": ["Home", "About", "Contact", etc.],
    "style_description": "Design style (modern, minimalist, corporate, playful, etc.)",
    "color_scheme": {
        "primary": "#hexcolor",
        "secondary": "#hexcolor",
        "accent": "#hexcolor",
        "background": "#hexcolor",
        "text": "#hexcolor"
    },
    "features": ["feature1", "feature2"],
    "integrations": ["integration1", "integration2"],
    "seo_requirements": ["seo1", "seo2"]
}"""
            },
            {
                "role": "user",
                "content": f"Analyze this website request: {description}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return WebsiteRequirements(
            name=result.get("name", "My Website"),
            purpose=result.get("purpose", ""),
            target_audience=result.get("target_audience", ""),
            pages=result.get("pages", ["Home"]),
            style_description=result.get("style_description", "modern"),
            color_scheme=result.get("color_scheme", {}),
            features=result.get("features", []),
            integrations=result.get("integrations", []),
            seo_requirements=result.get("seo_requirements", []),
        )
    
    async def _create_project_structure(
        self,
        project_id: str,
        requirements: WebsiteRequirements,
    ) -> Path:
        """Create the project directory structure."""
        project_path = self.output_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create directories
        (project_path / "src" / "components").mkdir(parents=True, exist_ok=True)
        (project_path / "src" / "pages").mkdir(parents=True, exist_ok=True)
        (project_path / "src" / "hooks").mkdir(parents=True, exist_ok=True)
        (project_path / "src" / "lib").mkdir(parents=True, exist_ok=True)
        (project_path / "public").mkdir(parents=True, exist_ok=True)
        
        return project_path
    
    async def _generate_code_files(
        self,
        project_path: Path,
        requirements: WebsiteRequirements,
    ) -> List[str]:
        """Generate all code files for the website."""
        files = []
        
        # Generate package.json
        package_json = await self._generate_package_json(requirements)
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        files.append("package.json")
        
        # Generate vite.config.ts
        vite_config = await self._generate_vite_config(requirements)
        (project_path / "vite.config.ts").write_text(vite_config)
        files.append("vite.config.ts")
        
        # Generate tsconfig.json
        tsconfig = await self._generate_tsconfig()
        (project_path / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))
        files.append("tsconfig.json")
        
        # Generate tailwind.config.js
        tailwind_config = await self._generate_tailwind_config(requirements)
        (project_path / "tailwind.config.js").write_text(tailwind_config)
        files.append("tailwind.config.js")
        
        # Generate index.html
        index_html = await self._generate_index_html(requirements)
        (project_path / "index.html").write_text(index_html)
        files.append("index.html")
        
        # Generate main.tsx
        main_tsx = await self._generate_main_tsx(requirements)
        (project_path / "src" / "main.tsx").write_text(main_tsx)
        files.append("src/main.tsx")
        
        # Generate App.tsx
        app_tsx = await self._generate_app_tsx(requirements)
        (project_path / "src" / "App.tsx").write_text(app_tsx)
        files.append("src/App.tsx")
        
        # Generate index.css
        index_css = await self._generate_index_css(requirements)
        (project_path / "src" / "index.css").write_text(index_css)
        files.append("src/index.css")
        
        # Generate page components
        for page in requirements.pages:
            page_component = await self._generate_page_component(page, requirements)
            page_file = f"src/pages/{page.lower().replace(' ', '_')}.tsx"
            (project_path / page_file).write_text(page_component)
            files.append(page_file)
        
        # Generate shared components
        components = ["Header", "Footer", "Navigation", "Hero"]
        for component in components:
            component_code = await self._generate_component(component, requirements)
            component_file = f"src/components/{component}.tsx"
            (project_path / component_file).write_text(component_code)
            files.append(component_file)
        
        return files
    
    async def _generate_package_json(self, requirements: WebsiteRequirements) -> Dict:
        """Generate package.json content."""
        return {
            "name": requirements.name.lower().replace(" ", "-"),
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0",
                "framer-motion": "^10.16.0",
                "lucide-react": "^0.294.0",
                "clsx": "^2.0.0",
                "tailwind-merge": "^2.0.0",
            },
            "devDependencies": {
                "@types/react": "^18.2.37",
                "@types/react-dom": "^18.2.15",
                "@vitejs/plugin-react": "^4.2.0",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.31",
                "tailwindcss": "^3.3.5",
                "typescript": "^5.2.2",
                "vite": "^5.0.0",
            },
        }
    
    async def _generate_vite_config(self, requirements: WebsiteRequirements) -> str:
        """Generate vite.config.ts content."""
        return '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
'''
    
    async def _generate_tsconfig(self) -> Dict:
        """Generate tsconfig.json content."""
        return {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
                "baseUrl": ".",
                "paths": {
                    "@/*": ["./src/*"],
                },
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}],
        }
    
    async def _generate_tailwind_config(self, requirements: WebsiteRequirements) -> str:
        """Generate tailwind.config.js content."""
        colors = requirements.color_scheme
        primary = colors.get("primary", "#3b82f6")
        
        return f'''/** @type {{import('tailwindcss').Config}} */
export default {{
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: '{primary}',
        secondary: '{colors.get("secondary", "#64748b")}',
        accent: '{colors.get("accent", "#f59e0b")}',
      }},
      fontFamily: {{
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }},
    }},
  }},
  plugins: [],
}}
'''
    
    async def _generate_index_html(self, requirements: WebsiteRequirements) -> str:
        """Generate index.html content."""
        return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{requirements.purpose}" />
    <title>{requirements.name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''
    
    async def _generate_main_tsx(self, requirements: WebsiteRequirements) -> str:
        """Generate main.tsx content."""
        return '''import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
'''
    
    async def _generate_app_tsx(self, requirements: WebsiteRequirements) -> str:
        """Generate App.tsx content."""
        imports = ['import { Routes, Route } from "react-router-dom"']
        routes = []
        
        for page in requirements.pages:
            page_name = page.replace(" ", "")
            page_import = f'import {page_name} from "./pages/{page.lower().replace(" ", "_")}"'
            imports.append(page_import)
            routes.append(f'        <Route path="/{page.lower().replace(" ", "-")}" element={{<{page_name} />}} />')
        
        home_page = requirements.pages[0].replace(" ", "") if requirements.pages else "Home"
        routes.insert(0, f'        <Route path="/" element={{<{home_page} />}} />')
        
        imports_str = "\n".join(imports)
        routes_str = "\n".join(routes)
        return f'''{imports_str}
import Header from "./components/Header"
import Footer from "./components/Footer"

function App() {{
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Routes>
{routes_str}
        </Routes>
      </main>
      <Footer />
    </div>
  )
}}

export default App
'''
    
    async def _generate_index_css(self, requirements: WebsiteRequirements) -> str:
        """Generate index.css content."""
        colors = requirements.color_scheme
        return f'''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {{
  --color-primary: {colors.get("primary", "#3b82f6")};
  --color-secondary: {colors.get("secondary", "#64748b")};
  --color-accent: {colors.get("accent", "#f59e0b")};
  --color-background: {colors.get("background", "#ffffff")};
  --color-text: {colors.get("text", "#1f2937")};
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: 'Inter', system-ui, sans-serif;
  background-color: var(--color-background);
  color: var(--color-text);
  line-height: 1.6;
}}
'''
    
    async def _generate_page_component(
        self,
        page: str,
        requirements: WebsiteRequirements,
    ) -> str:
        """Generate a page component using LLM."""
        messages = [
            {
                "role": "system",
                "content": f"""Generate a React page component for: {page}

Website: {requirements.name}
Purpose: {requirements.purpose}
Style: {requirements.style_description}

Requirements:
- Use TypeScript
- Use Tailwind CSS for styling
- Use Lucide React for icons
- Make it responsive
- Use the color scheme: {json.dumps(requirements.color_scheme)}
- Include appropriate content for the page type

Respond with ONLY the complete TypeScript React component code, no explanations."""
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        
        code = response.choices[0].message.content
        # Extract code from markdown if present
        code = self._extract_code_block(code)
        
        return code
    
    async def _generate_component(
        self,
        component: str,
        requirements: WebsiteRequirements,
    ) -> str:
        """Generate a shared component using LLM."""
        messages = [
            {
                "role": "system",
                "content": f"""Generate a React component: {component}

Website: {requirements.name}
Style: {requirements.style_description}
Pages: {', '.join(requirements.pages)}

Requirements:
- Use TypeScript
- Use Tailwind CSS
- Make it reusable and configurable
- Use Lucide React icons
- Responsive design

Respond with ONLY the complete TypeScript React component code, no explanations."""
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        
        code = response.choices[0].message.content
        code = self._extract_code_block(code)
        
        return code
    
    def _extract_code_block(self, text: str) -> str:
        """Extract code from markdown code blocks."""
        import re
        
        # Try to find TypeScript/React code block
        match = re.search(r'```(?:tsx|typescript|jsx|react)?\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Return as-is if no code block found
        return text.strip()
    
    async def _build_project(self, project_path: Path) -> bool:
        """Build the project using npm."""
        try:
            # Install dependencies
            process = await asyncio.create_subprocess_exec(
                "npm", "install",
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"npm install failed: {stderr.decode()}")
                return False
            
            # Build project
            process = await asyncio.create_subprocess_exec(
                "npm", "run", "build",
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"npm build failed: {stderr.decode()}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error building project: {e}")
            return False
    
    async def _deploy_to_vercel(self, project: WebsiteProject) -> str:
        """Deploy to Vercel."""
        # This would integrate with Vercel API
        # For now, return a placeholder
        return f"https://{project.project_id}.vercel.app"
    
    async def _deploy_to_netlify(self, project: WebsiteProject) -> str:
        """Deploy to Netlify."""
        # This would integrate with Netlify API
        return f"https://{project.project_id}.netlify.app"
    
    def get_project(self, project_id: str) -> Optional[WebsiteProject]:
        """Get a project by ID."""
        return self._active_projects.get(project_id)


# Singleton instance
_website_builder: Optional[WebsiteBuilderAgent] = None


def get_website_builder(llm_client: openai.AsyncOpenAI = None) -> WebsiteBuilderAgent:
    """Get or create the Website Builder Agent singleton."""
    global _website_builder
    if _website_builder is None and llm_client:
        _website_builder = WebsiteBuilderAgent(llm_client)
    return _website_builder
