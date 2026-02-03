'use client';

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { 
  Send, 
  Plus, 
  MessageSquare, 
  ChevronLeft,
  ChevronRight,
  Sparkles,
  ExternalLink,
  Lightbulb,
  ArrowRight
} from "lucide-react";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{ title: string; url: string; }>;
  keyInsights?: string[];
  followUpQuestions?: string[];
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

export default function DashboardPage() {
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check for pre-filled prompt from landing page
  useEffect(() => {
    const domainPrompt = sessionStorage.getItem("domainPrompt");
    if (domainPrompt) {
      sessionStorage.removeItem("domainPrompt");
      setInput(domainPrompt);
      // Auto-submit after a short delay
      setTimeout(() => {
        handleSendMessage(domainPrompt);
      }, 500);
    }
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [currentConversation?.messages]);

  const createNewConversation = () => {
    const newConv: Conversation = {
      id: Date.now().toString(),
      title: "New Chat",
      messages: [],
      createdAt: new Date(),
    };
    setConversations(prev => [newConv, ...prev]);
    setCurrentConversation(newConv);
  };

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || input;
    if (!text.trim() || isLoading) return;

    // Create conversation if none exists
    let conv = currentConversation;
    if (!conv) {
      conv = {
        id: Date.now().toString(),
        title: text.slice(0, 50) + (text.length > 50 ? "..." : ""),
        messages: [],
        createdAt: new Date(),
      };
      setConversations(prev => [conv!, ...prev]);
      setCurrentConversation(conv);
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    const updatedConv = {
      ...conv,
      title: conv.messages.length === 0 ? text.slice(0, 50) + (text.length > 50 ? "..." : "") : conv.title,
      messages: [...conv.messages, userMessage],
    };
    setCurrentConversation(updatedConv);
    setConversations(prev => prev.map(c => c.id === conv!.id ? updatedConv : c));
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          conversation_id: conv.id,
          mode: "quick",
          domain: "all"
        }),
      });

      const data = await response.json();
      
      // Parse V5.1 response
      let content = "";
      let sources: Array<{ title: string; url: string; }> = [];
      let keyInsights: string[] = [];
      let followUpQuestions: string[] = [];

      if (data.response) {
        const resp = data.response;
        content = resp.summary || resp.answer || "";
        
        if (resp.key_insights) {
          keyInsights = resp.key_insights;
        }
        if (resp.sources) {
          sources = resp.sources.map((s: any) => ({
            title: s.title || s.name || "Source",
            url: s.url || s.link || "#"
          }));
        }
        if (resp.follow_up_questions) {
          followUpQuestions = resp.follow_up_questions;
        }
      } else if (typeof data === 'string') {
        content = data;
      } else {
        content = JSON.stringify(data);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content,
        timestamp: new Date(),
        sources,
        keyInsights,
        followUpQuestions,
      };

      const finalConv = {
        ...updatedConv,
        messages: [...updatedConv.messages, assistantMessage],
      };
      setCurrentConversation(finalConv);
      setConversations(prev => prev.map(c => c.id === conv!.id ? finalConv : c));

    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Sorry, there was an error processing your request. Please try again.",
        timestamp: new Date(),
      };
      const finalConv = {
        ...updatedConv,
        messages: [...updatedConv.messages, errorMessage],
      };
      setCurrentConversation(finalConv);
      setConversations(prev => prev.map(c => c.id === conv!.id ? finalConv : c));
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowUpClick = (question: string) => {
    setInput(question);
    handleSendMessage(question);
  };

  return (
    <div className="min-h-screen bg-[#070707] flex">
      {/* Sidebar */}
      <aside className={cn(
        "fixed left-0 top-0 h-full z-40",
        "bg-gradient-to-b from-[#0D0D0D] to-[#080808]",
        "border-r border-white/[0.08]",
        "transition-all duration-200",
        sidebarOpen ? "w-72" : "w-14"
      )}>
        {/* Sidebar Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/[0.08]">
          {sidebarOpen && (
            <Link href="/" className="font-editorial text-lg text-white">
              McLeuker
            </Link>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-md hover:bg-white/[0.08] text-white/60 hover:text-white transition-colors"
          >
            {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={createNewConversation}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg",
              "bg-white/[0.08] hover:bg-white/[0.12]",
              "text-white/80 hover:text-white",
              "transition-colors",
              !sidebarOpen && "justify-center"
            )}
          >
            <Plus className="w-4 h-4" />
            {sidebarOpen && <span className="text-sm">New Chat</span>}
          </button>
        </div>

        {/* Conversations List */}
        {sidebarOpen && (
          <div className="px-3 py-2 overflow-y-auto max-h-[calc(100vh-140px)]">
            <p className="text-xs text-white/40 uppercase tracking-wider mb-2 px-2">Recent Chats</p>
            <div className="space-y-1">
              {conversations.map(conv => (
                <button
                  key={conv.id}
                  onClick={() => setCurrentConversation(conv)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left",
                    "hover:bg-white/[0.08] transition-colors",
                    currentConversation?.id === conv.id 
                      ? "bg-white/[0.10] text-white" 
                      : "text-white/60"
                  )}
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm truncate">{conv.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className={cn(
        "flex-1 flex flex-col min-h-screen",
        sidebarOpen ? "ml-72" : "ml-14"
      )}>
        {/* Header */}
        <header className="h-16 border-b border-white/[0.08] flex items-center justify-between px-6 bg-[#0A0A0A]">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-white/60" />
            <span className="text-white/80 font-medium">
              {currentConversation?.title || "McLeuker AI"}
            </span>
          </div>
          <Link
            href="/"
            className="text-sm text-white/60 hover:text-white transition-colors"
          >
            Back to Home
          </Link>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-3xl mx-auto space-y-6">
            {!currentConversation || currentConversation.messages.length === 0 ? (
              <div className="text-center py-20">
                <Sparkles className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <h2 className="text-2xl font-editorial text-white/80 mb-2">
                  How can I help you today?
                </h2>
                <p className="text-white/50">
                  Ask me about fashion trends, suppliers, market analysis, or sustainability.
                </p>
              </div>
            ) : (
              currentConversation.messages.map(message => (
                <div key={message.id} className={cn(
                  "flex",
                  message.role === 'user' ? "justify-end" : "justify-start"
                )}>
                  <div className={cn(
                    "max-w-[85%] rounded-[20px] p-5",
                    message.role === 'user' 
                      ? "bg-white text-black" 
                      : "bg-gradient-to-b from-[#1A1A1A] to-[#141414] border border-white/[0.08]"
                  )}>
                    <p className={cn(
                      "leading-relaxed whitespace-pre-wrap",
                      message.role === 'user' ? "text-black" : "text-white/[0.88]"
                    )}>
                      {message.content}
                    </p>

                    {/* Key Insights */}
                    {message.keyInsights && message.keyInsights.length > 0 && (
                      <div className="mt-5 pt-5 border-t border-white/[0.08]">
                        <div className="flex items-center gap-2 mb-3">
                          <Lightbulb className="w-4 h-4 text-white/60" />
                          <span className="text-sm font-medium text-white/70">Key Insights</span>
                        </div>
                        <ul className="space-y-2">
                          {message.keyInsights.map((insight, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                              <span className="text-white/40">•</span>
                              {insight}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-5 pt-5 border-t border-white/[0.08]">
                        <div className="flex items-center gap-2 mb-3">
                          <ExternalLink className="w-4 h-4 text-white/60" />
                          <span className="text-sm font-medium text-white/70">Sources</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {message.sources.map((source, i) => (
                            <a
                              key={i}
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs px-3 py-1.5 rounded-full bg-white/[0.08] text-white/70 hover:bg-white/[0.12] hover:text-white transition-colors"
                            >
                              {source.title}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Follow-up Questions */}
                    {message.followUpQuestions && message.followUpQuestions.length > 0 && (
                      <div className="mt-5 pt-5 border-t border-white/[0.08]">
                        <p className="text-xs text-white/50 mb-3">Suggested follow-ups:</p>
                        <div className="flex flex-wrap gap-2">
                          {message.followUpQuestions.map((question, i) => (
                            <button
                              key={i}
                              onClick={() => handleFollowUpClick(question)}
                              className="text-xs px-3 py-1.5 rounded-full border border-white/[0.12] text-white/70 hover:bg-white/[0.08] hover:text-white transition-colors flex items-center gap-1"
                            >
                              {question}
                              <ArrowRight className="w-3 h-3" />
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] border border-white/[0.08] rounded-[20px] p-5">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-white/40 rounded-full animate-pulse" />
                    <div className="w-2 h-2 bg-white/40 rounded-full animate-pulse delay-100" />
                    <div className="w-2 h-2 bg-white/40 rounded-full animate-pulse delay-200" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-white/[0.08] p-4 bg-gradient-to-b from-[#0A0A0A] to-[#070707]">
          <div className="max-w-3xl mx-auto">
            <div className="relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about fashion trends, suppliers, market analysis..."
                className={cn(
                  "w-full h-24 px-5 py-4 pr-14",
                  "rounded-[18px]",
                  "bg-gradient-to-b from-[#1B1B1B] to-[#111111]",
                  "border border-white/[0.10]",
                  "text-white/[0.88] placeholder:text-white/40",
                  "focus:outline-none focus:border-white/[0.18]",
                  "focus:ring-[3px] focus:ring-white/[0.06]",
                  "resize-none text-sm"
                )}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!input.trim() || isLoading}
                className={cn(
                  "absolute bottom-4 right-4",
                  "w-10 h-10 rounded-full",
                  "bg-white text-black",
                  "hover:bg-white/90",
                  "disabled:bg-white/20 disabled:text-white/40",
                  "flex items-center justify-center",
                  "transition-colors"
                )}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
