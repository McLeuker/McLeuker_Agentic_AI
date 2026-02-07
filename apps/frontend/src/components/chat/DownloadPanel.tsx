'use client';

import React from 'react';
import { DownloadableFile, api } from '@/lib/api';
import { DownloadButton } from './DownloadButton';

interface DownloadPanelProps {
  downloads: DownloadableFile[];
  onClose: () => void;
}

export function DownloadPanel({ downloads, onClose }: DownloadPanelProps) {
  const downloadAll = () => {
    downloads.forEach((file, index) => {
      setTimeout(() => {
        api.downloadFile(file.file_id, file.filename);
      }, index * 500);
    });
  };

  const groupedDownloads = downloads.reduce((acc, file) => {
    const type = file.file_type || 'other';
    if (!acc[type]) acc[type] = [];
    acc[type].push(file);
    return acc;
  }, {} as Record<string, DownloadableFile[]>);

  return (
    <div className="fixed right-0 top-16 bottom-0 w-80 bg-white border-l shadow-xl z-30 overflow-y-auto">
      <div className="sticky top-0 bg-white border-b px-4 py-3 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">Downloads</h3>
          <p className="text-xs text-gray-500">{downloads.length} file(s)</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={downloadAll}
            className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Download All
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {Object.entries(groupedDownloads).map(([type, files]) => (
          <div key={type}>
            <h4 className="text-xs font-medium text-gray-500 uppercase mb-2">{type}</h4>
            <div className="space-y-2">
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
