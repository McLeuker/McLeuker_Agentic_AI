/**
 * McLeuker Agentic AI Platform - Chat Interface Component
 * 
 * A complete chat interface component for Lovable integration.
 * Copy this file into your Lovable project's `src/components/` directory.
 */

import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { getFileDownloadUrl } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { 
  Loader2, 
  Send, 
  Download, 
  FileSpreadsheet, 
  FileText, 
  Presentation, 
  Code, 
  Globe,
  ExternalLink,
  Trash2
} from 'lucide-react';

// --- Helper Functions ---

function getFileIcon(format: string) {
  switch (format.toLowerCase()) {
    case 'excel':
    case 'csv':
      return <FileSpreadsheet className="w-4 h-4" />;
    case 'pdf':
    case 'word':
      return <FileText className="w-4 h-4" />;
    case 'ppt':
      return <Presentation className="w-4 h-4" />;
    case 'code':
      return <Code className="w-4 h-4" />;
    case 'web':
    case 'dashboard':
      return <Globe className="w-4 h-4" />;
    default:
      return <FileText className="w-4 h-4" />;
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// --- Component ---

interface ChatInterfaceProps {
  className?: string;
  title?: string;
  placeholder?: string;
}

export function ChatInterface({
  className = '',
  title = 'McLeuker AI Assistant',
  placeholder = 'Ask me anything or describe a task...',
}: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const message = input;
    setInput('');
    await sendMessage(message);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Card className={`flex flex-col h-[600px] ${className}`}>
      <CardHeader className="flex flex-row items-center justify-between py-3 border-b">
        <CardTitle className="text-lg">{title}</CardTitle>
        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearMessages}
            className="text-gray-500 hover:text-red-500"
          >
            <Trash2 className="w-4 h-4 mr-1" />
            Clear
          </Button>
        )}
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Messages Area */}
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <p className="text-lg font-medium mb-2">Welcome to McLeuker AI</p>
                <p className="text-sm">
                  I can help you create reports, analyze data, research topics, and more.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    {/* Message Content */}
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>

                    {/* Generated Files */}
                    {msg.files && msg.files.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-semibold mb-2 text-gray-600">
                          Generated Files:
                        </p>
                        <div className="space-y-2">
                          {msg.files.map((file, idx) => (
                            <a
                              key={idx}
                              href={getFileDownloadUrl(file.filename)}
                              download
                              className="flex items-center gap-2 p-2 bg-white rounded border hover:bg-gray-50 transition-colors"
                            >
                              {getFileIcon(file.format)}
                              <div className="flex-1 min-w-0">
                                <p className="text-xs font-medium truncate">
                                  {file.filename}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {formatFileSize(file.size_bytes)}
                                </p>
                              </div>
                              <Download className="w-4 h-4 text-gray-400" />
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Sources */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-semibold mb-2 text-gray-600">
                          Sources:
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {msg.sources.map((source, idx) => (
                            <a
                              key={idx}
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
                            >
                              <ExternalLink className="w-3 h-3" />
                              {source.title}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Timestamp */}
                    <p className="text-xs mt-2 opacity-60">
                      {msg.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-500">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>

        {/* Error Display */}
        {error && (
          <div className="px-4 py-2 bg-red-50 border-t border-red-200">
            <p className="text-sm text-red-600">{error.message}</p>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 border-t">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading || !input.trim()}>
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </form>
          <p className="text-xs text-gray-400 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default ChatInterface;
