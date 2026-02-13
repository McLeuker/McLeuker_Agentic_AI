'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

type CookiePreferences = {
  necessary: boolean;
  analytics: boolean;
  functional: boolean;
  marketing: boolean;
};

const COOKIE_CONSENT_KEY = 'mcleuker_cookie_consent';
const COOKIE_CONSENT_EXPIRY = 13 * 30 * 24 * 60 * 60 * 1000; // 13 months in ms

export function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    analytics: false,
    functional: false,
    marketing: false,
  });

  useEffect(() => {
    const stored = localStorage.getItem(COOKIE_CONSENT_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        const expiresAt = parsed.expiresAt || 0;
        if (Date.now() > expiresAt) {
          // Consent expired (13 months), re-ask
          localStorage.removeItem(COOKIE_CONSENT_KEY);
          setVisible(true);
        }
        // Consent still valid, don't show banner
      } catch {
        setVisible(true);
      }
    } else {
      setVisible(true);
    }
  }, []);

  const saveConsent = (prefs: CookiePreferences) => {
    const data = {
      preferences: prefs,
      timestamp: new Date().toISOString(),
      expiresAt: Date.now() + COOKIE_CONSENT_EXPIRY,
    };
    localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(data));
    setVisible(false);
  };

  const handleAcceptAll = () => {
    const allAccepted: CookiePreferences = {
      necessary: true,
      analytics: true,
      functional: true,
      marketing: true,
    };
    setPreferences(allAccepted);
    saveConsent(allAccepted);
  };

  const handleRejectAll = () => {
    const allRejected: CookiePreferences = {
      necessary: true,
      analytics: false,
      functional: false,
      marketing: false,
    };
    setPreferences(allRejected);
    saveConsent(allRejected);
  };

  const handleSavePreferences = () => {
    saveConsent(preferences);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[9999] p-4 md:p-6">
      <div className="max-w-2xl mx-auto bg-[#111111] border border-white/[0.1] rounded-2xl shadow-2xl shadow-black/50">
        <div className="p-6">
          {/* Main Banner */}
          <div className="mb-4">
            <h3 className="text-white font-medium text-lg mb-2">We value your privacy</h3>
            <p className="text-white/50 text-sm leading-relaxed">
              We use cookies to enhance your experience. Strictly necessary cookies are always active. You can choose to accept or reject non-essential cookies. Read our{' '}
              <Link href="/cookies" className="text-white/70 underline hover:text-white">Cookie Policy</Link> for details.
            </p>
          </div>

          {/* Detailed Preferences (toggle) */}
          {showDetails && (
            <div className="mb-4 space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/[0.04]">
                <div>
                  <p className="text-white/80 text-sm font-medium">Strictly Necessary</p>
                  <p className="text-white/40 text-xs">Authentication, security, session</p>
                </div>
                <div className="text-white/40 text-xs">Always active</div>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/[0.04]">
                <div>
                  <p className="text-white/80 text-sm font-medium">Analytics &amp; Performance</p>
                  <p className="text-white/40 text-xs">Usage statistics, performance monitoring</p>
                </div>
                <button
                  onClick={() => setPreferences(p => ({ ...p, analytics: !p.analytics }))}
                  className={`w-10 h-6 rounded-full transition-colors ${preferences.analytics ? 'bg-white' : 'bg-white/20'}`}
                >
                  <div className={`w-4 h-4 rounded-full bg-[#111111] transition-transform mx-1 ${preferences.analytics ? 'translate-x-4' : 'translate-x-0'}`} />
                </button>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/[0.04]">
                <div>
                  <p className="text-white/80 text-sm font-medium">Functional</p>
                  <p className="text-white/40 text-xs">Preferences, language, theme</p>
                </div>
                <button
                  onClick={() => setPreferences(p => ({ ...p, functional: !p.functional }))}
                  className={`w-10 h-6 rounded-full transition-colors ${preferences.functional ? 'bg-white' : 'bg-white/20'}`}
                >
                  <div className={`w-4 h-4 rounded-full bg-[#111111] transition-transform mx-1 ${preferences.functional ? 'translate-x-4' : 'translate-x-0'}`} />
                </button>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/[0.04]">
                <div>
                  <p className="text-white/80 text-sm font-medium">Marketing</p>
                  <p className="text-white/40 text-xs">Personalized communications</p>
                </div>
                <button
                  onClick={() => setPreferences(p => ({ ...p, marketing: !p.marketing }))}
                  className={`w-10 h-6 rounded-full transition-colors ${preferences.marketing ? 'bg-white' : 'bg-white/20'}`}
                >
                  <div className={`w-4 h-4 rounded-full bg-[#111111] transition-transform mx-1 ${preferences.marketing ? 'translate-x-4' : 'translate-x-0'}`} />
                </button>
              </div>
            </div>
          )}

          {/* Buttons - CNIL compliant: Reject All and Accept All have equal prominence */}
          <div className="flex flex-col sm:flex-row gap-3">
            {showDetails ? (
              <>
                <button
                  onClick={handleSavePreferences}
                  className="flex-1 px-4 py-2.5 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-colors"
                >
                  Save Preferences
                </button>
                <button
                  onClick={() => setShowDetails(false)}
                  className="flex-1 px-4 py-2.5 rounded-lg border border-white/20 text-white text-sm font-medium hover:bg-white/[0.05] transition-colors"
                >
                  Back
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleRejectAll}
                  className="flex-1 px-4 py-2.5 rounded-lg border border-white/20 text-white text-sm font-medium hover:bg-white/[0.05] transition-colors"
                >
                  Reject All
                </button>
                <button
                  onClick={() => setShowDetails(true)}
                  className="flex-1 px-4 py-2.5 rounded-lg border border-white/20 text-white text-sm font-medium hover:bg-white/[0.05] transition-colors"
                >
                  Customize
                </button>
                <button
                  onClick={handleAcceptAll}
                  className="flex-1 px-4 py-2.5 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-colors"
                >
                  Accept All
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
