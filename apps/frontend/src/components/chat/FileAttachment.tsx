"use client";

/**
 * FileAttachment Component (FIXED)
 * ================================
 * 
 * CRITICAL FIX: This component adds file attachment UI to the chat interface.
 * 
 * Previously missing features:
 * - File upload button in message input
 * - File preview before sending
 * - File metadata display
 * - Support for images, documents, spreadsheets
 * - Integration with API file handling
 */

import React, { useState, useRef, useCallback } from "react";

export interface AttachedFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  preview?: string; // For images
  base64?: string;  // For API upload
}

interface FileAttachmentProps {
  /** Called when files are attached */
  onFilesAttached: (files: AttachedFile[]) => void;
  /** Called when a file is removed */
  onFileRemoved?: (fileId: string) => void;
  /** Currently attached files */
  attachedFiles?: AttachedFile[];
  /** Maximum file size in MB */
  maxFileSizeMB?: number;
  /** Allowed file types */
  allowedTypes?: string[];
  /** Whether multiple files are allowed */
  multiple?: boolean;
  /** Disabled state */
  disabled?: boolean;
}

const DEFAULT_MAX_SIZE = 10; // 10MB
const DEFAULT_ALLOWED_TYPES = [
  // Images
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/webp",
  // Documents
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
  "text/markdown",
  // Spreadsheets
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "text/csv",
  // Code files
  "text/javascript",
  "text/typescript",
  "text/html",
  "text/css",
  "application/json",
];

const FILE_TYPE_ICONS: Record<string, string> = {
  image: "🖼️",
  pdf: "📄",
  word: "📝",
  excel: "📊",
  code: "💻",
  text: "📃",
  default: "📎",
};

function getFileIcon(type: string): string {
  if (type.startsWith("image/")) return FILE_TYPE_ICONS.image;
  if (type === "application/pdf") return FILE_TYPE_ICONS.pdf;
  if (type.includes("word")) return FILE_TYPE_ICONS.word;
  if (type.includes("excel") || type.includes("sheet") || type === "text/csv") {
    return FILE_TYPE_ICONS.excel;
  }
  if (type.includes("javascript") || type.includes("typescript") || type.includes("json")) {
    return FILE_TYPE_ICONS.code;
  }
  if (type.startsWith("text/")) return FILE_TYPE_ICONS.text;
  return FILE_TYPE_ICONS.default;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

export default function FileAttachment({
  onFilesAttached,
  onFileRemoved,
  attachedFiles = [],
  maxFileSizeMB = DEFAULT_MAX_SIZE,
  allowedTypes = DEFAULT_ALLOWED_TYPES,
  multiple = true,
  disabled = false,
}: FileAttachmentProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const maxSizeBytes = maxFileSizeMB * 1024 * 1024;

  const processFile = async (file: File): Promise<AttachedFile> => {
    const attachedFile: AttachedFile = {
      id: generateId(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
    };

    // Generate preview for images
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      attachedFile.preview = await new Promise((resolve) => {
        reader.onloadend = () => resolve(reader.result as string);
        reader.readAsDataURL(file);
      });
    }

    // Generate base64 for API upload
    const base64Reader = new FileReader();
    attachedFile.base64 = await new Promise((resolve) => {
      base64Reader.onloadend = () => {
        const result = base64Reader.result as string;
        // Remove data URL prefix (e.g., "data:image/jpeg;base64,")
        resolve(result.split(",")[1]);
      };
      base64Reader.readAsDataURL(file);
    });

    return attachedFile;
  };

  const validateFile = (file: File): string | null => {
    if (file.size > maxSizeBytes) {
      return `File too large. Max size is ${maxFileSizeMB}MB`;
    }
    if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
      return `File type not supported. Allowed: ${allowedTypes.map(t => t.split("/")[1]).join(", ")}`;
    }
    return null;
  };

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setError(null);
    const newFiles: AttachedFile[] = [];
    const errors: string[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const validationError = validateFile(file);

      if (validationError) {
        errors.push(`${file.name}: ${validationError}`);
        continue;
      }

      try {
        const attachedFile = await processFile(file);
        newFiles.push(attachedFile);
      } catch (err) {
        errors.push(`${file.name}: Failed to process file`);
      }
    }

    if (errors.length > 0) {
      setError(errors.join("; "));
    }

    if (newFiles.length > 0) {
      onFilesAttached(multiple ? [...attachedFiles, ...newFiles] : newFiles);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (!disabled) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [disabled]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleRemoveFile = (fileId: string) => {
    if (onFileRemoved) {
      onFileRemoved(fileId);
    }
  };

  const handleButtonClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="w-full">
      {/* Error message */}
      {error && (
        <div className="mb-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-xs text-red-400">
          {error}
        </div>
      )}

      {/* Attached files preview */}
      {attachedFiles.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {attachedFiles.map((file) => (
            <div
              key={file.id}
              className="group flex items-center gap-2 px-2 py-1.5 bg-white/5 hover:bg-white/10 
                         border border-white/10 rounded-lg transition-colors"
            >
              {/* File icon or preview */}
              {file.preview ? (
                <img
                  src={file.preview}
                  alt={file.name}
                  className="w-6 h-6 rounded object-cover"
                />
              ) : (
                <span className="text-lg">{getFileIcon(file.type)}</span>
              )}

              {/* File info */}
              <div className="flex flex-col min-w-0">
                <span className="text-xs text-white/80 truncate max-w-[120px]">
                  {file.name}
                </span>
                <span className="text-[10px] text-white/40">
                  {formatFileSize(file.size)}
                </span>
              </div>

              {/* Remove button */}
              <button
                onClick={() => handleRemoveFile(file.id)}
                disabled={disabled}
                className="ml-1 p-0.5 text-white/40 hover:text-red-400 
                           disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Remove file"
              >
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload button and drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          flex items-center gap-2 p-2 rounded-lg border border-dashed
          transition-colors duration-200
          ${isDragging 
            ? "border-blue-400/50 bg-blue-400/5" 
            : "border-white/10 hover:border-white/20"
          }
          ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
        `}
      >
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          onChange={(e) => handleFiles(e.target.files)}
          accept={allowedTypes.join(",")}
          multiple={multiple}
          disabled={disabled}
          className="hidden"
        />

        {/* Upload button */}
        <button
          onClick={handleButtonClick}
          disabled={disabled}
          className="flex items-center gap-1.5 px-2 py-1 text-xs text-white/60 
                     hover:text-white/80 disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
            />
          </svg>
          Attach file
        </button>

        {/* Drag & drop hint */}
        <span className="text-[10px] text-white/30">
          or drag & drop
        </span>

        {/* File type hint */}
        <span className="ml-auto text-[10px] text-white/20">
          Max {maxFileSizeMB}MB
        </span>
      </div>
    </div>
  );
}

// ============================================================================
// Hook for using file attachments in chat
// ============================================================================

export interface UseFileAttachmentReturn {
  files: AttachedFile[];
  addFiles: (files: AttachedFile[]) => void;
  removeFile: (fileId: string) => void;
  clearFiles: () => void;
  hasImages: boolean;
  getImagePreviews: () => { base64: string; name: string }[];
  getFilesForApi: () => { name: string; type: string; base64: string }[];
}

export function useFileAttachment(): UseFileAttachmentReturn {
  const [files, setFiles] = useState<AttachedFile[]>([]);

  const addFiles = useCallback((newFiles: AttachedFile[]) => {
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const removeFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  const hasImages = files.some((f) => f.type.startsWith("image/"));

  const getImagePreviews = useCallback(() => {
    return files
      .filter((f) => f.type.startsWith("image/") && f.base64)
      .map((f) => ({ base64: f.base64!, name: f.name }));
  }, [files]);

  const getFilesForApi = useCallback(() => {
    return files
      .filter((f) => f.base64)
      .map((f) => ({ name: f.name, type: f.type, base64: f.base64! }));
  }, [files]);

  return {
    files,
    addFiles,
    removeFile,
    clearFiles,
    hasImages,
    getImagePreviews,
    getFilesForApi,
  };
}

export default FileAttachment;
