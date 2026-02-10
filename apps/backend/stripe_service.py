"""
McLeuker AI - Stripe Integration Service
Handles subscriptions, credit purchases, and webhooks
"""

import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

from supabase import Client


class StripeService:
    """
    Stripe integration for subscriptions and credit purchases
    """
    
    def __init__(self, stripe_secret_key: str, supabase: Client, frontend_url: str = "https://mcleuker.com"):
        if stripe_secret_key:
            stripe.api_key = stripe_secret_key
        self.supabase = supabase
        self.webhook_secret = None
        self.frontend_url = frontend_url
    
    # ========================================================================
    # CUSTOMER MANAGEMENT
    # ========================================================================
    
    async def get_or_create_customer(self, user_id: str, email: str, name: Optional[str] = None) -> str:
        """Get or create Stripe customer for user"""
        try:
            response = self.supabase.table("user_subscriptions")\
                .select("stripe_customer_id")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if response.data and response.data.get("stripe_customer_id"):
                return response.data["stripe_customer_id"]
        except Exception:
            pass
        
        # Create new Stripe customer
        customer = stripe.Customer.create(
            email=email,
            name=name or email,
            metadata={
                "user_id": user_id,
                "platform": "mcleuker_ai"
            }
        )
        
        # Save customer ID
        try:
            self.supabase.table("user_subscriptions")\
                .update({"stripe_customer_id": customer.id})\
                .eq("user_id", user_id)\
                .execute()
        except Exception:
            pass
        
        return customer.id
    
    # ========================================================================
    # SUBSCRIPTION MANAGEMENT
    # ========================================================================
    
    async def create_subscription(
        self,
        user_id: str,
        email: str,
        plan_slug: str,
        billing_interval: str,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new subscription"""
        try:
            plan_response = self.supabase.table("pricing_plans")\
                .select("*")\
                .eq("slug", plan_slug)\
                .single()\
                .execute()
            
            if not plan_response.data:
                return {"error": "Plan not found"}
            
            plan = plan_response.data
            stripe_price_id = plan.get("stripe_yearly_price_id") if billing_interval == "year" else plan.get("stripe_monthly_price_id")
            
            if not stripe_price_id:
                return {"error": "Stripe price not configured for this plan. Please contact support."}
            
            customer_id = await self.get_or_create_customer(user_id, email)
            
            if payment_method_id:
                stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={"default_payment_method": payment_method_id}
                )
            
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": stripe_price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "user_id": user_id,
                    "plan_slug": plan_slug,
                    "billing_interval": billing_interval
                }
            )
            
            self.supabase.table("user_subscriptions").update({
                "stripe_subscription_id": subscription.id,
                "stripe_customer_id": customer_id,
                "stripe_payment_method_id": payment_method_id,
                "billing_interval": billing_interval,
                "plan_id": plan["id"],
                "status": "incomplete",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).execute()
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None,
                "status": subscription.status
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def cancel_subscription(self, user_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        """Cancel user subscription"""
        try:
            response = self.supabase.table("user_subscriptions")\
                .select("stripe_subscription_id")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not response.data or not response.data.get("stripe_subscription_id"):
                return {"error": "No active subscription found"}
            
            subscription_id = response.data["stripe_subscription_id"]
            
            if at_period_end:
                stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
                self.supabase.table("user_subscriptions").update({
                    "cancel_at_period_end": True,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("user_id", user_id).execute()
                return {"success": True, "cancel_at_period_end": True}
            else:
                stripe.Subscription.delete(subscription_id)
                self.supabase.table("user_subscriptions").update({
                    "status": "canceled",
                    "canceled_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("user_id", user_id).execute()
                return {"success": True, "canceled_immediately": True}
        except Exception as e:
            return {"error": str(e)}
    
    # ========================================================================
    # CREDIT PURCHASE
    # ========================================================================
    
    async def create_credit_purchase_intent(
        self,
        user_id: str,
        email: str,
        package_slug: str = None,
        custom_credits: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create Stripe PaymentIntent for credit purchase"""
        try:
            customer_id = await self.get_or_create_customer(user_id, email)
            
            if package_slug:
                package_response = self.supabase.table("credit_packages")\
                    .select("*")\
                    .eq("slug", package_slug)\
                    .single()\
                    .execute()
                
                if not package_response.data:
                    return {"error": "Package not found"}
                
                package = package_response.data
                credits = package["credits"]
                base_price_cents = package["base_price_cents"]
            else:
                credits = custom_credits or 1000
                base_price_cents = credits  # 1 cent per credit
            
            # Get price with potential annual discount
            from credit_service import CreditService
            credit_service = CreditService(self.supabase)
            price_info = await credit_service.get_credit_price(user_id, credits)
            
            final_price_cents = price_info.get("final_price_cents", base_price_cents)
            
            intent = stripe.PaymentIntent.create(
                amount=max(final_price_cents, 50),  # Stripe minimum $0.50
                currency="usd",
                customer=customer_id,
                automatic_payment_methods={"enabled": True},
                metadata={
                    "user_id": user_id,
                    "credits": credits,
                    "package_slug": package_slug or "custom",
                    "base_price_cents": base_price_cents,
                    "discount_percent": price_info.get("annual_discount_percent", 0),
                    "type": "credit_purchase"
                }
            )
            
            return {
                "client_secret": intent.client_secret,
                "credits": credits,
                "amount_cents": final_price_cents,
                "amount_dollars": final_price_cents / 100,
                "base_price_cents": base_price_cents,
                "discount_percent": price_info.get("annual_discount_percent", 0),
                "savings_cents": price_info.get("savings_cents", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ========================================================================
    # WEBHOOK HANDLING
    # ========================================================================
    
    def set_webhook_secret(self, secret: str):
        """Set webhook secret for verification"""
        self.webhook_secret = secret
    
    # Plan details for updating users table
    PLAN_DETAILS = {
        "free": {"daily_fresh_credits": 15, "monthly_credits": 450, "max_domains": 2},
        "standard": {"daily_fresh_credits": 50, "monthly_credits": 1500, "max_domains": 5},
        "pro": {"daily_fresh_credits": 300, "monthly_credits": 9000, "max_domains": 10},
        "enterprise": {"daily_fresh_credits": 500, "monthly_credits": 25000, "max_domains": 10},
    }

    def _update_user_plan(self, user_id: str, plan_slug: str, status: str = "active"):
        """Update the users table with plan details"""
        try:
            details = self.PLAN_DETAILS.get(plan_slug, self.PLAN_DETAILS["free"])
            self.supabase.table("users").update({
                "subscription_plan": plan_slug,
                "subscription_status": status,
                "daily_fresh_credits": details["daily_fresh_credits"],
                "monthly_credits": details["monthly_credits"],
                "max_domains": details["max_domains"],
            }).eq("id", user_id).execute()
        except Exception as e:
            print(f"Error updating user plan: {e}")

    async def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            if self.webhook_secret:
                event = stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
            else:
                data = payload if isinstance(payload, dict) else __import__('json').loads(payload)
                event = data
        except ValueError:
            return {"error": "Invalid payload"}
        except Exception as e:
            return {"error": str(e)}
        
        event_type = event.get("type", "") if isinstance(event, dict) else event["type"]
        event_data = event.get("data", {}).get("object", {}) if isinstance(event, dict) else event["data"]["object"]
        
        handlers = {
            "invoice.payment_succeeded": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_failed,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "payment_intent.succeeded": self._handle_payment_intent_succeeded,
            "checkout.session.completed": self._handle_checkout_completed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return await handler(event_data)
        
        return {"received": True, "type": event_type}
    
    async def _handle_checkout_completed(self, session: Dict) -> Dict[str, Any]:
        """Handle completed checkout session - update users table with plan"""
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        plan_slug = metadata.get("plan_slug")
        mode = session.get("mode")
        
        if mode == "subscription" and user_id and plan_slug:
            # Update users table with new plan
            self._update_user_plan(user_id, plan_slug, "active")
            # Also store stripe_customer_id in users table
            try:
                self.supabase.table("users").update({
                    "stripe_customer_id": session.get("customer"),
                    "billing_cycle": metadata.get("billing_interval", "month"),
                }).eq("id", user_id).execute()
            except Exception:
                pass
            return {"success": True, "event": "checkout.session.completed", "user_id": user_id, "plan": plan_slug}
        elif mode == "payment" and metadata.get("type") == "credit_purchase":
            # Credit purchase - credits will be added via payment_intent.succeeded
            return {"success": True, "event": "checkout.session.completed", "type": "credit_purchase"}
        
        return {"success": True, "event": "checkout.session.completed"}

    async def _handle_invoice_paid(self, invoice: Dict) -> Dict[str, Any]:
        """Handle successful subscription payment"""
        customer_id = invoice.get("customer")
        try:
            response = self.supabase.table("user_subscriptions")\
                .select("user_id, plan_id")\
                .eq("stripe_customer_id", customer_id)\
                .single()\
                .execute()
            
            if response.data:
                user_id = response.data["user_id"]
                self.supabase.table("user_subscriptions").update({
                    "status": "active",
                    "current_period_start": datetime.fromtimestamp(invoice["period_start"]).isoformat(),
                    "current_period_end": datetime.fromtimestamp(invoice["period_end"]).isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("user_id", user_id).execute()
                return {"success": True, "event": "invoice.paid", "user_id": user_id}
        except Exception as e:
            return {"error": str(e)}
        return {"success": True, "event": "invoice.paid"}
    
    async def _handle_invoice_failed(self, invoice: Dict) -> Dict[str, Any]:
        """Handle failed subscription payment"""
        customer_id = invoice.get("customer")
        try:
            response = self.supabase.table("user_subscriptions")\
                .select("user_id")\
                .eq("stripe_customer_id", customer_id)\
                .single()\
                .execute()
            if response.data:
                self.supabase.table("user_subscriptions").update({
                    "status": "past_due",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("user_id", response.data["user_id"]).execute()
        except Exception:
            pass
        return {"success": True, "event": "invoice.payment_failed"}
    
    async def _handle_subscription_updated(self, subscription: Dict) -> Dict[str, Any]:
        """Handle subscription update"""
        customer_id = subscription.get("customer")
        try:
            response = self.supabase.table("user_subscriptions")\
                .select("user_id")\
                .eq("stripe_customer_id", customer_id)\
                .single()\
                .execute()
            if response.data:
                self.supabase.table("user_subscriptions").update({
                    "status": subscription["status"],
                    "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("user_id", response.data["user_id"]).execute()
        except Exception:
            pass
        return {"success": True, "event": "subscription.updated"}
    
    async def _handle_subscription_deleted(self, subscription: Dict) -> Dict[str, Any]:
        """Handle subscription cancellation - downgrade to free"""
        customer_id = subscription.get("customer")
        try:
            response = self.supabase.table("user_subscriptions")\
                .select("user_id")\
                .eq("stripe_customer_id", customer_id)\
                .single()\
                .execute()
            if response.data:
                user_id = response.data["user_id"]
                free_plan = self.supabase.table("pricing_plans")\
                    .select("id")\
                    .eq("slug", "free")\
                    .single()\
                    .execute()
                if free_plan.data:
                    self.supabase.table("user_subscriptions").update({
                        "plan_id": free_plan.data["id"],
                        "status": "canceled",
                        "canceled_at": datetime.utcnow().isoformat(),
                        "stripe_subscription_id": None,
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("user_id", user_id).execute()
                # Downgrade user to free tier
                self._update_user_plan(user_id, "free", "canceled")
        except Exception:
            pass
        return {"success": True, "event": "subscription.deleted"}
    
    async def _handle_payment_intent_succeeded(self, payment_intent: Dict) -> Dict[str, Any]:
        """Handle successful credit purchase"""
        metadata = payment_intent.get("metadata", {})
        if metadata.get("type") != "credit_purchase":
            return {"success": True, "event": "payment_intent.succeeded", "type": "other"}
        
        user_id = metadata.get("user_id")
        credits = int(metadata.get("credits", 0))
        package_slug = metadata.get("package_slug")
        
        if not user_id or credits <= 0:
            return {"error": "Invalid payment intent metadata"}
        
        try:
            from credit_service import CreditService
            credit_service = CreditService(self.supabase)
            result = await credit_service.purchase_credits(
                user_id=user_id,
                credits_amount=credits,
                stripe_payment_intent_id=payment_intent["id"],
                package_slug=package_slug if package_slug != "custom" else None
            )
            return {
                "success": True,
                "event": "payment_intent.succeeded",
                "type": "credit_purchase",
                "user_id": user_id,
                "credits_added": result.get("credits_added", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ========================================================================
    # PORTAL
    # ========================================================================
    
    async def create_customer_portal_session(self, user_id: str) -> Dict[str, Any]:
        """Create Stripe Customer Portal session"""
        try:
            response = self.supabase.table("user_subscriptions")\
                .select("stripe_customer_id")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not response.data or not response.data.get("stripe_customer_id"):
                return {"error": "No Stripe customer found"}
            
            session = stripe.billing_portal.Session.create(
                customer=response.data["stripe_customer_id"],
                return_url=f"{self.frontend_url}/settings/billing"
            )
            return {"url": session.url}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_invoices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's Stripe invoices"""
        try:
            response = self.supabase.table("user_subscriptions")\
                .select("stripe_customer_id")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not response.data or not response.data.get("stripe_customer_id"):
                return []
            
            invoices = stripe.Invoice.list(
                customer=response.data["stripe_customer_id"],
                limit=10
            )
            return [{
                "id": inv["id"],
                "amount_due": inv["amount_due"],
                "amount_paid": inv["amount_paid"],
                "status": inv["status"],
                "created": inv["created"],
                "pdf_url": inv.get("invoice_pdf")
            } for inv in invoices["data"]]
        except Exception:
            return []
