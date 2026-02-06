"""
McLeuker AI Backend - Kimi 2.5 Edition
Replaces Grok with full Kimi 2.5 capabilities
Maintains backward compatibility with existing frontend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, Union
import openai
import os
import base64
import json
import asyncio
import httpx
from datetime import datetime
from enum import Enum
import re

# ============================================================================
# INITIALIZATION
# ============================================================================

app = FastAPI(
    title="McLeuker AI - Kimi 2.5",
    description="Advanced Agentic AI Platform with Kimi 2.5",
    version="2.5.0"
)

# CORS - Allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mcleuker-agentic-ai.vercel.app",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Kimi 2.5 Client
KIMI_API_KEY = os.getenv("KIMI_API_KEY")
client = openai.OpenAI(
    api_key=KIMI_API_KEY,
    base_url="https://api.moonshot.cn/v1"
) if KIMI_API_KEY else None

# Legacy API keys from Railway (for tool integrations)
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

security = HTTPBearer()

# ============================================================================
# DATA MODELS (Backward Compatible + New Features)
# ============================================================================

class KeyInsight(BaseModel):
    title: str
    description: str
    confidence: float = Field(ge=0, le=1)

class Source(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None

class ResponseMetadata(BaseModel):
    model: str = "kimi-k2.5"
    mode: str
    tokens_used: Dict[str, int]
    latency_ms: Optional[int] = None
    agents_deployed: Optional[int] = None
    tool_calls_count: Optional[int] = None

# Legacy V5.1 Response (Maintained for compatibility)
class V51Response(BaseModel):
    success: bool
    response: Dict[str, Any]
    error: Optional[str] = None

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    mode: Literal["instant", "thinking", "agent", "swarm", "vision_code"] = "thinking"
    stream: bool = False
    context_id: Optional[str] = None

class SwarmTaskRequest(BaseModel):
    master_task: str
    context: Dict[str, Any] = {}
    num_agents: int = Field(default=5, ge=1, le=20)
    auto_synthesize: bool = True

class VisionCodeRequest(BaseModel):
    image_base64: str
    requirements: str = "Modern, responsive, animated UI"
    framework: Literal["html", "react", "vue", "svelte"] = "html"
    include_dependencies: bool = True

class ResearchRequest(BaseModel):
    query: str
    depth: Literal["quick", "deep", "exhaustive"] = "deep"
    sources: List[Literal["web", "academic", "news", "social"]] = ["web"]

# ============================================================================
# KIMI 2.5 CORE ENGINE
# ============================================================================

class KimiEngine:
    """
    Unified interface for all Kimi 2.5 capabilities
    Handles: Instant, Thinking, Agent, Swarm, Vision modes
    """
    
    CONFIGS = {
        "instant": {
            "temperature": 0.6,
            "top_p": 0.95,
            "extra_body": {"thinking": {"type": "disabled"}}
        },
        "thinking": {
            "temperature": 1.0,
            "top_p": 0.95,
            "extra_body": {"thinking": {"type": "enabled"}}
        },
        "agent": {
            "temperature": 0.6,
            "top_p": 0.95,
            "extra_body": {
                "thinking": {"type": "disabled"},
                "parallel_tool_calls": True
            }
        },
        "vision_code": {
            "temperature": 0.6,
            "max_tokens": 16384,
            "extra_body": {"thinking": {"type": "enabled"}}
        }
    }
    
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the internet for current information, news, and facts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "default": 5}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "perplexity_search",
                "description": "Deep research using Perplexity AI for comprehensive answers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "focus": {"type": "string", "enum": ["web", "academic", "news"], "default": "web"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_code",
                "description": "Generate code in any programming language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string", "description": "What the code should do"},
                        "language": {"type": "string", "default": "python"},
                        "framework": {"type": "string", "default": "none"}
                    },
                    "required": ["description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_data",
                "description": "Analyze structured data and provide insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "JSON or CSV data string"},
                        "analysis_type": {"type": "string", "enum": ["summary", "trends", "anomalies", "correlation"]}
                    },
                    "required": ["data", "analysis_type"]
                }
            }
        }
    ]
    
    @classmethod
    async def chat(
        cls,
        messages: List[Dict],
        mode: str = "thinking",
        use_tools: bool = False,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Execute chat with specified mode"""
        
        config = cls.CONFIGS.get(mode, cls.CONFIGS["thinking"]).copy()
        params = {
            "model": "kimi-k2.5",
            "messages": messages,
            "stream": stream,
            **config
        }
        
        # Add tools for agent mode
        if use_tools and mode == "agent":
            params["tools"] = cls.TOOLS
            params["tool_choice"] = "auto"
        
        try:
            start_time = datetime.now()
            response = client.chat.completions.create(**params)
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if stream:
                return response
            
            message = response.choices[0].message
            
            result = {
                "content": message.content,
                "reasoning_content": getattr(message, 'reasoning_content', None),
                "tool_calls": getattr(message, 'tool_calls', None),
                "mode": mode,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "reasoning_tokens": getattr(response.usage, 'reasoning_tokens', 0),
                    "total_tokens": response.usage.total_tokens
                },
                "latency_ms": latency
            }
            
            # Execute tools if present
            if result["tool_calls"]:
                tool_results = await cls.execute_tools(result["tool_calls"])
                result["tool_results"] = tool_results
                
                # Continue conversation with tool results
                continued = await cls.continue_with_tools(messages, message, tool_results)
                result["content"] = continued["content"]
                result["usage"]["total_tokens"] += continued["usage"]["total_tokens"]
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Kimi API Error: {str(e)}")
    
    @classmethod
    async def execute_tools(cls, tool_calls: List[Any]) -> List[Dict]:
        """Execute actual tool calls"""
        results = []
        
        for call in tool_calls:
            function_name = call.function.name
            arguments = json.loads(call.function.arguments)
            
            try:
                if function_name == "web_search":
                    result = await Tools.web_search(**arguments)
                elif function_name == "perplexity_search":
                    result = await Tools.perplexity_search(**arguments)
                elif function_name == "generate_code":
                    result = {"generated_code": f"// Code generation simulated for: {arguments['description']}"}
                elif function_name == "analyze_data":
                    result = {"analysis": f"Data analysis simulated for {arguments['analysis_type']}"}
                else:
                    result = {"error": f"Unknown tool: {function_name}"}
                
                results.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result)
                })
            except Exception as e:
                results.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "content": json.dumps({"error": str(e)})
                })
        
        return results
    
    @classmethod
    async def continue_with_tools(
        cls,
        original_messages: List[Dict],
        assistant_message: Any,
        tool_results: List[Dict]
    ) -> Dict[str, Any]:
        """Continue conversation after tool execution"""
        
        # Build message history with reasoning preservation
        messages = original_messages.copy()
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "reasoning_content": getattr(assistant_message, 'reasoning_content', None),
            "tool_calls": [tc.model_dump() for tc in assistant_message.tool_calls]
        })
        messages.extend(tool_results)
        
        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=messages,
            temperature=0.6,
            extra_body={"thinking": {"type": "disabled"}}  # Fast follow-up
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    @classmethod
    async def vision_to_code(
        cls,
        image_base64: str,
        requirements: str,
        framework: str
    ) -> Dict[str, Any]:
        """Convert UI image to complete code"""
        
        framework_prompts = {
            "html": "Create a single, complete HTML file with embedded CSS (Tailwind-style) and JavaScript. Include scroll animations, hover effects, and responsive design.",
            "react": "Create a complete React functional component with hooks, TypeScript, and Tailwind CSS styling.",
            "vue": "Create a complete Vue 3 Composition API component with TypeScript and scoped styles.",
            "svelte": "Create a complete Svelte component with animations and reactive statements."
        }
        
        prompt = f"""Analyze this UI design and generate production-ready {framework.upper()} code.

Requirements: {requirements}
Style: {framework_prompts.get(framework, framework_prompts['html'])}

Output ONLY the complete, runnable code."""

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=messages,
            max_tokens=16384,
            temperature=0.6,
            extra_body={"thinking": {"type": "enabled"}}
        )
        
        content = response.choices[0].message.content
        
        # Extract code blocks
        code_blocks = cls.extract_code_blocks(content)
        
        return {
            "raw_response": content,
            "code_blocks": code_blocks,
            "framework": framework,
            "tokens_used": response.usage.total_tokens,
            "reasoning": getattr(response.choices[0].message, 'reasoning_content', None)
        }
    
    @staticmethod
    def extract_code_blocks(content: str) -> List[Dict]:
        """Extract code blocks from markdown"""
        blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for lang, code in matches:
            blocks.append({
                "language": lang or "text",
                "code": code.strip(),
                "lines": len(code.strip().split('\n'))
            })
        
        # If no code blocks found, treat entire response as code
        if not blocks and content.strip():
            blocks.append({
                "language": "html",
                "code": content.strip(),
                "lines": len(content.strip().split('\n'))
            })
        
        return blocks

# ============================================================================
# TOOL IMPLEMENTATIONS (Real API Integrations)
# ============================================================================

class Tools:
    """Real tool implementations using your Railway env vars"""
    
    @staticmethod
    async def web_search(query: str, num_results: int = 5) -> Dict:
        """Web search using Exa.ai (if available) or simulated"""
        if not EXA_API_KEY:
            return {
                "results": [
                    {"title": "Simulated Result", "url": "https://example.com", "snippet": f"Results for: {query}"}
                ],
                "note": "EXA_API_KEY not configured in Railway"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.exa.ai/search",
                    headers={"Authorization": f"Bearer {EXA_API_KEY}"},
                    json={"query": query, "numResults": num_results}
                )
                return response.json()
        except Exception as e:
            return {"error": str(e), "results": []}
    
    @staticmethod
    async def perplexity_search(query: str, focus: str = "web") -> Dict:
        """Deep research using Perplexity"""
        if not PERPLEXITY_API_KEY:
            return {"answer": f"Perplexity not configured. Query: {query}", "sources": []}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
                    json={
                        "model": "sonar-pro",
                        "messages": [{"role": "user", "content": query}]
                    }
                )
                data = response.json()
                return {
                    "answer": data["choices"][0]["message"]["content"],
                    "sources": [c.get("url") for c in data.get("citations", [])]
                }
        except Exception as e:
            return {"error": str(e)}

# ============================================================================
# AGENT SWARM ORCHESTRATOR
# ============================================================================

class AgentSwarm:
    """
    Parallel agent execution for complex tasks
    Scales up to 20 agents (practical limit for Railway)
    """
    
    AGENT_ROLES = {
        "researcher": "Expert at gathering and verifying information",
        "analyst": "Expert at data analysis and pattern recognition", 
        "strategist": "Expert at planning and strategic thinking",
        "creative": "Expert at creative solutions and innovation",
        "critic": "Expert at reviewing and identifying issues",
        "implementer": "Expert at execution and practical implementation"
    }
    
    async def execute(
        self,
        master_task: str,
        context: Dict,
        num_agents: int = 5,
        auto_synthesize: bool = True
    ) -> Dict[str, Any]:
        """Execute swarm task"""
        
        start_time = datetime.now()
        
        # Step 1: Planning - Kimi breaks down the task
        subtasks = await self._create_subtasks(master_task, context, num_agents)
        
        # Step 2: Parallel execution
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent
        
        async def run_with_limit(agent_def):
            async with semaphore:
                return await self._execute_agent(agent_def, context)
        
        agent_results = await asyncio.gather(
            *[run_with_limit(task) for task in subtasks]
        )
        
        # Step 3: Synthesis (if enabled)
        final_output = None
        if auto_synthesize:
            final_output = await self._synthesize_results(
                agent_results, master_task
            )
        
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            "master_task": master_task,
            "agents_deployed": len(subtasks),
            "subtasks": subtasks,
            "agent_outputs": agent_results,
            "synthesized_output": final_output,
            "total_tokens": sum(r.get("tokens_used", 0) for r in agent_results),
            "latency_ms": latency,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _create_subtasks(
        self,
        task: str,
        context: Dict,
        num_agents: int
    ) -> List[Dict]:
        """Use Kimi to intelligently decompose task"""
        
        prompt = f"""As a task decomposition expert, break down this complex task into {num_agents} parallel subtasks.

Master Task: {task}
Context: {json.dumps(context, indent=2)}

Available roles: {list(self.AGENT_ROLES.keys())}

Return ONLY a JSON array:
[
  {{"role": "researcher/analyst/etc", "task": "specific description", "priority": 1-10}}
]"""

        try:
            response = client.chat.completions.create(
                model="kimi-k2.5",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "enabled"}}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            tasks = data.get("subtasks", data.get("tasks", []))
            
            # Validate and limit
            valid_tasks = []
            for t in tasks[:num_agents]:
                if isinstance(t, dict) and "role" in t and "task" in t:
                    valid_tasks.append({
                        "id": f"agent_{len(valid_tasks)}",
                        "role": t["role"] if t["role"] in self.AGENT_ROLES else "researcher",
                        "task": t["task"],
                        "priority": t.get("priority", 5)
                    })
            
            return valid_tasks if valid_tasks else self._fallback_subtasks(task, num_agents)
            
        except Exception as e:
            print(f"Task decomposition error: {e}")
            return self._fallback_subtasks(task, num_agents)
    
    def _fallback_subtasks(self, task: str, num: int) -> List[Dict]:
        """Fallback if decomposition fails"""
        roles = list(self.AGENT_ROLES.keys())[:num]
        return [
            {
                "id": f"agent_{i}",
                "role": role,
                "task": f"Analyze aspect {i+1} of: {task[:100]}",
                "priority": 5
            }
            for i, role in enumerate(roles)
        ]
    
    async def _execute_agent(self, agent_def: Dict, context: Dict) -> Dict:
        """Execute single agent task"""
        
        role_desc = self.AGENT_ROLES.get(agent_def["role"], "AI Assistant")
        
        messages = [
            {
                "role": "system",
                "content": f"You are a {agent_def['role']}. {role_desc}. Be concise and specific."
            },
            {
                "role": "user",
                "content": f"""Task: {agent_def['task']}
Context: {json.dumps(context, indent=2)}

Provide your analysis/output:"""
            }
        ]
        
        try:
            response = client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                extra_body={"thinking": {"type": "disabled"}}  # Fast mode
            )
            
            return {
                "agent_id": agent_def["id"],
                "role": agent_def["role"],
                "task": agent_def["task"],
                "output": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "success": True
            }
        except Exception as e:
            return {
                "agent_id": agent_def["id"],
                "role": agent_def["role"],
                "task": agent_def["task"],
                "output": f"Error: {str(e)}",
                "tokens_used": 0,
                "success": False
            }
    
    async def _synthesize_results(
        self,
        results: List[Dict],
        master_task: str
    ) -> str:
        """Synthesize all agent outputs into coherent response"""
        
        # Sort by priority/success
        successful = [r for r in results if r.get("success")]
        
        synthesis_input = "\n\n".join([
            f"### {r['role'].upper()} (Agent {r['agent_id']})\n{r['output'][:800]}"
            for r in successful[:6]  # Top 6 results
        ])
        
        prompt = f"""Synthesize these expert analyses into a comprehensive final answer.

Master Task: {master_task}

Agent Analyses:
{synthesis_input}

Provide a well-structured, actionable final response:"""

        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096,
            extra_body={"thinking": {"type": "enabled"}}
        )
        
        return response.choices[0].message.content

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/v5/chat", response_model=V51Response)
@app.post("/api/v1/chat", response_model=V51Response)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - supports all Kimi 2.5 modes
    Backward compatible with existing frontend
    """
    try:
        # Convert messages to dict format
        messages = [m.model_dump(exclude_none=True) for m in request.messages]
        
        # Determine if tools should be used
        use_tools = request.mode == "agent"
        
        result = await KimiEngine.chat(
            messages=messages,
            mode=request.mode,
            use_tools=use_tools,
            stream=request.stream
        )
        
        # Build V5.1 compatible response
        response_data = {
            "answer": result["content"],
            "mode": result["mode"],
            "reasoning": result.get("reasoning_content"),
            "sources": result.get("tool_results", []),
            "metadata": {
                "model": "kimi-k2.5",
                "mode": result["mode"],
                "tokens_used": result["usage"],
                "latency_ms": result.get("latency_ms"),
                "tool_calls_count": len(result.get("tool_calls", []))
            }
        }
        
        return V51Response(
            success=True,
            response=response_data
        )
        
    except Exception as e:
        return V51Response(
            success=False,
            response={},
            error=str(e)
        )

@app.post("/api/v1/swarm", response_model=V51Response)
async def swarm_endpoint(request: SwarmTaskRequest):
    """Agent Swarm endpoint for complex multi-agent tasks"""
    try:
        swarm = AgentSwarm()
        result = await swarm.execute(
            master_task=request.master_task,
            context=request.context,
            num_agents=request.num_agents,
            auto_synthesize=request.auto_synthesize
        )
        
        return V51Response(
            success=True,
            response={
                "answer": result.get("synthesized_output") or json.dumps(result["agent_outputs"]),
                "mode": "swarm",
                "metadata": {
                    "model": "kimi-k2.5",
                    "mode": "swarm",
                    "agents_deployed": result["agents_deployed"],
                    "tokens_used": {"total": result["total_tokens"]},
                    "latency_ms": result["latency_ms"],
                    "subtasks": result["subtasks"]
                },
                "raw_results": result
            }
        )
    except Exception as e:
        return V51Response(success=False, response={}, error=str(e))

@app.post("/api/v1/vision-to-code", response_model=V51Response)
async def vision_to_code_endpoint(request: VisionCodeRequest):
    """Convert UI images to complete code"""
    try:
        result = await KimiEngine.vision_to_code(
            image_base64=request.image_base64,
            requirements=request.requirements,
            framework=request.framework
        )
        
        return V51Response(
            success=True,
            response={
                "answer": result["raw_response"],
                "code_blocks": result["code_blocks"],
                "mode": "vision_code",
                "metadata": {
                    "model": "kimi-k2.5",
                    "mode": "vision_code",
                    "framework": request.framework,
                    "tokens_used": {"total": result["tokens_used"]},
                    "reasoning": result.get("reasoning")
                }
            }
        )
    except Exception as e:
        return V51Response(success=False, response={}, error=str(e))

@app.post("/api/v1/multimodal")
async def multimodal_endpoint(
    text: str = Form(...),
    mode: str = Form("thinking"),
    image: Optional[UploadFile] = File(None)
):
    """Handle text + image inputs"""
    try:
        content = [{"type": "text", "text": text}]
        
        if image:
            image_bytes = await image.read()
            image_b64 = base64.b64encode(image_bytes).decode()
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image.content_type};base64,{image_b64}",
                    "detail": "high"
                }
            })
        
        messages = [{"role": "user", "content": content}]
        
        result = await KimiEngine.chat(messages=messages, mode=mode)
        
        return {
            "success": True,
            "response": {
                "answer": result["content"],
                "reasoning": result.get("reasoning_content"),
                "mode": mode
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/research")
async def research_endpoint(request: ResearchRequest):
    """Deep research endpoint using multiple sources"""
    try:
        # Use agent mode with search tools
        messages = [{
            "role": "user",
            "content": f"Conduct {request.depth} research on: {request.query}. Focus on sources: {', '.join(request.sources)}"
        }]
        
        result = await KimiEngine.chat(
            messages=messages,
            mode="agent",
            use_tools=True
        )
        
        return V51Response(
            success=True,
            response={
                "answer": result["content"],
                "sources": result.get("tool_results", []),
                "mode": "research",
                "metadata": {
                    "tokens_used": result["usage"],
                    "tool_calls": len(result.get("tool_calls", []))
                }
            }
        )
    except Exception as e:
        return V51Response(success=False, response={}, error=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check with model info"""
    return {
        "status": "healthy",
        "version": "2.5.0",
        "model": "kimi-k2.5",
        "capabilities": [
            "instant_mode",
            "thinking_mode", 
            "agent_mode",
            "swarm_mode",
            "vision_code",
            "multimodal",
            "web_search",
            "code_generation"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "McLeuker AI - Kimi 2.5 Backend",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "success": False,
        "error": str(exc),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
