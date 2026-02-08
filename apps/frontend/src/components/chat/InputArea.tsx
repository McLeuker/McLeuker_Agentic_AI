'use client';

import React, { useRef, useState, useCallback } from 'react';
import { ChatMode } from './ModeSelector';

interface InputAreaProps {
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  onFileUpload: (file: File) => void;
  onVisionToCode: (file: File) => void;
  isLoading: boolean;
  mode: ChatMode;
}

// All supported file types for upload and analysis
const ALL_ACCEPTED_TYPES = [
  // Images
  'image/png', 'image/jpeg', 'image/webp', 'image/gif', 'image/svg+xml', 'image/bmp', 'image/tiff',
  // Videos
  'video/mp4', 'video/webm', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska',
  // Documents
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'text/csv',
  'text/plain',
  'application/json',
  'text/markdown',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
].join(',');

const ACCEPT_STRING = `${ALL_ACCEPTED_TYPES},.png,.jpg,.jpeg,.webp,.gif,.svg,.bmp,.tiff,.mp4,.webm,.mov,.avi,.mkv,.pdf,.xlsx,.xls,.docx,.doc,.csv,.txt,.json,.md,.pptx`;

interface UploadedFilePreview {
  file: File;
  name: string;
  type: 'image' | 'video' | 'document';
  preview?: string;
}

function getFileCategory(mime: string): 'image' | 'video' | 'document' {
  if (mime.startsWith('image/')) return 'image';
  if (mime.startsWith('video/')) return 'video';
  return 'document';
}

function getFileIcon(type: 'image' | 'video' | 'document', name: string): string {
  if (type === 'image') return '🖼️';
  if (type === 'video') return '🎬';
  const ext = name.split('.').pop()?.toLowerCase() || '';
  if (ext === 'pdf') return '📕';
  if (['xlsx', 'xls', 'csv'].includes(ext)) return '📊';
  if (['docx', 'doc'].includes(ext)) return '📄';
  if (ext === 'pptx') return '📽️';
  if (['json', 'md', 'txt'].includes(ext)) return '📝';
  return '📎';
}

export function InputArea({ 
  input, 
  onInputChange, 
  onSend, 
  onFileUpload, 
  onVisionToCode,
  isLoading, 
  mode 
}: InputAreaProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [attachedFiles, setAttachedFiles] = useState<UploadedFilePreview[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const addFile = useCallback((file: File) => {
    const category = getFileCategory(file.type);
    const preview: UploadedFilePreview = {
      file,
      name: file.name,
      type: category,
    };

    // Generate image preview
    if (category === 'image') {
      const reader = new FileReader();
      reader.onload = (e) => {
        preview.preview = e.target?.result as string;
        setAttachedFiles(prev => [...prev, preview]);
      };
      reader.readAsDataURL(file);
    } else {
      setAttachedFiles(prev => [...prev, preview]);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      Array.from(files).forEach(addFile);
    }
    e.target.value = '';
  };

  const removeFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSend = () => {
    // Upload attached files first
    attachedFiles.forEach(f => {
      if (f.type === 'image' && mode === 'code') {
        onVisionToCode(f.file);
      } else {
        onFileUpload(f.file);
      }
    });
    setAttachedFiles([]);
    onSend();
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files) {
      Array.from(files).forEach(addFile);
    }
  };

  // Auto-resize textarea
  const handleTextChange = (value: string) => {
    onInputChange(value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  };

  const modeLabels: Record<string, string> = {
    instant: 'Quick Search',
    research: 'Deep Research',
    agent: 'Agent',
    code: 'Creative & Code',
    thinking: 'Thinking',
    swarm: 'Swarm',
    hybrid: 'Hybrid',
  };

  const quickActions = [
    { icon: '📊', label: 'Excel', prompt: 'Generate an Excel spreadsheet with ', color: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400' },
    { icon: '📄', label: 'Word', prompt: 'Create a Word document about ', color: 'bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-500/10 dark:text-blue-400' },
    { icon: '📕', label: 'PDF', prompt: 'Generate a PDF report on ', color: 'bg-red-50 text-red-700 hover:bg-red-100 dark:bg-red-500/10 dark:text-red-400' },
    { icon: '📽️', label: 'PPT', prompt: 'Create a presentation about ', color: 'bg-orange-50 text-orange-700 hover:bg-orange-100 dark:bg-orange-500/10 dark:text-orange-400' },
    { icon: '🔍', label: 'Research', prompt: 'Research and analyze ', color: 'bg-violet-50 text-violet-700 hover:bg-violet-100 dark:bg-violet-500/10 dark:text-violet-400' },
    { icon: '💻', label: 'Code', prompt: 'Write code to ', color: 'bg-gray-50 text-gray-700 hover:bg-gray-100 dark:bg-gray-500/10 dark:text-gray-400' },
  ];

  return (
    <div 
      className="bg-background border-t border-border/50 px-4 py-3"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {isDragOver && (
        <div className="absolute inset-0 bg-blue-500/10 border-2 border-dashed border-blue-400 rounded-2xl z-10 flex items-center justify-center">
          <div className="text-blue-500 font-medium text-sm flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Drop files here to upload
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="flex gap-1.5 mb-2.5 overflow-x-auto pb-1 scrollbar-hide">
        {quickActions.map((action, i) => (
          <button
            key={i}
            onClick={() => onInputChange(action.prompt)}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs whitespace-nowrap transition-all ${action.color}`}
          >
            <span className="text-sm">{action.icon}</span>
            <span className="font-medium">{action.label}</span>
          </button>
        ))}
      </div>

      {/* Attached Files Preview */}
      {attachedFiles.length > 0 && (
        <div className="flex gap-2 mb-2 overflow-x-auto pb-1">
          {attachedFiles.map((f, i) => (
            <div key={i} className="relative flex items-center gap-2 px-3 py-1.5 bg-muted/50 rounded-lg border border-border/50 group min-w-0">
              {f.preview ? (
                <img src={f.preview} alt={f.name} className="w-8 h-8 rounded object-cover" />
              ) : (
                <span className="text-lg">{getFileIcon(f.type, f.name)}</span>
              )}
              <div className="min-w-0">
                <p className="text-xs font-medium text-foreground truncate max-w-[120px]">{f.name}</p>
                <p className="text-[10px] text-muted-foreground capitalize">{f.type}</p>
              </div>
              <button
                onClick={() => removeFile(i)}
                className="absolute -top-1.5 -right-1.5 w-4 h-4 bg-destructive text-destructive-foreground rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Container */}
      <div className="flex items-end gap-2 bg-muted/50 rounded-2xl p-2 border border-border/30 focus-within:border-border/60 transition-colors">
        {/* File Upload Button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          className="p-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-xl transition-colors"
          title="Upload files (images, videos, PDFs, Excel, Word, etc.)"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button>

        {/* Text Input */}
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => handleTextChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Message McLeuker AI (${modeLabels[mode] || mode})...`}
            className="w-full px-2 py-2 bg-transparent resize-none focus:outline-none text-foreground placeholder-muted-foreground/60 text-sm"
            rows={1}
            style={{ minHeight: '40px', maxHeight: '200px' }}
          />
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={(!input.trim() && attachedFiles.length === 0) || isLoading}
          className={`p-2.5 rounded-xl transition-all ${
            (input.trim() || attachedFiles.length > 0) && !isLoading
              ? 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm'
              : 'bg-muted text-muted-foreground cursor-not-allowed'
          }`}
        >
          {isLoading ? (
            <svg className="w-4.5 h-4.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          )}
        </button>
      </div>

      {/* Hidden File Input - accepts ALL formats */}
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPT_STRING}
        onChange={handleFileChange}
        multiple
        className="hidden"
      />

      <div className="flex items-center justify-between mt-1.5 px-1">
        <p className="text-[10px] text-muted-foreground/50">
          Supports: Images, Videos, PDF, Excel, Word, PPT, CSV, JSON, Markdown
        </p>
        <p className="text-[10px] text-muted-foreground/50">
          <kbd className="px-1 py-0.5 bg-muted rounded text-muted-foreground text-[9px]">Enter</kbd> send
          <span className="mx-1">·</span>
          <kbd className="px-1 py-0.5 bg-muted rounded text-muted-foreground text-[9px]">Shift+Enter</kbd> newline
        </p>
      </div>
    </div>
  );
}
