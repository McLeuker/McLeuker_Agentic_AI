'use client';

import React, { useState } from 'react';
import { DownloadInfo, api } from '@/lib/api';

interface DownloadButtonProps {
  file: DownloadInfo;
  variant?: 'default' | 'compact';
}

export function DownloadButton({ file, variant = 'default' }: DownloadButtonProps) {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    setError(false);
    try {
      // Use the persistent download URL - works even after server restart
      const downloadUrl = api.getFileDownloadUrl(file.file_id);
      
      const response = await fetch(downloadUrl);
      if (!response.ok) {
        // If redirect (Supabase public URL), follow it
        if (response.redirected) {
          window.open(response.url, '_blank');
          return;
        }
        throw new Error('Download failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      setError(true);
      // Fallback: try opening the URL directly
      try {
        window.open(api.getFileDownloadUrl(file.file_id), '_blank');
      } catch {
        // ignore
      }
    } finally {
      setDownloading(false);
    }
  };

  const getFileIcon = (filename: string) => {
    if (filename.endsWith('.xlsx') || filename.endsWith('.csv')) return '📊';
    if (filename.endsWith('.docx')) return '📄';
    if (filename.endsWith('.pdf')) return '📕';
    if (filename.endsWith('.pptx')) return '📽️';
    if (filename.endsWith('.json')) return '📋';
    if (filename.endsWith('.md')) return '📝';
    return '📎';
  };

  const getFileColor = (filename: string) => {
    if (filename.endsWith('.xlsx') || filename.endsWith('.csv')) return 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/30';
    if (filename.endsWith('.docx')) return 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/30';
    if (filename.endsWith('.pdf')) return 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/30';
    if (filename.endsWith('.pptx')) return 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100 dark:bg-orange-500/10 dark:text-orange-400 dark:border-orange-500/30';
    return 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-500/10 dark:text-gray-400 dark:border-gray-500/30';
  };

  if (variant === 'compact') {
    return (
      <button
        onClick={handleDownload}
        disabled={downloading}
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs transition-all border ${getFileColor(file.filename)} ${downloading ? 'opacity-60' : ''} ${error ? 'ring-1 ring-red-300' : ''}`}
        title={error ? 'Download failed - click to retry' : file.filename}
      >
        {downloading ? (
          <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <span>{getFileIcon(file.filename)}</span>
        )}
        <span className="truncate max-w-[120px]">{file.filename}</span>
      </button>
    );
  }

  return (
    <button
      onClick={handleDownload}
      disabled={downloading}
      className={`flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl border transition-all ${getFileColor(file.filename)} ${downloading ? 'opacity-60' : ''} ${error ? 'ring-1 ring-red-300' : ''}`}
    >
      {downloading ? (
        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : (
        <span className="text-lg">{getFileIcon(file.filename)}</span>
      )}
      <div className="text-left min-w-0">
        <div className="text-sm font-medium truncate max-w-[160px]">{file.filename}</div>
        <div className="text-[10px] opacity-60">
          {error ? 'Failed - click to retry' : downloading ? 'Downloading...' : 'Click to download'}
        </div>
      </div>
      <svg className="w-4 h-4 ml-auto flex-shrink-0 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
    </button>
  );
}
