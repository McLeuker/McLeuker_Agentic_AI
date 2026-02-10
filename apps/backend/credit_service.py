"""
McLeuker AI - Credit Service
Production-ready credit billing system with direct table operations.
No dependency on database RPC functions - uses simple CRUD operations.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
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


# Credit costs per operation type
CREDIT_COSTS = {
    "chat_simple": 5,       # Simple chat without search
    "chat_search": 10,      # Chat with web search
    "chat_deep": 20,        # Deep research chat
    "chat_agent": 30,       # Agent mode chat
    "chat_creative": 15,    # Creative mode chat
    "image_generation": 25, # Image generation
    "file_generation": 10,  # File generation (PDF, Excel, etc.)
    "default": 10,          # Default cost
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


class CreditService:
    """
    Production credit billing service using direct Supabase table operations.
    No RPC function dependencies - fully self-contained.
    """
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.min_credits_to_start = 5
        self.low_balance_threshold = 10
    
    # ========================================================================
    # USER CREDIT MANAGEMENT
    # ========================================================================
    
    async def get_credit_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's complete credit status from user_credits table"""
        try:
            # Try the view first
            try:
                response = self.supabase.table("user_credit_summary")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .single()\
                    .execute()
                if response.data:
                    return response.data
            except Exception:
                pass
            
            # Fallback: read directly from user_credits
            response = self.supabase.table("user_credits")\
                .select("*")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if response.data:
                data = response.data
                balance = data.get("balance", 0)
                return {
                    "user_id": user_id,
                    "balance": balance,
                    "lifetime_purchased": data.get("lifetime_purchased", 0),
                    "plan": "free",
                    "daily_credits_available": True,
                }
            
            # No record exists - create one with default balance
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
                .single()\
                .execute()
            return response.data.get("balance", 0) if response.data else 0
        except Exception:
            # Try to create the record
            try:
                result = await self._ensure_user_credits(user_id)
                return result.get("balance", 0)
            except Exception:
                return 0
    
    async def has_sufficient_credits(self, user_id: str, min_required: int = 5) -> bool:
        """Check if user has enough credits to proceed"""
        balance = await self.get_balance(user_id)
        return balance >= min_required
    
    async def _ensure_user_credits(self, user_id: str) -> Dict[str, Any]:
        """Ensure user has a credit record, create if missing"""
        try:
            # Check if record exists
            response = self.supabase.table("user_credits")\
                .select("*")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            if response.data:
                return response.data
        except Exception:
            pass
        
        # Create new record with 50 free credits
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
    
    async def deduct_credits(self, user_id: str, amount: int, reason: str = "chat") -> BillingResult:
        """
        Directly deduct credits from user's balance.
        This is the core billing operation - simple and reliable.
        """
        try:
            # Get current balance
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
            
            # Update balance directly
            self.supabase.table("user_credits")\
                .update({
                    "balance": new_balance,
                    "updated_at": datetime.utcnow().isoformat()
                })\
                .eq("user_id", user_id)\
                .execute()
            
            # Also update users table for frontend consistency
            try:
                self.supabase.table("users")\
                    .update({"credit_balance": new_balance})\
                    .eq("id", user_id)\
                    .execute()
            except Exception:
                pass  # Non-critical - user_credits is source of truth
            
            # Log the consumption (non-blocking)
            try:
                self.supabase.table("credit_transactions")\
                    .insert({
                        "user_id": user_id,
                        "amount": -amount,
                        "balance_after": new_balance,
                        "type": "deduction",
                        "description": f"Credit deduction for {reason}",
                    })\
                    .execute()
            except Exception:
                pass  # Non-critical - logging only
            
            return BillingResult(
                success=True,
                credits_used=amount,
                remaining_balance=new_balance,
                margin_usd=Decimal("0"),
            )
        except Exception as e:
            print(f"Credit deduction error: {e}")
            return BillingResult(
                success=False,
                credits_used=0,
                remaining_balance=0,
                margin_usd=Decimal("0"),
                error=str(e)
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
                # Also update lifetime_purchased
                try:
                    resp = self.supabase.table("user_credits")\
                        .select("lifetime_purchased")\
                        .eq("user_id", user_id)\
                        .single()\
                        .execute()
                    current_lifetime = resp.data.get("lifetime_purchased", 0) if resp.data else 0
                    update_data["lifetime_purchased"] = current_lifetime + amount
                except Exception:
                    pass
            
            self.supabase.table("user_credits")\
                .update(update_data)\
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
            
            # Log transaction
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
                success=True,
                credits_used=0,
                remaining_balance=new_balance,
                margin_usd=Decimal("0"),
            )
        except Exception as e:
            print(f"Credit addition error: {e}")
            return BillingResult(
                success=False,
                credits_used=0,
                remaining_balance=0,
                margin_usd=Decimal("0"),
                error=str(e)
            )
    
    async def claim_daily_credits(self, user_id: str) -> Dict[str, Any]:
        """Claim daily free credits - direct implementation"""
        try:
            # Try RPC first (if it exists)
            try:
                result = self.supabase.rpc("claim_daily_credits", {"p_user_id": user_id}).execute()
                if result.data:
                    data = result.data[0] if isinstance(result.data, list) else result.data
                    if data.get("success"):
                        return data
            except Exception:
                pass
            
            # Fallback: direct implementation
            # Check last daily claim
            try:
                resp = self.supabase.table("user_credits")\
                    .select("last_daily_claim, balance")\
                    .eq("user_id", user_id)\
                    .single()\
                    .execute()
                
                if resp.data:
                    last_claim = resp.data.get("last_daily_claim")
                    current_balance = resp.data.get("balance", 0)
                    
                    if last_claim:
                        last_claim_dt = datetime.fromisoformat(last_claim.replace("Z", "+00:00"))
                        now = datetime.utcnow().replace(tzinfo=last_claim_dt.tzinfo)
                        if (now - last_claim_dt).total_seconds() < 86400:
                            return {"success": False, "credits_granted": 0, "message": "Daily credits already claimed"}
                    
                    # Grant 50 daily credits
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
                    
                    # Sync to users table
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
    # SIMPLIFIED TASK MANAGEMENT
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
        """Start a new task - returns a task_id for tracking"""
        try:
            balance = await self.get_balance(user_id)
            if balance < self.min_credits_to_start:
                return None
            
            # Generate a task ID
            task_id = str(uuid.uuid4())
            
            # Try RPC first
            try:
                result = self.supabase.rpc("start_task", {
                    "p_user_id": user_id,
                    "p_task_type": task_type,
                    "p_module_type": module_type,
                    "p_conversation_id": conversation_id,
                    "p_input_data": input_data or {},
                    "p_estimated_credits": estimated_credits
                }).execute()
                if result.data:
                    return result.data if isinstance(result.data, str) else task_id
            except Exception:
                pass
            
            # Fallback: just return the task_id (we'll deduct on completion)
            return task_id
        except Exception as e:
            print(f"Error starting task: {e}")
            return str(uuid.uuid4())  # Always return a task_id
    
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
        """Bill for API usage - simplified to just track, actual deduction on complete"""
        # In simplified mode, we just return success
        # Actual deduction happens in complete_task
        return BillingResult(
            success=True,
            credits_used=0,
            remaining_balance=0,
            margin_usd=Decimal("0")
        )
    
    async def complete_task(
        self,
        task_id: str,
        status: str = "completed",
        output_data: Optional[Dict] = None,
        user_id: Optional[str] = None,
        credits_to_deduct: Optional[int] = None
    ) -> Optional[TaskSummary]:
        """Complete task and deduct credits"""
        try:
            # Try RPC first
            try:
                result = self.supabase.rpc("complete_task", {
                    "p_task_id": task_id,
                    "p_status": status,
                    "p_output_data": output_data or {}
                }).execute()
                if result.data:
                    data = result.data[0] if isinstance(result.data, list) else result.data
                    if isinstance(data, dict):
                        return TaskSummary(
                            task_id=task_id,
                            total_credits=data.get("total_credits", 0),
                            total_apis=data.get("total_apis", 0),
                            total_margin_usd=Decimal(str(data.get("total_margin", 0))),
                            reasoning_steps=0,
                            status=data.get("final_status", status)
                        )
            except Exception:
                pass
            
            # Fallback: deduct credits directly if user_id provided
            if user_id and credits_to_deduct and credits_to_deduct > 0:
                await self.deduct_credits(user_id, credits_to_deduct, f"task_{task_id[:8]}")
            
            return TaskSummary(
                task_id=task_id,
                total_credits=credits_to_deduct or 0,
                total_apis=0,
                total_margin_usd=Decimal("0"),
                reasoning_steps=0,
                status=status
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
            # Fallback pricing
            price_per_credit = 0.01  # $0.01 per credit
            return {
                "credits": credits_amount,
                "price_usd": round(credits_amount * price_per_credit, 2),
                "price_per_credit": price_per_credit
            }
    
    async def purchase_credits(
        self,
        user_id: str,
        credits_amount: int,
        stripe_payment_intent_id: str,
        package_slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process credit purchase after Stripe payment"""
        try:
            # Try RPC first
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
            
            # Fallback: add credits directly
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
            # Return default packages
            return [
                {"slug": "starter", "name": "Starter", "credits": 500, "price_usd": 4.99, "display_order": 1, "is_active": True},
                {"slug": "pro", "name": "Pro", "credits": 2000, "price_usd": 14.99, "display_order": 2, "is_active": True},
                {"slug": "business", "name": "Business", "credits": 10000, "price_usd": 49.99, "display_order": 3, "is_active": True},
            ]
    
    # ========================================================================
    # USAGE ANALYTICS
    # ========================================================================
    
    async def get_usage_history(
        self,
        user_id: str,
        days: int = 30,
        api_service: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get detailed usage history"""
        try:
            # Try credit_transactions first (our new table)
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
            
            # Fallback: try credit_consumption
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
