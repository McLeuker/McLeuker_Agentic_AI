'use client';

import React, { useRef, useState } from 'react';
import { ChatMode } from '@/lib/api';

interface InputAreaProps {
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  onFileUpload: (file: File) => void;
  onVisionToCode: (file: File) => void;
  isLoading: boolean;
  mode: ChatMode;
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
  const imageInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [showQuickActions, setShowQuickActions] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'image' | 'ui') => {
    const file = e.target.files?.[0];
    if (file) {
      if (type === 'ui') {
        onVisionToCode(file);
      } else {
        onFileUpload(file);
      }
    }
    e.target.value = ''; // Reset input
  };

  const quickActions = [
    { 
      icon: '📊', 
      label: 'Excel', 
      prompt: 'Generate an Excel spreadsheet with ',
      color: 'bg-green-100 text-green-700 hover:bg-green-200'
    },
    { 
      icon: '📄', 
      label: 'Word Doc', 
      prompt: 'Create a Word document about ',
      color: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
    },
    { 
      icon: '📑', 
      label: 'PDF', 
      prompt: 'Generate a PDF report on ',
      color: 'bg-red-100 text-red-700 hover:bg-red-200'
    },
    { 
      icon: '📽️', 
      label: 'Presentation', 
      prompt: 'Create a presentation about ',
      color: 'bg-orange-100 text-orange-700 hover:bg-orange-200'
    },
    { 
      icon: '🔍', 
      label: 'Research', 
      prompt: 'Research ',
      color: 'bg-purple-100 text-purple-700 hover:bg-purple-200'
    },
    { 
      icon: '💻', 
      label: 'Code', 
      prompt: 'Write code to ',
      color: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    },
  ];

  return (
    <div className="bg-white border-t px-4 py-4">
      {/* Quick Actions */}
      <div className="flex gap-2 mb-3 overflow-x-auto pb-1 scrollbar-hide">
        {quickActions.map((action, i) => (
          <button
            key={i}
            onClick={() => onInputChange(action.prompt)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition ${action.color}`}
          >
            <span>{action.icon}</span>
            <span className="font-medium">{action.label}</span>
          </button>
        ))}
      </div>

      {/* Input Container */}
      <div className="flex items-end gap-2 bg-gray-100 rounded-2xl p-2">
        {/* File Upload Buttons */}
        <div className="flex gap-1">
          <button
            onClick={() => imageInputRef.current?.click()}
            className="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-xl transition"
            title="Upload image for analysis"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </button>
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-xl transition"
            title="Upload UI mockup for code generation"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </button>
        </div>

        {/* Text Input */}
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Message in ${mode} mode...`}
            className="w-full px-3 py-2.5 bg-transparent resize-none focus:outline-none text-gray-800 placeholder-gray-400"
            rows={1}
            style={{ minHeight: '44px', maxHeight: '200px' }}
          />
        </div>

        {/* Send Button */}
        <button
          onClick={onSend}
          disabled={!input.trim() || isLoading}
          className={`p-3 rounded-xl transition ${
            input.trim() && !isLoading
              ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isLoading ? (
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>

      {/* Hidden File Inputs */}
      <input
        ref={imageInputRef}
        type="file"
        accept="image/*"
        onChange={(e) => handleFileChange(e, 'image')}
        className="hidden"
      />
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={(e) => handleFileChange(e, 'ui')}
        className="hidden"
      />

      <p className="text-xs text-gray-400 mt-2 text-center">
        Press <kbd className="px-1.5 py-0.5 bg-gray-200 rounded text-gray-600">Enter</kbd> to send, 
        <kbd className="px-1.5 py-0.5 bg-gray-200 rounded text-gray-600">Shift + Enter</kbd> for new line
      </p>
    </div>
  );
}
