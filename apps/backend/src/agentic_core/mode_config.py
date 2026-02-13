"""
Mode Configuration — Instant / Auto / Agent Mode Definitions
==============================================================

Defines the capabilities, credit costs, and behavior for each execution mode:

┌──────────┬──────────────────────────────────────────────────────────────────┐
│ Mode     │ Description                                                      │
├──────────┼──────────────────────────────────────────────────────────────────┤
│ Instant  │ Fast Q&A. No tools. Single LLM call. Reasoning-first, concise.  │
│          │ Credit cost: 1 credit per message.                              │
│          │ Best for: greetings, definitions, quick facts, simple analysis. │
├──────────┼──────────────────────────────────────────────────────────────────┤
│ Auto     │ Smart routing. Search + analysis. 2-5 steps.                    │
│          │ Credit cost: 3-8 credits per task.                              │
│          │ Best for: research, comparisons, data analysis, summaries.      │
├──────────┼──────────────────────────────────────────────────────────────────┤
│ Agent    │ Full agentic execution. Plan → Execute → Reflect → Deliver.     │
│          │ Credit cost: 10-50 credits per task.                            │
│          │ Best for: web automation, multi-step tasks, file generation,    │
│          │ login assistance, complex research, code execution.             │
└──────────┴──────────────────────────────────────────────────────────────────┘
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class ExecutionMode(Enum):
    INSTANT = "instant"
    AUTO = "auto"
    AGENT = "agent"


@dataclass
class ModeCapabilities:
    """Capabilities available in a mode."""
    search: bool = False
    browser: bool = False
    code_execution: bool = False
    file_generation: bool = False
    multi_step: bool = False
    reflection: bool = False
    memory: bool = False
    live_screen: bool = False
    login_assistance: bool = False
    max_steps: int = 1
    max_tokens_output: int = 4000
    models_allowed: List[str] = field(default_factory=list)


@dataclass
class ModeCreditConfig:
    """Credit costs for a mode."""
    base_cost: float = 1.0
    per_step_cost: float = 0.0
    search_cost: float = 0.0
    browser_cost: float = 0.0
    code_cost: float = 0.0
    file_cost: float = 0.0
    max_cost_cap: float = 0.0  # 0 = no cap


# Mode definitions
MODE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "instant": {
        "name": "Instant",
        "description": "Fast, reasoning-first Q&A. No tools. Single LLM call.",
        "capabilities": ModeCapabilities(
            search=False,
            browser=False,
            code_execution=False,
            file_generation=False,
            multi_step=False,
            reflection=False,
            memory=True,
            live_screen=False,
            login_assistance=False,
            max_steps=1,
            max_tokens_output=4000,
            models_allowed=["kimi-k2.5", "grok-3-mini"],
        ),
        "credits": ModeCreditConfig(
            base_cost=1.0,
            max_cost_cap=1.0,
        ),
        "routing_keywords": [
            "hi", "hello", "hey", "what is", "define", "who is", "when was",
            "how old", "capital of", "meaning of", "translate", "convert",
            "thanks", "thank you", "ok", "sure", "yes", "no",
        ],
    },
    "auto": {
        "name": "Auto",
        "description": "Smart routing with search and analysis. 2-5 steps.",
        "capabilities": ModeCapabilities(
            search=True,
            browser=False,
            code_execution=False,
            file_generation=True,
            multi_step=True,
            reflection=False,
            memory=True,
            live_screen=False,
            login_assistance=False,
            max_steps=5,
            max_tokens_output=8000,
            models_allowed=["kimi-k2.5", "grok-4-1-fast-reasoning"],
        ),
        "credits": ModeCreditConfig(
            base_cost=3.0,
            per_step_cost=1.0,
            search_cost=0.5,
            file_cost=1.0,
            max_cost_cap=8.0,
        ),
        "routing_keywords": [
            "research", "compare", "analyze", "summarize", "find",
            "search", "look up", "what are the latest", "current",
            "explain in detail", "write a report", "data on",
        ],
    },
    "agent": {
        "name": "Agent",
        "description": "Full agentic execution with planning, tools, reflection, and live screen.",
        "capabilities": ModeCapabilities(
            search=True,
            browser=True,
            code_execution=True,
            file_generation=True,
            multi_step=True,
            reflection=True,
            memory=True,
            live_screen=True,
            login_assistance=True,
            max_steps=20,
            max_tokens_output=16000,
            models_allowed=["kimi-k2.5", "grok-4-1-fast-reasoning", "grok-3-mini"],
        ),
        "credits": ModeCreditConfig(
            base_cost=10.0,
            per_step_cost=2.0,
            search_cost=0.5,
            browser_cost=1.0,
            code_cost=2.0,
            file_cost=1.0,
            max_cost_cap=50.0,
        ),
        "routing_keywords": [
            "help me login", "fill out", "book", "purchase", "sign up",
            "create a file", "generate code", "build", "automate",
            "browse", "go to", "open website", "click", "navigate",
            "execute", "run code", "deploy", "multi-step",
        ],
    },
}


def get_mode_config(mode: str) -> Dict[str, Any]:
    """Get configuration for a mode."""
    return MODE_CONFIGS.get(mode, MODE_CONFIGS["auto"])


def estimate_credit_cost(mode: str, steps: int = 1) -> float:
    """Estimate the credit cost for an execution."""
    config = get_mode_config(mode)
    credits_config = config["credits"]

    cost = credits_config.base_cost + (credits_config.per_step_cost * max(0, steps - 1))

    if credits_config.max_cost_cap > 0:
        cost = min(cost, credits_config.max_cost_cap)

    return cost


def get_mode_capabilities_summary() -> Dict[str, Any]:
    """Get a summary of all mode capabilities for the frontend."""
    summary = {}
    for mode_key, config in MODE_CONFIGS.items():
        caps = config["capabilities"]
        credits = config["credits"]
        summary[mode_key] = {
            "name": config["name"],
            "description": config["description"],
            "capabilities": {
                "search": caps.search,
                "browser": caps.browser,
                "code_execution": caps.code_execution,
                "file_generation": caps.file_generation,
                "multi_step": caps.multi_step,
                "reflection": caps.reflection,
                "live_screen": caps.live_screen,
                "login_assistance": caps.login_assistance,
                "max_steps": caps.max_steps,
            },
            "credits": {
                "base_cost": credits.base_cost,
                "per_step_cost": credits.per_step_cost,
                "max_cost_cap": credits.max_cost_cap,
            },
        }
    return summary
