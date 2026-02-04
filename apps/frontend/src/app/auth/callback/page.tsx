'use client';

import { useEffect, useState, Suspense, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/integrations/supabase/client';

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState('Processing authentication...');
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(true);

  const handleAuthCallback = useCallback(async () => {
    try {
      // Check for error in URL params
      const urlError = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');
      
      if (urlError) {
        console.error('OAuth error:', urlError, errorDescription);
        setError(errorDescription || urlError);
        setStatus('Authentication failed');
        setTimeout(() => router.replace('/login?error=oauth_failed'), 2000);
        return;
      }

      setStatus('Verifying session...');
      
      // CRITICAL FIX: Wait for Supabase to fully process the URL hash/code
      // This prevents the "flash" where session isn't detected immediately
      let retries = 0;
      const maxRetries = 5;
      let session = null;
      
      while (retries < maxRetries && !session) {
        // Wait before checking (increases with each retry)
        await new Promise(resolve => setTimeout(resolve, 300 + (retries * 200)));
        
        // Try to get session
        const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) {
          console.error('Session error on retry', retries, ':', sessionError);
        } else if (sessionData.session) {
          session = sessionData.session;
          break;
        }
        
        // If no session, try code exchange for PKCE flow
        const code = searchParams.get('code');
        if (code && retries === 0) {
          setStatus('Completing authentication...');
          const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
          
          if (!exchangeError && data.session) {
            session = data.session;
            break;
          } else if (exchangeError) {
            console.error('Code exchange error:', exchangeError);
          }
        }
        
        retries++;
        setStatus(`Verifying session... (attempt ${retries + 1})`);
      }
      
      if (session) {
        setStatus('Authentication successful! Redirecting...');
        
        // CRITICAL: Force a session refresh to ensure it's properly stored
        await supabase.auth.refreshSession();
        
        // Get the return URL from localStorage
        const returnTo = typeof window !== 'undefined' 
          ? localStorage.getItem('auth-return-to') || '/dashboard'
          : '/dashboard';
        
        // Clear the return URL
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-return-to');
        }
        
        // Small delay to ensure session is fully propagated
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Use window.location for a full page reload to ensure auth state is fresh
        window.location.href = returnTo;
      } else {
        // No session found after all retries
        setStatus('Session verification failed. Redirecting to login...');
        setError('Could not verify your session. Please try again.');
        setTimeout(() => router.replace('/login?error=session_not_found'), 2000);
      }
    } catch (err) {
      console.error('Unexpected auth callback error:', err);
      setError('An unexpected error occurred');
      setStatus('Authentication error');
      setTimeout(() => router.replace('/login?error=unexpected'), 2000);
    } finally {
      setIsProcessing(false);
    }
  }, [router, searchParams]);

  useEffect(() => {
    handleAuthCallback();
  }, [handleAuthCallback]);

  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center">
      <div className="text-center max-w-md px-4">
        {!error ? (
          <>
            <div className="w-12 h-12 border-4 border-[#177b57] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-white/60">{status}</p>
            {isProcessing && (
              <p className="text-white/30 text-xs mt-2">Please wait while we verify your session...</p>
            )}
          </>
        ) : (
          <>
            <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="text-white/80 font-medium mb-2">{status}</p>
            <p className="text-white/40 text-sm">{error}</p>
            <p className="text-white/30 text-xs mt-4">Redirecting to login...</p>
          </>
        )}
      </div>
    </div>
  );
}

function LoadingFallback() {
  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-[#177b57] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-white/60">Loading...</p>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <AuthCallbackContent />
    </Suspense>
  );
}
