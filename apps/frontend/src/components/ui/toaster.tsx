'use client';

import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import { X, CheckCircle, AlertCircle } from 'lucide-react';

export function Toaster() {
  const { toasts, dismiss } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-md">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "flex items-start gap-3 p-4 rounded-lg shadow-lg border animate-in slide-in-from-right-full",
            "bg-[#1A1A1A] border-white/[0.08]",
            toast.variant === 'destructive' && "border-red-500/30 bg-red-950/50"
          )}
        >
          <div className="flex-shrink-0 mt-0.5">
            {toast.variant === 'destructive' ? (
              <AlertCircle className="h-5 w-5 text-red-400" />
            ) : (
              <CheckCircle className="h-5 w-5 text-green-400" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className={cn(
              "text-sm font-medium",
              toast.variant === 'destructive' ? "text-red-200" : "text-white"
            )}>
              {toast.title}
            </p>
            {toast.description && (
              <p className={cn(
                "text-sm mt-1",
                toast.variant === 'destructive' ? "text-red-300/70" : "text-white/60"
              )}>
                {toast.description}
              </p>
            )}
          </div>
          <button
            onClick={() => dismiss(toast.id)}
            className="flex-shrink-0 p-1 rounded hover:bg-white/10 text-white/40 hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
