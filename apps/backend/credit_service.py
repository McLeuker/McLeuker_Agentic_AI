"""
McLeuker AI - Credit Service v2
Real-time usage-based credit deduction system (Manus AI style).
Credits are deducted incrementally during task execution based on actual API usage.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from supabase import Client


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModuleType(Enum):
    SEARCH = "search"
    SOCIAL = "social"
    AGENT = "agent"
    ANALYSIS = "analysis"


# ============================================================================
# REAL-TIME CREDIT COST TABLE
# Each operation has a specific credit cost based on actual API expense + margin
# Margin target: ~60-70% gross margin on API costs
# ============================================================================

# API cost estimates (USD) and credit mappings
# 1 credit ≈ $0.01 value to user (at $4.99/500 credits = $0.00998/credit)
# We price operations at ~2.5-3x actual API cost for healthy margins

OPERATION_COSTS = {
    # Search APIs (per call)
    "search_brave": 1,          # Brave search ~$0.003/query → 1 credit
    "search_serper": 1,         # Serper ~$0.004/query → 1 credit
    "search_perplexity": 3,     # Perplexity ~$0.008/query → 3 credits
    "search_exa": 2,            # Exa ~$0.005/query → 2 credits
    "search_bing": 1,           # Bing ~$0.003/query → 1 credit
    "search_google": 1,         # Google Custom Search → 1 credit
    "search_serpapi": 1,        # SerpAPI → 1 credit
    "search_firecrawl": 2,      # Firecrawl scraping → 2 credits

    # LLM calls (per call, varies by model)
    "llm_kimi_stream": 3,       # Kimi K2.5 streaming response → 3 credits
    "llm_kimi_generate": 4,     # Kimi K2.5 content generation (file) → 4 credits
    "llm_kimi_quality": 2,      # Kimi quality check → 2 credits
    "llm_kimi_conclusion": 1,   # Kimi conclusion generation → 1 credit
    "llm_grok_stream": 2,       # Grok streaming response → 2 credits
    "llm_grok_search": 3,       # Grok search-augmented → 3 credits

    # File generation (per file)
    "file_excel": 5,            # Excel generation → 5 credits
    "file_pdf": 5,              # PDF generation → 5 credits
    "file_pptx": 8,             # PPTX generation → 8 credits
    "file_word": 5,             # Word generation → 5 credits
    "file_csv": 2,              # CSV generation → 2 credits

    # Image generation
    "image_generation": 15,     # Image gen via Grok/DALL-E → 15 credits

    # Agent operations (per reasoning step)
    "agent_step": 3,            # Each agent reasoning step → 3 credits
    "agent_tool_call": 2,       # Each tool invocation → 2 credits
}

# Mode base costs (minimum charge even for simple queries)
MODE_BASE_COSTS = {
    "instant": 2,       # Minimum 2 credits for instant mode
    "research": 3,      # Minimum 3 credits for auto/research mode
    "agent": 5,         # Minimum 5 credits for agent mode
    "thinking": 3,
    "code": 3,
    "hybrid": 3,
    "swarm": 5,
}

# Mode minimum required balance to start
MODE_MIN_BALANCE = {
    "instant": 3,       # Need at least 3 credits to start instant
    "research": 5,      # Need at least 5 credits to start research
    "agent": 10,        # Need at least 10 credits to start agent
    "thinking": 5,
    "code": 5,
    "hybrid": 5,
    "swarm": 10,
}


@dataclass
class BillingResult:
    success: bool
    credits_used: int
    remaining_balance: int
    margin_usd: Decimal
    should_pause: bool = False
    error: Optional[str] = None


@dataclass
class TaskSummary:
    task_id: str
    total_credits: int
    total_apis: int
    total_margin_usd: Decimal
    reasoning_steps: int
    status: str


@dataclass
class RunningTaskTracker:
    """Tracks credits consumed during a running task"""
    task_id: str
    user_id: str
    mode: str
    total_deducted: int = 0
    operations: list = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)


class CreditService:
    """
    Real-time usage-based credit billing service.
    Credits are deducted incrementally as operations are performed,
    similar to Manus AI's credit system.
    """

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.min_credits_to_start = 3
        self.low_balance_threshold = 10
        # In-memory task trackers for real-time billing
        self._active_tasks: Dict[str, RunningTaskTracker] = {}

    # ========================================================================
    # USER CREDIT MANAGEMENT
    # ========================================================================

    async def get_credit_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's complete credit status"""
        try:
            try:
                response = self.supabase.table("user_credit_summary")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .execute()
                if response.data and len(response.data) > 0:
                    return response.data[0]
            except Exception:
                pass

            response = self.supabase.table("user_credits")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()

            if response.data and len(response.data) > 0:
                data = response.data[0]
                return {
                    "user_id": user_id,
                    "balance": data.get("balance", 0),
                    "lifetime_purchased": data.get("lifetime_purchased", 0),
                    "plan": "free",
                    "daily_credits_available": True,
                }

            return await self._ensure_user_credits(user_id)
        except Exception as e:
            print(f"Error getting credit summary: {e}")
            return {"user_id": user_id, "balance": 0, "plan": "free"}

    async def get_balance(self, user_id: str) -> int:
        """Get user's current credit balance"""
        try:
            response = self.supabase.table("user_credits")\
                .select("balance")\
                .eq("user_id", user_id)\
                .execute()
            return response.data[0].get("balance", 0) if response.data and len(response.data) > 0 else 0
        except Exception:
            try:
                result = await self._ensure_user_credits(user_id)
                return result.get("balance", 0)
            except Exception:
                return 0

    async def has_sufficient_credits(self, user_id: str, min_required: int = 3) -> bool:
        """Check if user has enough credits to proceed"""
        balance = await self.get_balance(user_id)
        return balance >= min_required

    async def get_min_required_for_mode(self, mode: str) -> int:
        """Get minimum credits required to start a mode"""
        return MODE_MIN_BALANCE.get(mode, 5)

    async def _ensure_user_credits(self, user_id: str) -> Dict[str, Any]:
        """Ensure user has a credit record, create if missing"""
        try:
            response = self.supabase.table("user_credits")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
        except Exception:
            pass

        try:
            response = self.supabase.table("user_credits")\
                .insert({
                    "user_id": user_id,
                    "balance": 50,
                    "lifetime_purchased": 0,
                })\
                .execute()
            return response.data[0] if response.data else {"user_id": user_id, "balance": 50}
        except Exception as e:
            print(f"Error creating user credits: {e}")
            return {"user_id": user_id, "balance": 50}

    # ========================================================================
    # REAL-TIME CREDIT DEDUCTION (Manus AI style)
    # ========================================================================

    async def start_billing_session(self, user_id: str, mode: str) -> Optional[str]:
        """
        Start a billing session for a task. Returns a session_id.
        Deducts the base cost immediately.
        """
        min_required = MODE_MIN_BALANCE.get(mode, 5)
        balance = await self.get_balance(user_id)
        if balance < min_required:
            return None

        session_id = str(uuid.uuid4())[:12]
        base_cost = MODE_BASE_COSTS.get(mode, 3)

        # Deduct base cost immediately
        result = await self.deduct_credits(user_id, base_cost, f"base_{mode}")
        if not result.success:
            return None

        # Track the session
        self._active_tasks[session_id] = RunningTaskTracker(
            task_id=session_id,
            user_id=user_id,
            mode=mode,
            total_deducted=base_cost,
            operations=[{"op": f"base_{mode}", "cost": base_cost, "ts": datetime.utcnow().isoformat()}],
        )

        return session_id

    async def bill_operation(
        self,
        session_id: str,
        operation: str,
        units: float = 1.0,
        context: str = ""
    ) -> BillingResult:
        """
        Bill for a specific operation during task execution.
        Deducts credits in real-time as each operation completes.
        Returns the billing result with updated balance.
        """
        tracker = self._active_tasks.get(session_id)
        if not tracker:
            # No active session — skip billing (non-blocking)
            return BillingResult(
                success=True, credits_used=0, remaining_balance=0, margin_usd=Decimal("0")
            )

        # Calculate cost for this operation
        base_cost = OPERATION_COSTS.get(operation, 1)
        cost = max(1, int(base_cost * units))

        # Check if user still has credits
        balance = await self.get_balance(tracker.user_id)
        if balance < cost:
            # Insufficient credits — deduct what's available, then signal pause
            if balance > 0:
                result = await self.deduct_credits(tracker.user_id, balance, f"{operation}")
                tracker.total_deducted += balance
                tracker.operations.append({
                    "op": operation, "cost": balance, "context": context,
                    "ts": datetime.utcnow().isoformat(), "partial": True
                })
                return BillingResult(
                    success=True,
                    credits_used=balance,
                    remaining_balance=0,
                    margin_usd=Decimal("0"),
                    should_pause=True,
                    error="Low credits - task may be limited"
                )
            return BillingResult(
                success=False, credits_used=0, remaining_balance=0,
                margin_usd=Decimal("0"), should_pause=True,
                error="Insufficient credits"
            )

        # Deduct the operation cost
        result = await self.deduct_credits(tracker.user_id, cost, f"{operation}")
        if result.success:
            tracker.total_deducted += cost
            tracker.operations.append({
                "op": operation, "cost": cost, "context": context,
                "ts": datetime.utcnow().isoformat()
            })

        return result

    async def end_billing_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        End a billing session and return the summary.
        """
        tracker = self._active_tasks.pop(session_id, None)
        if not tracker:
            return None

        summary = {
            "session_id": session_id,
            "user_id": tracker.user_id,
            "mode": tracker.mode,
            "total_credits_used": tracker.total_deducted,
            "operations_count": len(tracker.operations),
            "operations": tracker.operations,
            "duration_seconds": (datetime.utcnow() - tracker.started_at).total_seconds(),
        }

        return summary

    # ========================================================================
    # CORE CREDIT OPERATIONS
    # ========================================================================

    async def deduct_credits(self, user_id: str, amount: int, reason: str = "chat") -> BillingResult:
        """
        Directly deduct credits from user's balance.
        Core billing operation - simple and reliable.
        """
        try:
            current_balance = await self.get_balance(user_id)

            if current_balance < amount:
                return BillingResult(
                    success=False,
                    credits_used=0,
                    remaining_balance=current_balance,
                    margin_usd=Decimal("0"),
                    error="Insufficient credits"
                )

            new_balance = current_balance - amount

            self.supabase.table("user_credits")\
                .update({
                    "balance": new_balance,
                    "updated_at": datetime.utcnow().isoformat()
                })\
                .eq("user_id", user_id)\
                .execute()

            # Sync to users table
            try:
                self.supabase.table("users")\
                    .update({"credit_balance": new_balance})\
                    .eq("id", user_id)\
                    .execute()
            except Exception:
                pass

            # Log the transaction
            try:
                self.supabase.table("credit_transactions")\
                    .insert({
                        "user_id": user_id,
                        "amount": -amount,
                        "balance_after": new_balance,
                        "type": "deduction",
                        "description": f"Credit deduction: {reason}",
                    })\
                    .execute()
            except Exception:
                pass

            return BillingResult(
                success=True,
                credits_used=amount,
                remaining_balance=new_balance,
                margin_usd=Decimal("0"),
            )
        except Exception as e:
            print(f"Credit deduction error: {e}")
            return BillingResult(
                success=False, credits_used=0, remaining_balance=0,
                margin_usd=Decimal("0"), error=str(e)
            )

    async def add_credits(self, user_id: str, amount: int, reason: str = "purchase") -> BillingResult:
        """Add credits to user's balance"""
        try:
            current_balance = await self.get_balance(user_id)
            new_balance = current_balance + amount

            update_data = {
                "balance": new_balance,
                "updated_at": datetime.utcnow().isoformat()
            }
            if reason == "purchase":
                try:
                    resp = self.supabase.table("user_credits")\
                        .select("lifetime_purchased")\
                        .eq("user_id", user_id)\
                        .execute()
                    current_lifetime = resp.data[0].get("lifetime_purchased", 0) if resp.data and len(resp.data) > 0 else 0
                    update_data["lifetime_purchased"] = current_lifetime + amount
                except Exception:
                    pass

            self.supabase.table("user_credits")\
                .update(update_data)\
                .eq("user_id", user_id)\
                .execute()

            try:
                self.supabase.table("users")\
                    .update({"credit_balance": new_balance})\
                    .eq("id", user_id)\
                    .execute()
            except Exception:
                pass

            try:
                self.supabase.table("credit_transactions")\
                    .insert({
                        "user_id": user_id,
                        "amount": amount,
                        "balance_after": new_balance,
                        "type": "credit",
                        "description": f"Credits added: {reason}",
                    })\
                    .execute()
            except Exception:
                pass

            return BillingResult(
                success=True, credits_used=0, remaining_balance=new_balance,
                margin_usd=Decimal("0"),
            )
        except Exception as e:
            print(f"Credit addition error: {e}")
            return BillingResult(
                success=False, credits_used=0, remaining_balance=0,
                margin_usd=Decimal("0"), error=str(e)
            )

    # ========================================================================
    # DAILY / MONTHLY CREDITS
    # ========================================================================

    async def claim_daily_credits(self, user_id: str) -> Dict[str, Any]:
        """Claim daily free credits"""
        try:
            try:
                result = self.supabase.rpc("claim_daily_credits", {"p_user_id": user_id}).execute()
                if result.data:
                    data = result.data[0] if isinstance(result.data, list) else result.data
                    if data.get("success"):
                        return data
            except Exception:
                pass

            try:
                resp = self.supabase.table("user_credits")\
                    .select("last_daily_claim, balance")\
                    .eq("user_id", user_id)\
                    .execute()

                if resp.data and len(resp.data) > 0:
                    resp.data = resp.data[0]
                    last_claim = resp.data.get("last_daily_claim")
                    current_balance = resp.data.get("balance", 0)

                    if last_claim:
                        last_claim_dt = datetime.fromisoformat(last_claim.replace("Z", "+00:00"))
                        now = datetime.utcnow().replace(tzinfo=last_claim_dt.tzinfo)
                        if (now - last_claim_dt).total_seconds() < 86400:
                            return {"success": False, "credits_granted": 0, "message": "Daily credits already claimed"}

                    daily_credits = 50
                    new_balance = current_balance + daily_credits

                    self.supabase.table("user_credits")\
                        .update({
                            "balance": new_balance,
                            "last_daily_claim": datetime.utcnow().isoformat(),
                            "updated_at": datetime.utcnow().isoformat()
                        })\
                        .eq("user_id", user_id)\
                        .execute()

                    try:
                        self.supabase.table("users")\
                            .update({"credit_balance": new_balance})\
                            .eq("id", user_id)\
                            .execute()
                    except Exception:
                        pass

                    return {
                        "success": True,
                        "credits_granted": daily_credits,
                        "new_balance": new_balance,
                        "streak": 1
                    }
            except Exception as e:
                print(f"Daily credits fallback error: {e}")

            return {"success": False, "credits_granted": 0, "error": "Failed to claim daily credits"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def claim_monthly_bonus(self, user_id: str) -> Dict[str, Any]:
        """Claim monthly bonus credits (Paid tiers only)"""
        try:
            result = self.supabase.rpc("claim_monthly_bonus", {"p_user_id": user_id}).execute()
            return result.data[0] if result.data else {"success": False, "credits_granted": 0}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================================
    # LEGACY COMPATIBILITY (bill_consumption, start_task, complete_task)
    # ========================================================================

    async def start_task(
        self, user_id: str, task_type: str, module_type: str = "search",
        conversation_id: Optional[str] = None, input_data: Optional[Dict] = None,
        estimated_credits: Optional[int] = None
    ) -> Optional[str]:
        """Legacy: Start a task (now wraps start_billing_session)"""
        return await self.start_billing_session(user_id, task_type)

    async def bill_consumption(
        self, task_id: str, api_service: str, api_operation: str,
        units: float = 1.0, reasoning_step: int = 0,
        reasoning_context: Optional[str] = None, metadata: Optional[Dict] = None
    ) -> BillingResult:
        """Legacy: Bill for API usage (now wraps bill_operation)"""
        operation_key = f"{api_service}_{api_operation}"
        # Map to known operations
        if "search" in api_service:
            operation_key = f"search_{api_operation}" if f"search_{api_operation}" in OPERATION_COSTS else "search_brave"
        elif "llm" in api_service or "kimi" in api_service:
            operation_key = "llm_kimi_stream"
        elif "grok" in api_service:
            operation_key = "llm_grok_stream"
        return await self.bill_operation(task_id, operation_key, units, reasoning_context or "")

    async def complete_task(
        self, task_id: str, status: str = "completed",
        output_data: Optional[Dict] = None, user_id: Optional[str] = None,
        credits_to_deduct: Optional[int] = None
    ) -> Optional[TaskSummary]:
        """Legacy: Complete task (now wraps end_billing_session)"""
        summary = await self.end_billing_session(task_id)
        total = summary.get("total_credits_used", 0) if summary else 0
        return TaskSummary(
            task_id=task_id, total_credits=total, total_apis=0,
            total_margin_usd=Decimal("0"), reasoning_steps=0, status=status
        )

    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        try:
            result = self.supabase.rpc("resume_task", {"p_task_id": task_id}).execute()
            return result.data if result.data else False
        except Exception:
            return False

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status"""
        try:
            response = self.supabase.table("active_tasks")\
                .select("*")\
                .eq("id", task_id)\
                .execute()
            return response.data[0] if response.data and len(response.data) > 0 else None
        except Exception:
            return None

    # ========================================================================
    # CREDIT PURCHASE
    # ========================================================================

    async def get_credit_price(self, user_id: str, credits_amount: int) -> Dict[str, Any]:
        """Get price quote for credit purchase"""
        try:
            result = self.supabase.rpc("get_credit_price", {
                "p_user_id": user_id,
                "p_credits": credits_amount
            }).execute()
            return result.data[0] if result.data else {}
        except Exception:
            price_per_credit = 0.01
            return {
                "credits": credits_amount,
                "price_usd": round(credits_amount * price_per_credit, 2),
                "price_per_credit": price_per_credit
            }

    async def purchase_credits(
        self, user_id: str, credits_amount: int,
        stripe_payment_intent_id: str, package_slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process credit purchase after Stripe payment"""
        try:
            try:
                result = self.supabase.rpc("purchase_credits", {
                    "p_user_id": user_id,
                    "p_credits": credits_amount,
                    "p_stripe_payment_intent_id": stripe_payment_intent_id,
                    "p_package_slug": package_slug
                }).execute()
                if result.data:
                    return result.data[0] if isinstance(result.data, list) else result.data
            except Exception:
                pass

            billing_result = await self.add_credits(user_id, credits_amount, "purchase")
            return {
                "success": billing_result.success,
                "new_balance": billing_result.remaining_balance,
                "credits_added": credits_amount
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_credit_packages(self) -> List[Dict[str, Any]]:
        """Get available credit packages"""
        try:
            response = self.supabase.table("credit_packages")\
                .select("*")\
                .eq("is_active", True)\
                .order("display_order")\
                .execute()
            return response.data or []
        except Exception:
            return [
                {"slug": "starter", "name": "Starter", "credits": 500, "price_usd": 4.99, "display_order": 1, "is_active": True},
                {"slug": "pro", "name": "Pro", "credits": 2000, "price_usd": 14.99, "display_order": 2, "is_active": True},
                {"slug": "business", "name": "Business", "credits": 10000, "price_usd": 49.99, "display_order": 3, "is_active": True},
            ]

    # ========================================================================
    # USAGE ANALYTICS
    # ========================================================================

    async def get_usage_history(
        self, user_id: str, days: int = 30, api_service: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get detailed usage history"""
        try:
            try:
                query = self.supabase.table("credit_transactions")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .gte("created_at", (datetime.utcnow() - timedelta(days=days)).isoformat())\
                    .order("created_at", desc=True)\
                    .limit(100)
                response = query.execute()
                if response.data:
                    return response.data
            except Exception:
                pass

            query = self.supabase.table("credit_consumption")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("created_at", (datetime.utcnow() - timedelta(days=days)).isoformat())\
                .order("created_at", desc=True)

            if api_service:
                query = query.eq("api_service", api_service)

            response = query.execute()
            return response.data or []
        except Exception:
            return []

    async def get_active_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's running tasks"""
        try:
            response = self.supabase.table("active_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "running")\
                .order("created_at", desc=True)\
                .execute()
            return response.data or []
        except Exception:
            return []

    async def get_task_consumption(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all consumption records for a task"""
        try:
            response = self.supabase.table("credit_consumption")\
                .select("*")\
                .eq("task_id", task_id)\
                .order("created_at")\
                .execute()
            return response.data or []
        except Exception:
            return []
