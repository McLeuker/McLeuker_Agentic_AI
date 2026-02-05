'use client';

import { useEffect, useState, Suspense, useCallback, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/integrations/supabase/client';

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState('Processing authentication...');
  const [error, setError] = useState<string | null>(null);
  const processedRef = useRef(false);

  const handleAuthCallback = useCallback(async () => {
    // Prevent double processing
    if (processedRef.current) return;
    processedRef.current = true;

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
      
      // Get the code from URL for PKCE flow
      const code = searchParams.get('code');
      
      if (code) {
        setStatus('Completing authentication...');
        
        // Exchange code for session
        const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
        
        if (exchangeError) {
          console.error('Code exchange error:', exchangeError);
          
          // If code already used, check if we have a session
          if (exchangeError.message?.includes('already used') || exchangeError.message?.includes('expired')) {
            const { data: sessionData } = await supabase.auth.getSession();
            if (sessionData.session) {
              // Session exists, redirect
              setStatus('Session found! Redirecting...');
              const returnTo = localStorage.getItem('auth-return-to') || '/dashboard';
              localStorage.removeItem('auth-return-to');
              router.replace(returnTo);
              return;
            }
          }
          
          setError(exchangeError.message);
          setStatus('Authentication failed');
          setTimeout(() => router.replace('/login?error=exchange_failed'), 2000);
          return;
        }
        
        if (data.session) {
          setStatus('Authentication successful!');
          
          // Store session confirmation in localStorage
          localStorage.setItem('mcleuker-session-confirmed', 'true');
          localStorage.setItem('mcleuker-user-id', data.session.user.id);
          
          // Get return URL
          const returnTo = localStorage.getItem('auth-return-to') || '/dashboard';
          localStorage.removeItem('auth-return-to');
          
          // Small delay to ensure session is propagated
          await new Promise(resolve => setTimeout(resolve, 300));
          
          // Use router.replace for smoother navigation
          router.replace(returnTo);
          return;
        }
      }
      
      // No code, check for existing session
      const { data: sessionData } = await supabase.auth.getSession();
      
      if (sessionData.session) {
        setStatus('Session found! Redirecting...');
        const returnTo = localStorage.getItem('auth-return-to') || '/dashboard';
        localStorage.removeItem('auth-return-to');
        router.replace(returnTo);
        return;
      }
      
      // No session found
      setStatus('No session found. Redirecting to login...');
      setTimeout(() => router.replace('/login'), 1500);
      
    } catch (err) {
      console.error('Unexpected auth callback error:', err);
      setError('An unexpected error occurred');
      setStatus('Authentication error');
      setTimeout(() => router.replace('/login?error=unexpected'), 2000);
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
            <div className="w-12 h-12 border-4 border-[#3d655c] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-white/60">{status}</p>
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
        <div className="w-12 h-12 border-4 border-[#3d655c] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
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
