"""
McLeuker AI - Credit Service
Production-ready credit billing system with margin protection
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import asyncio

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


class CreditService:
    """
    Production credit billing service with real-time cost tracking
    """
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.min_credits_to_start = 10
        self.low_balance_threshold = 5
        self.max_negative_balance = -20
    
    # ========================================================================
    # USER CREDIT MANAGEMENT
    # ========================================================================
    
    async def get_credit_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's complete credit status"""
        try:
            response = self.supabase.table("user_credit_summary")\
                .select("*")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting credit summary: {e}")
            return None
    
    async def get_balance(self, user_id: str) -> int:
        """Get user's current credit balance"""
        try:
            response = self.supabase.table("user_credits")\
                .select("balance")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            return response.data.get("balance", 0) if response.data else 0
        except Exception:
            return 0
    
    async def has_sufficient_credits(self, user_id: str, min_required: int = 10) -> bool:
        """Check if user has enough credits to proceed"""
        balance = await self.get_balance(user_id)
        return balance >= min_required
    
    async def claim_daily_credits(self, user_id: str) -> Dict[str, Any]:
        """Claim daily free credits (Free tier only)"""
        try:
            result = self.supabase.rpc("claim_daily_credits", {"p_user_id": user_id}).execute()
            return result.data[0] if result.data else {"success": False, "credits_granted": 0}
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
    # TASK MANAGEMENT
    # ========================================================================
    
    async def start_task(
        self,
        user_id: str,
        task_type: str,
        module_type: str = "search",
        conversation_id: Optional[str] = None,
        input_data: Optional[Dict] = None,
        estimated_credits: Optional[int] = None
    ) -> Optional[str]:
        """Start a new task with credit reservation"""
        try:
            balance = await self.get_balance(user_id)
            if balance < self.min_credits_to_start:
                return None
            
            result = self.supabase.rpc("start_task", {
                "p_user_id": user_id,
                "p_task_type": task_type,
                "p_module_type": module_type,
                "p_conversation_id": conversation_id,
                "p_input_data": input_data or {},
                "p_estimated_credits": estimated_credits
            }).execute()
            return result.data
        except Exception as e:
            print(f"Error starting task: {e}")
            return None
    
    async def bill_consumption(
        self,
        task_id: str,
        api_service: str,
        api_operation: str,
        units: float = 1.0,
        reasoning_step: int = 0,
        reasoning_context: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> BillingResult:
        """Bill for API usage with real-time cost tracking"""
        try:
            result = self.supabase.rpc("bill_consumption", {
                "p_task_id": task_id,
                "p_api_service": api_service,
                "p_api_operation": api_operation,
                "p_units": units,
                "p_reasoning_step": reasoning_step,
                "p_reasoning_context": reasoning_context,
                "p_metadata": metadata or {}
            }).execute()
            
            data = result.data[0] if result.data else None
            if not data:
                return BillingResult(success=True, credits_used=0, remaining_balance=0, margin_usd=Decimal("0"))
            
            return BillingResult(
                success=data.get("success", True),
                credits_used=data.get("credits_used", 0),
                remaining_balance=data.get("remaining_balance", 0),
                margin_usd=Decimal(str(data.get("margin_usd", 0))),
                should_pause=data.get("should_pause", False)
            )
        except Exception as e:
            print(f"Billing error (non-blocking): {e}")
            return BillingResult(
                success=True,
                credits_used=0,
                remaining_balance=0,
                margin_usd=Decimal("0"),
                error=str(e)
            )
    
    async def complete_task(
        self,
        task_id: str,
        status: str = "completed",
        output_data: Optional[Dict] = None
    ) -> Optional[TaskSummary]:
        """Complete task and return financial summary"""
        try:
            result = self.supabase.rpc("complete_task", {
                "p_task_id": task_id,
                "p_status": status,
                "p_output_data": output_data or {}
            }).execute()
            
            data = result.data[0] if result.data else None
            if not data:
                return None
            
            return TaskSummary(
                task_id=task_id,
                total_credits=data.get("total_credits", 0),
                total_apis=data.get("total_apis", 0),
                total_margin_usd=Decimal(str(data.get("total_margin", 0))),
                reasoning_steps=0,
                status=data.get("final_status", status)
            )
        except Exception as e:
            print(f"Error completing task: {e}")
            return None
    
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
                .single()\
                .execute()
            return response.data
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
        except Exception as e:
            return {"error": str(e)}
    
    async def purchase_credits(
        self,
        user_id: str,
        credits_amount: int,
        stripe_payment_intent_id: str,
        package_slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process credit purchase after Stripe payment"""
        try:
            result = self.supabase.rpc("purchase_credits", {
                "p_user_id": user_id,
                "p_credits": credits_amount,
                "p_stripe_payment_intent_id": stripe_payment_intent_id,
                "p_package_slug": package_slug
            }).execute()
            return result.data[0] if result.data else {"error": "Purchase failed"}
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
            return []
    
    # ========================================================================
    # USAGE ANALYTICS
    # ========================================================================
    
    async def get_usage_history(
        self,
        user_id: str,
        days: int = 30,
        api_service: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get detailed usage history with cost breakdown"""
        try:
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
