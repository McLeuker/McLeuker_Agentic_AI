"use client";

import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Sparkles, Zap, Bot, ChevronDown, Check } from "lucide-react";

export type SearchMode = "auto" | "instant" | "agent";

interface ModelOption {
  id: SearchMode;
  label: string;
  description: string;
  icon: React.ElementType;
  credits: string;
}

const MODEL_OPTIONS: ModelOption[] = [
  {
    id: "auto",
    label: "Auto",
    description: "Smart routing, deep analysis",
    icon: Sparkles,
    credits: "10cr",
  },
  {
    id: "instant",
    label: "Instant",
    description: "Fast, concise answers",
    icon: Zap,
    credits: "5cr",
  },
  {
    id: "agent",
    label: "Agent",
    description: "Multi-step reasoning & tasks",
    icon: Bot,
    credits: "25cr",
  },
];

interface InlineModelPickerProps {
  value: SearchMode;
  onChange: (mode: SearchMode) => void;
  disabled?: boolean;
  /** Compact mode for smaller input areas */
  compact?: boolean;
}

export function InlineModelPicker({
  value,
  onChange,
  disabled = false,
  compact = false,
}: InlineModelPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const selected = MODEL_OPTIONS.find((m) => m.id === value) || MODEL_OPTIONS[0];
  const SelectedIcon = selected.icon;

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsOpen(false);
    };
    if (isOpen) {
      document.addEventListener("keydown", handleEsc);
      return () => document.removeEventListener("keydown", handleEsc);
    }
  }, [isOpen]);

  return (
    <div ref={containerRef} className="relative">
      {/* Trigger button — pill shape */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          "flex items-center gap-1.5 rounded-lg transition-all select-none",
          compact ? "px-2 py-1.5" : "px-2.5 py-1.5",
          "bg-white/[0.06] hover:bg-white/[0.10] border border-white/[0.08] hover:border-white/[0.14]",
          isOpen && "bg-white/[0.10] border-white/[0.14]",
          disabled && "opacity-40 cursor-not-allowed hover:bg-white/[0.06] hover:border-white/[0.08]"
        )}
      >
        <SelectedIcon className={cn("text-white/60", compact ? "h-3 w-3" : "h-3.5 w-3.5")} />
        <span className={cn("text-white/70 font-medium", compact ? "text-[10px]" : "text-[11px]")}>
          {selected.label}
        </span>
        <span className={cn("text-white/30 font-normal", compact ? "text-[9px]" : "text-[10px]")}>
          {selected.credits}
        </span>
        <ChevronDown
          className={cn(
            "text-white/30 transition-transform duration-200",
            compact ? "h-2.5 w-2.5" : "h-3 w-3",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {/* Dropdown — opens above the trigger */}
      {isOpen && (
        <div
          className={cn(
            "absolute bottom-full left-0 mb-2 z-50",
            "w-[220px] rounded-xl overflow-hidden",
            "bg-[#1a1a1a] border border-white/[0.10]",
            "shadow-xl shadow-black/50",
            "animate-in fade-in slide-in-from-bottom-2 duration-150"
          )}
        >
          {/* Header */}
          <div className="px-3 py-2 border-b border-white/[0.06]">
            <span className="text-[10px] text-white/30 uppercase tracking-wider font-medium">
              Search Mode
            </span>
          </div>

          {/* Options */}
          <div className="py-1">
            {MODEL_OPTIONS.map((option) => {
              const Icon = option.icon;
              const isSelected = option.id === value;
              return (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => {
                    onChange(option.id);
                    setIsOpen(false);
                  }}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2.5 transition-all text-left",
                    isSelected
                      ? "bg-[#2E3524]/40"
                      : "hover:bg-white/[0.04]"
                  )}
                >
                  <div
                    className={cn(
                      "w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0",
                      isSelected
                        ? "bg-[#2E3524] text-white"
                        : "bg-white/[0.06] text-white/40"
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span
                        className={cn(
                          "text-xs font-medium",
                          isSelected ? "text-white/90" : "text-white/60"
                        )}
                      >
                        {option.label}
                      </span>
                      <span className="text-[9px] text-white/25">
                        {option.credits}
                      </span>
                    </div>
                    <div className="text-[10px] text-white/30 leading-tight">
                      {option.description}
                    </div>
                  </div>
                  {isSelected && (
                    <Check className="h-3.5 w-3.5 text-[#5a7a3a] flex-shrink-0" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
