'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';
const DAILY_CLAIM_KEY = 'mcleuker_daily_credit_claim';

interface DailyCreditResult {
  claimed: boolean;
  creditsGranted: number;
  newBalance: number;
  streak: number;
  error?: string;
}

/**
 * Hook that automatically claims daily credits when the user opens the dashboard.
 * Uses localStorage to track the last claim date and avoids redundant API calls.
 * 
 * The claim happens:
 * 1. On first dashboard load of the day
 * 2. Silently in the background (no UI blocking)
 * 3. Only once per calendar day per user
 */
export function useDailyCredits() {
  const { user, session } = useAuth();
  const hasAttempted = useRef(false);
  const [lastResult, setLastResult] = useState<DailyCreditResult | null>(null);

  const getLastClaimDate = useCallback((userId: string): string | null => {
    try {
      const stored = localStorage.getItem(`${DAILY_CLAIM_KEY}_${userId}`);
      return stored;
    } catch {
      return null;
    }
  }, []);

  const setLastClaimDate = useCallback((userId: string) => {
    try {
      const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
      localStorage.setItem(`${DAILY_CLAIM_KEY}_${userId}`, today);
    } catch {
      // localStorage not available
    }
  }, []);

  const claimDailyCredits = useCallback(async () => {
    if (!user?.id || !session?.access_token) return;

    // Check if already claimed today
    const today = new Date().toISOString().split('T')[0];
    const lastClaim = getLastClaimDate(user.id);
    if (lastClaim === today) {
      return; // Already claimed today
    }

    try {
      const res = await fetch(`${API_URL}/api/v1/billing/credits/claim-daily`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await res.json();

      if (data.success && data.credits_granted > 0) {
        setLastClaimDate(user.id);
        setLastResult({
          claimed: true,
          creditsGranted: data.credits_granted,
          newBalance: data.new_balance,
          streak: data.streak || 0,
        });
        console.log(`[DailyCredits] Claimed ${data.credits_granted} credits. New balance: ${data.new_balance}`);
      } else if (data.success) {
        // Already claimed via server-side check
        setLastClaimDate(user.id);
        setLastResult({
          claimed: false,
          creditsGranted: 0,
          newBalance: data.new_balance || 0,
          streak: data.streak || 0,
        });
      } else {
        // Claim failed but mark as attempted to avoid spam
        setLastClaimDate(user.id);
        setLastResult({
          claimed: false,
          creditsGranted: 0,
          newBalance: 0,
          streak: 0,
          error: data.error || 'Claim failed',
        });
      }
    } catch (err) {
      console.warn('[DailyCredits] Failed to claim daily credits:', err);
      // Don't mark as claimed on network error - will retry next page load
    }
  }, [user?.id, session?.access_token, getLastClaimDate, setLastClaimDate]);

  // Auto-claim on mount (dashboard load)
  useEffect(() => {
    if (hasAttempted.current) return;
    if (!user?.id || !session?.access_token) return;

    hasAttempted.current = true;

    // Small delay to not block initial render
    const timer = setTimeout(() => {
      claimDailyCredits();
    }, 2000);

    return () => clearTimeout(timer);
  }, [user?.id, session?.access_token, claimDailyCredits]);

  return {
    lastResult,
    claimDailyCredits, // Manual trigger if needed
  };
}
