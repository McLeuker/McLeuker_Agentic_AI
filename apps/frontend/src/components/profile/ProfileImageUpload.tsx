'use client';

import { useState, useRef } from 'react';
import { cn } from '@/lib/utils';
import { Camera, User, Loader2 } from 'lucide-react';

interface ProfileImageUploadProps {
  currentImage: string | null;
  name: string;
  onImageSelect: (base64: string) => void;
  onError?: (message: string) => void;
  disabled?: boolean;
}

/**
 * Compress and resize an image to fit within maxSize x maxSize pixels
 * and return a JPEG data URL with the specified quality.
 * This keeps the base64 string small enough for Supabase text columns (~30-80KB).
 */
function compressImage(
  file: File,
  maxSize: number = 256,
  quality: number = 0.75
): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(url);

      // Calculate new dimensions (maintain aspect ratio, fit within maxSize)
      let width = img.width;
      let height = img.height;

      if (width > height) {
        if (width > maxSize) {
          height = Math.round(height * (maxSize / width));
          width = maxSize;
        }
      } else {
        if (height > maxSize) {
          width = Math.round(width * (maxSize / height));
          height = maxSize;
        }
      }

      // Draw to canvas at reduced size
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }

      ctx.drawImage(img, 0, 0, width, height);

      // Export as JPEG with quality setting
      const dataUrl = canvas.toDataURL('image/jpeg', quality);
      resolve(dataUrl);
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load image'));
    };

    img.src = url;
  });
}

export function ProfileImageUpload({
  currentImage,
  name,
  onImageSelect,
  onError,
  disabled = false,
}: ProfileImageUploadProps) {
  const [isHovering, setIsHovering] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      onError?.('Please select an image file (JPEG, PNG, GIF, WebP).');
      return;
    }

    // Validate file size (max 10MB raw - will be compressed)
    if (file.size > 10 * 1024 * 1024) {
      onError?.('Image is too large. Please select an image under 10MB.');
      return;
    }

    setIsProcessing(true);

    try {
      // Compress and resize the image to keep base64 small (~30-80KB)
      const compressedBase64 = await compressImage(file, 256, 0.75);
      onImageSelect(compressedBase64);
    } catch (error) {
      console.error('Error processing image:', error);
      onError?.('Failed to process image. Please try a different file.');
    } finally {
      setIsProcessing(false);
      // Reset input so the same file can be re-selected
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="relative">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp"
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled || isProcessing}
      />
      
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
        disabled={disabled || isProcessing}
        className={cn(
          "relative w-24 h-24 rounded-full overflow-hidden",
          "border-2 border-white/[0.12] transition-all duration-200",
          "focus:outline-none focus:ring-2 focus:ring-white/20",
          !disabled && "hover:border-white/30 cursor-pointer",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        {/* Avatar Image or Initials */}
        {currentImage ? (
          <img
            src={currentImage}
            alt={name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-[#2A2A2A] to-[#1A1A1A] flex items-center justify-center">
            {name ? (
              <span className="text-2xl font-medium text-white/60">
                {getInitials(name)}
              </span>
            ) : (
              <User className="w-10 h-10 text-white/40" />
            )}
          </div>
        )}

        {/* Hover Overlay */}
        {(isHovering || isProcessing) && !disabled && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
            {isProcessing ? (
              <Loader2 className="w-6 h-6 text-white animate-spin" />
            ) : (
              <Camera className="w-6 h-6 text-white" />
            )}
          </div>
        )}
      </button>

      {/* Helper Text */}
      <p className="text-xs text-white/40 mt-2 text-center">
        Click to upload
      </p>
    </div>
  );
}
