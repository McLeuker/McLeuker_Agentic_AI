'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/integrations/supabase/client';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState('Processing authentication...');

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Check for error in URL params
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');
        
        if (error) {
          console.error('OAuth error:', error, errorDescription);
          setStatus(`Authentication failed: ${errorDescription || error}`);
          setTimeout(() => router.push('/login?error=oauth_failed'), 2000);
          return;
        }

        // Check for auth code in URL (for PKCE flow)
        const code = searchParams.get('code');
        
        if (code) {
          setStatus('Exchanging authorization code...');
          // Exchange the code for a session
          const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
          
          if (exchangeError) {
            console.error('Code exchange error:', exchangeError);
            setStatus('Failed to complete authentication');
            setTimeout(() => router.push('/login?error=exchange_failed'), 2000);
            return;
          }

          if (data.session) {
            setStatus('Authentication successful! Redirecting...');
            router.push('/dashboard');
            return;
          }
        }

        // Fallback: Check if we already have a session (for implicit flow)
        setStatus('Checking session...');
        const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) {
          console.error('Session error:', sessionError);
          setStatus('Failed to verify session');
          setTimeout(() => router.push('/login?error=session_failed'), 2000);
          return;
        }

        if (sessionData.session) {
          setStatus('Session found! Redirecting...');
          router.push('/dashboard');
        } else {
          setStatus('No session found. Redirecting to login...');
          setTimeout(() => router.push('/login'), 1500);
        }
      } catch (err) {
        console.error('Unexpected auth callback error:', err);
        setStatus('An unexpected error occurred');
        setTimeout(() => router.push('/login?error=unexpected'), 2000);
      }
    };

    handleAuthCallback();
  }, [router, searchParams]);

  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-white/60">{status}</p>
      </div>
    </div>
  );
}
