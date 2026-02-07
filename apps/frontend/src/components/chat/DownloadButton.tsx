'use client';

import React from 'react';
import { DownloadableFile, api } from '@/lib/api';

interface DownloadButtonProps {
  file: DownloadableFile;
  variant?: 'default' | 'compact';
}

export function DownloadButton({ file, variant = 'default' }: DownloadButtonProps) {
  const handleDownload = () => {
    api.downloadFile(file.file_id, file.filename);
  };

  const getFileIcon = (filename: string) => {
    if (filename.endsWith('.xlsx') || filename.endsWith('.csv')) return '📊';
    if (filename.endsWith('.docx')) return '📄';
    if (filename.endsWith('.pdf')) return '📑';
    if (filename.endsWith('.pptx')) return '📽️';
    if (filename.endsWith('.json')) return '📋';
    return '📎';
  };

  const getFileColor = (filename: string) => {
    if (filename.endsWith('.xlsx') || filename.endsWith('.csv')) return 'bg-green-100 text-green-700 border-green-200 hover:bg-green-200';
    if (filename.endsWith('.docx')) return 'bg-blue-100 text-blue-700 border-blue-200 hover:bg-blue-200';
    if (filename.endsWith('.pdf')) return 'bg-red-100 text-red-700 border-red-200 hover:bg-red-200';
    if (filename.endsWith('.pptx')) return 'bg-orange-100 text-orange-700 border-orange-200 hover:bg-orange-200';
    if (filename.endsWith('.json')) return 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200';
    return 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200';
  };

  if (variant === 'compact') {
    return (
      <button
        onClick={handleDownload}
        className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs transition ${getFileColor(file.filename)}`}
        title={file.filename}
      >
        <span>{getFileIcon(file.filename)}</span>
        <span className="truncate max-w-[100px]">{file.filename}</span>
      </button>
    );
  }

  return (
    <button
      onClick={handleDownload}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition ${getFileColor(file.filename)}`}
    >
      <span className="text-lg">{getFileIcon(file.filename)}</span>
      <div className="text-left">
        <div className="text-sm font-medium truncate max-w-[150px]">{file.filename}</div>
        <div className="text-xs opacity-70">Click to download</div>
      </div>
      <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
    </button>
  );
}
