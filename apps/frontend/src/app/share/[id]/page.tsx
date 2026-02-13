'use client';
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '@/integrations/supabase/client';
import { Loader2, ArrowLeft, MessageSquare, ThumbsUp, Copy, Check } from 'lucide-react';

interface SharedMessage {
  id: string;
  content: string;
  user_query: string;
  created_at: string;
}

export default function SharePage() {
  const params = useParams();
  const shareId = params.id as string;
  const [message, setMessage] = useState<SharedMessage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function loadSharedMessage() {
      try {
        const { data, error: fetchError } = await supabase
          .from('chat_messages')
          .select('*')
          .eq('id', shareId)
          .limit(1);

        if (fetchError) throw fetchError;
        if (!data || data.length === 0) {
          setError('This shared conversation could not be found or has expired.');
          return;
        }
        setMessage(data[0]);
      } catch (e) {
        console.error('Error loading shared message:', e);
        setError('Unable to load this shared conversation.');
      } finally {
        setLoading(false);
      }
    }

    if (shareId && shareId !== 'temp') {
      loadSharedMessage();
    } else {
      setError('Invalid share link.');
      setLoading(false);
    }
  }, [shareId]);

  const handleCopy = () => {
    if (message?.content) {
      navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Simple markdown-to-HTML renderer
  const renderContent = (content: string) => {
    return content.split('\n').map((line, i) => {
      if (line.startsWith('## ')) return <h2 key={i} className="text-lg font-semibold text-white mt-4 mb-2">{line.slice(3)}</h2>;
      if (line.startsWith('### ')) return <h3 key={i} className="text-base font-medium text-white/90 mt-3 mb-1">{line.slice(4)}</h3>;
      if (line.startsWith('**') && line.endsWith('**')) return <p key={i} className="font-semibold text-white/90 mt-2">{line.slice(2, -2)}</p>;
      if (line.startsWith('- ')) return <li key={i} className="text-white/70 text-sm ml-4 list-disc">{line.slice(2)}</li>;
      if (line.startsWith('|')) return <p key={i} className="text-white/60 text-xs font-mono">{line}</p>;
      if (line.trim() === '') return <br key={i} />;
      return <p key={i} className="text-white/70 text-sm leading-relaxed">{line}</p>;
    });
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {/* Header */}
      <header className="border-b border-white/[0.06] bg-[#0A0A0A]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-white/80 hover:text-white transition-colors">
            <ArrowLeft className="h-4 w-4" />
            <span className="text-sm font-medium">McLeuker AI</span>
          </Link>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-white/50 hover:text-white/80 hover:bg-white/[0.05] transition-all"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-[#8a9a7e]" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <Link
              href="/dashboard"
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-medium bg-white/[0.08] text-white/80 hover:bg-white/[0.12] transition-all"
            >
              <MessageSquare className="h-3.5 w-3.5" />
              Try McLeuker AI
            </Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-white/30" />
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <MessageSquare className="h-10 w-10 text-white/20 mx-auto mb-4" />
            <p className="text-white/50 text-sm">{error}</p>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 mt-6 px-5 py-2.5 rounded-xl text-sm font-medium bg-white/[0.08] text-white/80 hover:bg-white/[0.12] transition-all"
            >
              Go to McLeuker AI
            </Link>
          </div>
        ) : message ? (
          <div>
            {/* Query */}
            {message.user_query && (
              <div className="mb-6 pb-6 border-b border-white/[0.06]">
                <p className="text-[10px] text-white/30 uppercase tracking-wider mb-2">Question</p>
                <p className="text-white/80 text-base">{message.user_query}</p>
              </div>
            )}

            {/* Response */}
            <div className="mb-6">
              <p className="text-[10px] text-white/30 uppercase tracking-wider mb-3">McLeuker AI Response</p>
              <div className="prose prose-invert max-w-none">
                {renderContent(message.content)}
              </div>
            </div>

            {/* Footer */}
            <div className="mt-8 pt-6 border-t border-white/[0.06] flex items-center justify-between">
              <p className="text-[10px] text-white/20">
                Shared from McLeuker AI &middot; {new Date(message.created_at).toLocaleDateString()}
              </p>
              <div className="flex items-center gap-1 text-white/20">
                <ThumbsUp className="h-3 w-3" />
                <span className="text-[10px]">Powered by McLeuker AI</span>
              </div>
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
}
