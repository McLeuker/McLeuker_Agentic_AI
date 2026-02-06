'use client';

import { useState, useRef, useEffect } from 'react';
import { X, Image as ImageIcon, Loader2, Download, RefreshCw, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ImageGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImageGenerated?: (imageUrl: string) => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

// Style presets for fashion-focused image generation
const STYLE_PRESETS = [
  { id: 'fashion', label: 'Fashion Editorial', description: 'High-end fashion photography style' },
  { id: 'streetwear', label: 'Streetwear', description: 'Urban street fashion aesthetic' },
  { id: 'minimalist', label: 'Minimalist', description: 'Clean, minimal design' },
  { id: 'luxury', label: 'Luxury', description: 'Premium, sophisticated look' },
  { id: 'sustainable', label: 'Eco-Friendly', description: 'Natural, sustainable aesthetic' },
  { id: 'avant-garde', label: 'Avant-Garde', description: 'Experimental, artistic style' },
];

export function ImageGenerationModal({ isOpen, onClose, onImageGenerated }: ImageGenerationModalProps) {
  const [prompt, setPrompt] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('fashion');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const modalRef = useRef<HTMLDivElement>(null);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  const handleGenerate = async () => {
    if (!prompt.trim() || isGenerating) return;

    setIsGenerating(true);
    setError(null);
    setProgress(0);
    setGeneratedImage(null);

    // Simulate progress for UX
    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + 10, 90));
    }, 500);

    try {
      // Build enhanced prompt with style
      const stylePreset = STYLE_PRESETS.find(s => s.id === selectedStyle);
      const enhancedPrompt = `${prompt}. Style: ${stylePreset?.description || 'fashion photography'}. High quality, professional, detailed.`;

      const response = await fetch(`${API_URL}/api/image/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: enhancedPrompt,
          style: selectedStyle,
          width: 1024,
          height: 1024,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || 'Failed to generate image');
      }

      const data = await response.json();
      
      if (data.image_url) {
        setGeneratedImage(data.image_url);
        setProgress(100);
        onImageGenerated?.(data.image_url);
      } else if (data.error) {
        throw new Error(data.error);
      } else {
        throw new Error('No image returned from API');
      }
    } catch (err: any) {
      console.error('Image generation error:', err);
      setError(err.message || 'Failed to generate image. Please try again.');
    } finally {
      clearInterval(progressInterval);
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!generatedImage) return;
    
    try {
      const response = await fetch(generatedImage);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mcleuker-ai-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download error:', err);
    }
  };

  const handleReset = () => {
    setGeneratedImage(null);
    setError(null);
    setProgress(0);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div 
        ref={modalRef}
        className="bg-[#111111] border border-white/[0.08] rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#3d655c] to-[#3d665c] flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Generate Image</h2>
              <p className="text-xs text-white/50">Powered by Nano Banana AI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white/50 hover:text-white hover:bg-white/[0.05] transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {!generatedImage ? (
            <div className="space-y-6">
              {/* Prompt Input */}
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Describe your image
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="A sustainable fashion collection featuring organic cotton dresses in earth tones..."
                  className={cn(
                    "w-full h-32 px-4 py-3 rounded-xl",
                    "bg-[#0A0A0A] border border-white/[0.08]",
                    "text-white placeholder:text-white/30",
                    "focus:border-[#3d655c]/50 focus:outline-none focus:ring-1 focus:ring-[#3d655c]/20",
                    "resize-none transition-all"
                  )}
                  disabled={isGenerating}
                />
              </div>

              {/* Style Presets */}
              <div>
                <label className="block text-sm font-medium text-white/70 mb-3">
                  Style Preset
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {STYLE_PRESETS.map((style) => (
                    <button
                      key={style.id}
                      onClick={() => setSelectedStyle(style.id)}
                      disabled={isGenerating}
                      className={cn(
                        "px-4 py-3 rounded-xl text-left transition-all",
                        selectedStyle === style.id
                          ? "bg-gradient-to-r from-[#3d655c]/20 to-[#3d665c]/20 border border-[#3d655c]/50"
                          : "bg-white/[0.03] border border-white/[0.08] hover:border-white/[0.15]"
                      )}
                    >
                      <span className={cn(
                        "text-sm font-medium",
                        selectedStyle === style.id ? "text-[#6b9b8a]" : "text-white/80"
                      )}>
                        {style.label}
                      </span>
                      <p className="text-xs text-white/40 mt-0.5">{style.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}

              {/* Progress Bar */}
              {isGenerating && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/60">Generating...</span>
                    <span className="text-white/60">{progress}%</span>
                  </div>
                  <div className="h-2 bg-white/[0.05] rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-[#3d655c] to-[#3d665c] transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className={cn(
                  "w-full py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2",
                  prompt.trim() && !isGenerating
                    ? "bg-gradient-to-r from-[#3d655c] to-[#3d665c] text-white hover:from-[#1a8a62] hover:to-[#2d7a35]"
                    : "bg-white/[0.05] text-white/40 cursor-not-allowed"
                )}
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    Generate Image
                  </>
                )}
              </button>
            </div>
          ) : (
            /* Generated Image View */
            <div className="space-y-4">
              <div className="relative rounded-xl overflow-hidden bg-black/50">
                <img 
                  src={generatedImage} 
                  alt="Generated image" 
                  className="w-full h-auto"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={handleDownload}
                  className="flex-1 py-3 rounded-xl font-medium bg-gradient-to-r from-[#3d655c] to-[#3d665c] text-white hover:from-[#1a8a62] hover:to-[#2d7a35] transition-all flex items-center justify-center gap-2"
                >
                  <Download className="h-5 w-5" />
                  Download
                </button>
                <button
                  onClick={handleReset}
                  className="flex-1 py-3 rounded-xl font-medium bg-white/[0.05] text-white/80 hover:bg-white/[0.08] transition-all flex items-center justify-center gap-2"
                >
                  <RefreshCw className="h-5 w-5" />
                  Generate Another
                </button>
              </div>

              {/* Prompt Used */}
              <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08]">
                <p className="text-xs text-white/40 mb-1">Prompt used:</p>
                <p className="text-sm text-white/70">{prompt}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
