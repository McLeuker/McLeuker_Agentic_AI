'use client';

import React from 'react';
import { DownloadInfo, api } from '@/lib/api';
import { DownloadButton } from './DownloadButton';

interface DownloadPanelProps {
  downloads: DownloadInfo[];
  onClose: () => void;
}

export function DownloadPanel({ downloads, onClose }: DownloadPanelProps) {
  const downloadAll = () => {
    downloads.forEach((file, index) => {
      setTimeout(() => {
        const url = api.getFileDownloadUrl(file.file_id);
        window.open(url, '_blank');
      }, index * 500);
    });
  };

  const groupedDownloads = downloads.reduce((acc, file) => {
    const type = file.file_type || 'other';
    if (!acc[type]) acc[type] = [];
    acc[type].push(file);
    return acc;
  }, {} as Record<string, DownloadInfo[]>);

  const typeLabels: Record<string, string> = {
    excel: 'Spreadsheets',
    word: 'Documents',
    pdf: 'PDF Reports',
    pptx: 'Presentations',
    csv: 'Data Files',
    markdown: 'Markdown',
    other: 'Other Files',
  };

  return (
    <div className="fixed right-0 top-16 bottom-0 w-80 bg-background border-l border-border shadow-2xl z-30 overflow-y-auto">
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b border-border px-4 py-3 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-foreground text-sm">Downloads</h3>
          <p className="text-[10px] text-muted-foreground">{downloads.length} file(s) — stored permanently</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={downloadAll}
            className="text-[10px] px-2.5 py-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition font-medium"
          >
            Download All
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="p-3 space-y-4">
        {Object.entries(groupedDownloads).map(([type, files]) => (
          <div key={type}>
            <h4 className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              {typeLabels[type] || type}
            </h4>
            <div className="space-y-1.5">
              {files.map((file, i) => (
                <DownloadButton key={i} file={file} variant="compact" />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
