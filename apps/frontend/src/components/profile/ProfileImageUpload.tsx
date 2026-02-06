'use client';

import { useState, useRef } from 'react';
import { cn } from '@/lib/utils';
import { Camera, User, Loader2 } from 'lucide-react';

interface ProfileImageUploadProps {
  currentImage: string | null;
  name: string;
  onImageSelect: (base64: string) => void;
  disabled?: boolean;
}

export function ProfileImageUpload({
  currentImage,
  name,
  onImageSelect,
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
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      return;
    }

    setIsProcessing(true);

    try {
      // Convert to base64
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target?.result as string;
        onImageSelect(base64);
        setIsProcessing(false);
      };
      reader.onerror = () => {
        setIsProcessing(false);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error processing image:', error);
      setIsProcessing(false);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="relative">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
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
