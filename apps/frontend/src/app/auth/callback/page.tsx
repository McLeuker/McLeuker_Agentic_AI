'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/integrations/supabase/client';

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState('Processing authentication...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    let timeoutId: NodeJS.Timeout;

    const handleAuthCallback = async () => {
      try {
        // Check for error in URL params
        const urlError = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');
        
        if (urlError) {
          console.error('OAuth error:', urlError, errorDescription);
          if (mounted) {
            setError(errorDescription || urlError);
            setStatus('Authentication failed');
          }
          timeoutId = setTimeout(() => {
            if (mounted) router.replace('/login?error=oauth_failed');
          }, 2000);
          return;
        }

        // For implicit flow, the hash contains the access token
        // Supabase's detectSessionInUrl should handle this automatically
        if (mounted) setStatus('Verifying session...');
        
        // Wait a moment for Supabase to process the URL hash
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Check for session
        const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) {
          console.error('Session error:', sessionError);
          if (mounted) {
            setError(sessionError.message);
            setStatus('Failed to verify session');
          }
          timeoutId = setTimeout(() => {
            if (mounted) router.replace('/login?error=session_failed');
          }, 2000);
          return;
        }

        if (sessionData.session) {
          if (mounted) setStatus('Authentication successful! Redirecting...');
          
          // Get the return URL from localStorage
          const returnTo = typeof window !== 'undefined' 
            ? localStorage.getItem('auth-return-to') || '/dashboard'
            : '/dashboard';
          
          // Clear the return URL
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth-return-to');
          }
          
          // Redirect to dashboard
          timeoutId = setTimeout(() => {
            if (mounted) router.replace(returnTo);
          }, 300);
        } else {
          // No session found, try to handle code exchange for PKCE flow
          const code = searchParams.get('code');
          
          if (code) {
            if (mounted) setStatus('Completing authentication...');
            
            const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
            
            if (exchangeError) {
              console.error('Code exchange error:', exchangeError);
              if (mounted) {
                setError(exchangeError.message);
                setStatus('Failed to complete authentication');
              }
              timeoutId = setTimeout(() => {
                if (mounted) router.replace('/login?error=exchange_failed');
              }, 2000);
              return;
            }

            if (data.session) {
              if (mounted) setStatus('Authentication successful! Redirecting...');
              
              const returnTo = typeof window !== 'undefined' 
                ? localStorage.getItem('auth-return-to') || '/dashboard'
                : '/dashboard';
              
              if (typeof window !== 'undefined') {
                localStorage.removeItem('auth-return-to');
              }
              
              timeoutId = setTimeout(() => {
                if (mounted) router.replace(returnTo);
              }, 300);
              return;
            }
          }
          
          // No session and no code, redirect to login
          if (mounted) setStatus('No session found. Redirecting to login...');
          timeoutId = setTimeout(() => {
            if (mounted) router.replace('/login');
          }, 1500);
        }
      } catch (err) {
        console.error('Unexpected auth callback error:', err);
        if (mounted) {
          setError('An unexpected error occurred');
          setStatus('Authentication error');
        }
        timeoutId = setTimeout(() => {
          if (mounted) router.replace('/login?error=unexpected');
        }, 2000);
      }
    };

    handleAuthCallback();

    return () => {
      mounted = false;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [router, searchParams]);

  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center">
      <div className="text-center max-w-md px-4">
        {!error ? (
          <>
            <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
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
        <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
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
